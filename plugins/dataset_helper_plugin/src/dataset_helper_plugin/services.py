import hashlib
import logging
import os
import re
import tempfile
import urllib.request
import uuid
import json as json_module

from django.conf import settings as django_settings
from django.core.files import File
from django.db import transaction
from django.utils import timezone
from geomanager.models.core import Category, Dataset, Metadata, SubCategory
from geomanager.models.raster_file import RasterFileLayer, RasterUpload
from geomanager.models.raster_tile import RasterTileLayer
from geomanager.models.vector_file import VectorFileLayer, PgVectorTable
from geomanager.models.vector_tile import VectorTileLayer
from geomanager.models.wms import WmsLayer, WmsRequestLayer, WmsRequestParam
from geomanager.settings import geomanager_settings
from geomanager.utils.raster_utils import read_raster_info, create_layer_raster_file
from geomanager.utils.vector_utils import ogr_db_import

from .models import CatalogEntry, PluginSettings

logger = logging.getLogger(__name__)


def _resolve_i18n(value, lang='en'):
    """
    Resolve a multilingual value. If value is a dict with language keys,
    return the string for `lang` (fallback to 'en', then first available).
    If value is already a string, return it as-is.
    """
    if isinstance(value, dict):
        return value.get(lang) or value.get('en') or next(iter(value.values()), '')
    return value or ''


def _substitute_ecmwf_token(wms_url, token):
    """
    Replace the token parameter in ECMWF eccharts WMS URLs with the configured token.
    E.g. https://eccharts.ecmwf.int/wms/?token=public -> ...?token=<configured>
    """
    if 'eccharts.ecmwf.int' in wms_url and token:
        return re.sub(r'(token=)[^&]*', rf'\g<1>{token}', wms_url)
    return wms_url


def _fetch_estation_product_ids(estation_url):
    """
    Fetch the local eStation /collections endpoint and return a set of product_id values.
    Returns None if estation_url is empty (meaning: no filtering).
    """
    if not estation_url:
        return None

    collections_url = estation_url.rstrip('/') + '/collections'
    try:
        req = urllib.request.Request(collections_url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json_module.loads(resp.read().decode('utf-8'))
        products = data.get('products', [])
        return {p['product_id'] for p in products if p.get('product_id')}
    except Exception as e:
        logger.warning("Failed to fetch eStation collections from %s: %s", collections_url, e)
        return None


def _substitute_estation_url(wms_url, estation_url):
    """
    Replace global eStation WMS base URL with the local eStation URL + /webservices.
    """
    if estation_url and 'estation' in wms_url.lower():
        return estation_url.rstrip('/') + '/webservices'
    return wms_url


def load_catalog_from_config(json_data):
    """
    Parse a config JSON and populate the CatalogEntry table.
    Uses update_or_create keyed on product_code for idempotency.

    Supports two formats:
    1. Nested: {"categories": [{"title":..., "subcategories": [{"datasets": [...]}]}]}
    2. Flat products: {"products": [{"category":..., "product_id":..., "descriptive_name":..., "wms_getmap_url":...}]}

    Applies plugin settings: language resolution, ECMWF token substitution,
    and eStation local product filtering.

    Returns stats dict with created/updated/unchanged counts.
    """
    stats = {'created': 0, 'updated': 0, 'unchanged': 0, 'skipped_estation': 0, 'errors': []}

    settings = PluginSettings.load()
    lang = settings.language
    ecmwf_token = settings.ecmwf_token
    estation_product_ids = _fetch_estation_product_ids(settings.estation_url)

    estation_url = settings.estation_url

    if json_data.get('categories'):
        _load_nested_format(json_data, stats, lang, ecmwf_token, estation_product_ids, estation_url)
    elif json_data.get('products'):
        _load_products_format(json_data, stats, lang, ecmwf_token, estation_product_ids, estation_url)
    else:
        stats['errors'].append(
            'Unrecognized format: expected top-level "categories" (nested format) '
            'or "products" (flat format).'
        )

    return stats


def _load_nested_format(json_data, stats, lang='en', ecmwf_token='public', estation_product_ids=None, estation_url=''):
    """Load from the nested categories > subcategories > datasets > layers format."""

    def is_estation_layer(layer_name):
        """Check if a layer_name is an eStation product."""
        if estation_product_ids is None:
            return True  # No filtering
        return layer_name in estation_product_ids

    for cat_data in json_data.get('categories', []):
        cat_title = _resolve_i18n(cat_data.get('title', ''), lang)
        cat_icon = cat_data.get('icon', 'map')

        for subcat_data in cat_data.get('subcategories', []):
            subcat_title = _resolve_i18n(subcat_data.get('title', ''), lang)

            for dataset_data in subcat_data.get('datasets', []):
                layers_data = dataset_data.get('layers', [])
                metadata = dataset_data.get('metadata', {})

                for layer_data in layers_data:
                    layer_type = layer_data.get('type', 'wms')
                    dataset_title = _resolve_i18n(dataset_data.get('title', '?'), lang)

                    # --- Validate required fields per type ---
                    if layer_type == 'wms':
                        layer_name = layer_data.get('layer_name', '')
                        wms_url = layer_data.get('wms_url', '')
                        if not layer_name or not wms_url:
                            stats['errors'].append(
                                f"Skipping WMS layer in '{cat_title}/{subcat_title}/"
                                f"{dataset_title}': missing layer_name or wms_url"
                            )
                            continue

                        # eStation filtering
                        if estation_product_ids is not None and 'estation' in wms_url.lower():
                            if not is_estation_layer(layer_name):
                                stats['skipped_estation'] += 1
                                continue

                        wms_url = _substitute_ecmwf_token(wms_url, ecmwf_token)
                        wms_url = _substitute_estation_url(wms_url, estation_url)
                        product_code = layer_name

                    elif layer_type in ('raster_tile', 'vector_tile'):
                        tile_url = layer_data.get('tile_url', '')
                        if not tile_url:
                            stats['errors'].append(
                                f"Skipping {layer_type} layer in '{cat_title}/{subcat_title}/"
                                f"{dataset_title}': missing tile_url"
                            )
                            continue
                        product_code = f"{layer_type}_{hashlib.md5(tile_url.encode()).hexdigest()[:12]}"

                    elif layer_type in ('raster_file', 'vector_file'):
                        file_url = layer_data.get('url', '')
                        if not file_url:
                            stats['errors'].append(
                                f"Skipping {layer_type} layer in '{cat_title}/{subcat_title}/"
                                f"{dataset_title}': missing url"
                            )
                            continue
                        product_code = f"{layer_type}_{hashlib.md5(file_url.encode()).hexdigest()[:12]}"

                    else:
                        stats['errors'].append(
                            f"Skipping layer in '{cat_title}/{subcat_title}/"
                            f"{dataset_title}': unknown type '{layer_type}'"
                        )
                        continue

                    defaults = {
                        'title': _resolve_i18n(dataset_data.get('title', ''), lang) or product_code,
                        'summary': _resolve_i18n(dataset_data.get('summary', ''), lang),
                        'category_title': cat_title,
                        'category_icon': cat_icon,
                        'subcategory_title': subcat_title,
                        'layer_type': layer_type,
                        'layer_name': layer_data.get('layer_name', ''),
                        'wms_url': wms_url if layer_type == 'wms' else '',
                        'layer_title': _resolve_i18n(layer_data.get('title', ''), lang),
                        'tile_url': layer_data.get('tile_url', ''),
                        'file_url': layer_data.get('url', ''),
                        'render_layers_json': layer_data.get('render_layers') or None,
                        'extra_params_json': layer_data.get('extra_params') or None,
                        'multi_temporal': dataset_data.get('multi_temporal', True),
                        'origin': CatalogEntry.ORIGIN_CONFIG,
                        'meta_source': metadata.get('source', ''),
                        'meta_resolution': metadata.get('resolution', ''),
                        'meta_geographic_coverage': _resolve_i18n(metadata.get('geographic_coverage', ''), lang),
                        'meta_license': metadata.get('license', ''),
                        'meta_frequency_of_update': _resolve_i18n(metadata.get('frequency_of_update', ''), lang),
                        'meta_function': _resolve_i18n(metadata.get('function', ''), lang),
                        'meta_overview': _resolve_i18n(metadata.get('overview', ''), lang),
                        'meta_learn_more': metadata.get('learn_more', ''),
                    }

                    _upsert_entry(product_code, defaults, stats)


def _load_products_format(json_data, stats, lang='en', ecmwf_token='public', estation_product_ids=None, estation_url=''):
    """
    Load from the flat products format (e.g. jrc_station_products.json).
    Each product has: category, product_id, descriptive_name, wms_getmap_url, resource_url.
    """
    server_url = json_data.get('ServerURL', 'localhost')
    # Build WMS base URL from server URL
    if not server_url.startswith('http'):
        wms_base_url = f"https://{server_url}/webservices"
    else:
        wms_base_url = server_url.rstrip('/') + '/webservices'

    for product in json_data.get('products', []):
        product_id = product.get('product_id', '')
        if not product_id:
            stats['errors'].append(f"Skipping product without product_id: {product.get('descriptive_name', '?')}")
            continue

        # eStation filtering: skip products not available on the local instance
        if estation_product_ids is not None:
            if product_id not in estation_product_ids:
                stats['skipped_estation'] += 1
                continue

        category = product.get('category', 'Uncategorized')
        # Capitalize category title
        cat_title = category.capitalize()

        # Extract WMS layer name from wms_getmap_url (LAYERS= param) or use product_id
        layer_name = product_id
        wms_url_raw = product.get('wms_getmap_url', '')
        wms_url = wms_base_url
        if wms_url_raw:
            # Extract base URL (before query params)
            if '?' in wms_url_raw:
                base_part = wms_url_raw.split('?')[0]
                if not base_part.startswith('http'):
                    base_part = f"https://{base_part}"
                wms_url = base_part

            # Extract LAYERS param value if present
            import urllib.parse
            parsed = urllib.parse.urlparse(wms_url_raw if '://' in wms_url_raw else f"https://{wms_url_raw}")
            params = urllib.parse.parse_qs(parsed.query)
            if 'LAYERS' in params:
                layer_name = params['LAYERS'][0]

        # Substitute eStation URL with local instance
        wms_url = _substitute_estation_url(wms_url, estation_url)

        descriptive_name = product.get('descriptive_name', product_id)

        defaults = {
            'title': descriptive_name,
            'summary': descriptive_name,
            'category_title': cat_title,
            'category_icon': 'map',
            'subcategory_title': 'Observation',
            'layer_type': 'wms',
            'layer_name': layer_name,
            'wms_url': wms_url,
            'layer_title': descriptive_name,
            'multi_temporal': True,
            'origin': CatalogEntry.ORIGIN_CONFIG,
            'meta_source': 'JRC eStation',
            'meta_learn_more': product.get('resource_url', ''),
        }

        _upsert_entry(product_id, defaults, stats)


def _upsert_entry(product_code, defaults, stats):
    """Create or update a CatalogEntry and update stats."""
    entry, created = CatalogEntry.objects.update_or_create(
        product_code=product_code,
        defaults=defaults,
    )
    if created:
        stats['created'] += 1
    else:
        stats['updated'] += 1


def sync_catalog_to_climweb():
    """
    Synchronize CatalogEntry state to Climweb DB.

    - pending_add entries: create Climweb objects and store dataset_id
    - pending_remove entries: delete Climweb Dataset (cascades) and clear dataset_id
    - synced entries: verify Dataset still exists; clear dataset_id if orphaned

    Returns stats dict.
    """
    stats = {
        'added': 0,
        'removed': 0,
        'orphans_cleared': 0,
        'already_synced': 0,
        'errors': [],
    }

    entries = CatalogEntry.objects.all()

    with transaction.atomic():
        for entry in entries:
            status = entry.status

            if status == CatalogEntry.STATUS_SYNCED:
                if not Dataset.objects.filter(id=entry.dataset_id).exists():
                    entry.dataset_id = None
                    entry.save(update_fields=['dataset_id', 'updated_at'])
                    stats['orphans_cleared'] += 1
                else:
                    stats['already_synced'] += 1

            elif status == CatalogEntry.STATUS_PENDING_ADD:
                sid = transaction.savepoint()
                try:
                    dataset_id = _provision_entry(entry)
                    entry.dataset_id = dataset_id
                    entry.save(update_fields=['dataset_id', 'updated_at'])
                    transaction.savepoint_commit(sid)
                    stats['added'] += 1
                except Exception as e:
                    transaction.savepoint_rollback(sid)
                    stats['errors'].append(f"Failed to provision '{entry.title}': {e}")
                    logger.exception("Failed to provision catalog entry %s", entry.product_code)

            elif status == CatalogEntry.STATUS_PENDING_REMOVE:
                sid = transaction.savepoint()
                try:
                    _deprovision_entry(entry)
                    entry.dataset_id = None
                    entry.save(update_fields=['dataset_id', 'updated_at'])
                    transaction.savepoint_commit(sid)
                    stats['removed'] += 1
                except Exception as e:
                    transaction.savepoint_rollback(sid)
                    stats['errors'].append(f"Failed to deprovision '{entry.title}': {e}")
                    logger.exception("Failed to deprovision catalog entry %s", entry.product_code)

            # STATUS_DISABLED: nothing to do

    return stats


# ---------------------------------------------------------------------------
# Provisioning helpers
# ---------------------------------------------------------------------------


def _create_common_objects(entry):
    """
    Create the shared Climweb objects for any layer type:
    Category, SubCategory, Metadata, Dataset.
    Returns the new Dataset instance.
    """
    category, _ = Category.objects.get_or_create(
        title=entry.category_title,
        defaults={
            'icon': entry.category_icon,
            'active': True,
            'public': True,
        },
    )

    subcategory, _ = SubCategory.objects.get_or_create(
        title=entry.subcategory_title,
        category=category,
        defaults={
            'active': True,
            'public': True,
        },
    )

    metadata = None
    if any([
        entry.meta_source, entry.meta_resolution, entry.meta_function,
        entry.meta_overview, entry.meta_geographic_coverage,
    ]):
        metadata = Metadata.objects.create(
            title=entry.meta_source or entry.title,
            function=entry.meta_function or None,
            resolution=entry.meta_resolution or None,
            geographic_coverage=entry.meta_geographic_coverage or None,
            source=entry.meta_source or None,
            license=entry.meta_license or None,
            frequency_of_update=entry.meta_frequency_of_update or None,
            overview=entry.meta_overview or None,
            learn_more=entry.meta_learn_more or None,
        )

    dataset = Dataset.objects.create(
        title=entry.title,
        category=category,
        sub_category=subcategory,
        layer_type=entry.layer_type,
        metadata=metadata,
        published=True,
        public=True,
        multi_temporal=entry.multi_temporal,
        multi_layer=False,
        near_realtime=False,
        can_clip=False,
        initial_visible=False,
    )

    if entry.summary:
        dataset.summary = entry.summary
        dataset.save(update_fields=['summary'])

    return dataset


def _provision_entry(entry):
    """
    Create Climweb objects for a single CatalogEntry.
    Dispatches to a type-specific provisioner.
    Returns the new Dataset UUID.
    """
    dataset = _create_common_objects(entry)
    provisioner = _PROVISIONERS.get(entry.layer_type)
    if provisioner is None:
        raise ValueError(f"Unsupported layer type: {entry.layer_type}")
    provisioner(entry, dataset)
    return dataset.id


def _provision_wms(entry, dataset):
    """Create WmsLayer + WmsRequestLayer for a WMS catalog entry."""
    wms_layer = WmsLayer.objects.create(
        dataset=dataset,
        title=entry.layer_title or entry.title,
        base_url=entry.wms_url,
        version='1.3.0',
        width=256,
        height=256,
        transparent=True,
        srs='EPSG:3857',
        format='image/png',
        default=True,
        request_time_from_capabilities=True,
        legend_from_capabilities=True,
    )

    WmsRequestLayer.objects.create(
        layer=wms_layer,
        name=entry.layer_name,
    )

    # Add extra WMS query params if present
    if entry.extra_params_json and isinstance(entry.extra_params_json, dict):
        for param_name, param_value in entry.extra_params_json.items():
            WmsRequestParam.objects.create(
                layer=wms_layer,
                name=param_name,
                value=str(param_value),
            )


def _provision_raster_tile(entry, dataset):
    """Create a RasterTileLayer for an XYZ raster tile catalog entry."""
    RasterTileLayer.objects.create(
        dataset=dataset,
        title=entry.layer_title or entry.title,
        base_url=entry.tile_url,
        default=True,
    )


def _provision_vector_tile(entry, dataset):
    """Create a VectorTileLayer for an MVT vector tile catalog entry."""
    VectorTileLayer.objects.create(
        dataset=dataset,
        title=entry.layer_title or entry.title,
        base_url=entry.tile_url,
        default=True,
        use_render_layers_json=bool(entry.render_layers_json),
        render_layers_json=entry.render_layers_json,
    )


def _provision_raster_file(entry, dataset):
    """Download a remote GeoTIFF and ingest it as a RasterFileLayer."""
    url = _resolve_file_url(entry.file_url)

    layer = RasterFileLayer.objects.create(
        dataset=dataset,
        title=entry.layer_title or entry.title,
        default=True,
    )

    _download_and_ingest_raster(layer, dataset, url)


def _provision_vector_file(entry, dataset):
    """Download a remote GeoJSON and import it as a VectorFileLayer."""
    url = _resolve_file_url(entry.file_url)

    layer = VectorFileLayer.objects.create(
        dataset=dataset,
        title=entry.layer_title or entry.title,
        default=True,
    )

    _download_and_ingest_vector(layer, url)


_PROVISIONERS = {
    'wms': _provision_wms,
    'raster_tile': _provision_raster_tile,
    'vector_tile': _provision_vector_tile,
    'raster_file': _provision_raster_file,
    'vector_file': _provision_vector_file,
}


# ---------------------------------------------------------------------------
# URL placeholder substitution
# ---------------------------------------------------------------------------


def _resolve_file_url(url_template):
    """
    Replace placeholders in a file URL with values from PluginSettings.
    Supported: {country_alpha3}, {COUNTRY_ALPHA3}
    """
    settings = PluginSettings.load()
    url = url_template
    if settings.country_alpha3:
        url = url.replace('{country_alpha3}', settings.country_alpha3.lower())
        url = url.replace('{COUNTRY_ALPHA3}', settings.country_alpha3.upper())
    return url


# ---------------------------------------------------------------------------
# File download and ingest helpers
# ---------------------------------------------------------------------------


def _download_file(url, suffix='.tif'):
    """
    Download a URL to a temporary file.
    Returns the temp file path. Caller is responsible for cleanup.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.close()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ClimwebDatasetHelper/1.0'})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(tmp.name, 'wb') as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        return tmp.name
    except Exception:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        raise


def _download_and_ingest_raster(layer, dataset, url):
    """Download a GeoTIFF from URL and create a LayerRasterFile."""
    file_path = _download_file(url, suffix='.tif')
    try:
        with open(file_path, 'rb') as f:
            upload = RasterUpload.objects.create(
                dataset=dataset,
                file=File(f, name=os.path.basename(file_path)),
            )

        raster_meta = read_raster_info(upload.file.path)
        upload.raster_metadata = raster_meta
        upload.save(update_fields=['raster_metadata'])

        time = timezone.now()
        create_layer_raster_file(layer, upload, time)
        upload.delete()
    finally:
        if os.path.exists(file_path):
            os.unlink(file_path)


def _download_and_ingest_vector(layer, url):
    """Download a GeoJSON from URL and import it into PostgreSQL."""
    file_path = _download_file(url, suffix='.geojson')
    try:
        default_db = django_settings.DATABASES['default']
        db_params = {
            'host': default_db.get('HOST'),
            'port': default_db.get('PORT'),
            'user': default_db.get('USER'),
            'password': default_db.get('PASSWORD'),
            'name': default_db.get('NAME'),
            'pg_service_schema': geomanager_settings.get('vector_db_schema'),
        }

        table_name = f"vector_{uuid.uuid4().hex[:12]}"
        table_info = ogr_db_import(file_path, table_name, db_params)

        PgVectorTable.objects.create(
            layer=layer,
            table_name=table_name,
            full_table_name=table_info.get('table_name', table_name),
            time=timezone.now(),
            properties=table_info.get('properties', []),
            geometry_type=table_info.get('geom_type', 'UNKNOWN'),
            bounds=table_info.get('bounds', []),
        )
    finally:
        if os.path.exists(file_path):
            os.unlink(file_path)


# ---------------------------------------------------------------------------
# Deprovision
# ---------------------------------------------------------------------------


def _deprovision_entry(entry):
    """
    Delete the Climweb Dataset associated with a CatalogEntry.
    Cascading deletes handle all layer types (WmsLayer, RasterTileLayer,
    VectorTileLayer, RasterFileLayer, VectorFileLayer and their children).
    """
    if entry.dataset_id:
        Dataset.objects.filter(id=entry.dataset_id).delete()


def add_entry(data, origin=CatalogEntry.ORIGIN_MANUAL):
    """
    Add a new CatalogEntry from manual input or WMS import.
    """
    layer_type = data.get('layer_type', 'wms')
    layer_name = data.get('layer_name', '')
    wms_url = data.get('wms_url', '')
    tile_url = data.get('tile_url', '')
    file_url = data.get('file_url', '')

    # Derive a unique identifier for product_code generation
    if layer_type == 'wms':
        identifier, url = layer_name, wms_url
    elif layer_type in ('raster_tile', 'vector_tile'):
        identifier, url = tile_url, tile_url
    else:
        identifier, url = file_url, file_url

    product_code = data.get('product_code')
    if not product_code:
        product_code = CatalogEntry.generate_product_code(identifier, url, origin, layer_type)

    entry = CatalogEntry.objects.create(
        product_code=product_code,
        title=data.get('title', identifier or 'Untitled'),
        summary=data.get('summary', ''),
        category_title=data['category_title'],
        category_icon=data.get('category_icon', 'map'),
        subcategory_title=data['subcategory_title'],
        layer_type=layer_type,
        layer_name=layer_name,
        wms_url=wms_url,
        layer_title=data.get('layer_title', ''),
        tile_url=tile_url,
        file_url=file_url,
        render_layers_json=data.get('render_layers_json'),
        extra_params_json=data.get('extra_params_json'),
        multi_temporal=data.get('multi_temporal', True),
        origin=origin,
        enabled=True,
        meta_source=data.get('meta_source', ''),
        meta_resolution=data.get('meta_resolution', ''),
        meta_geographic_coverage=data.get('meta_geographic_coverage', ''),
        meta_license=data.get('meta_license', ''),
        meta_frequency_of_update=data.get('meta_frequency_of_update', ''),
        meta_function=data.get('meta_function', ''),
        meta_overview=data.get('meta_overview', ''),
        meta_learn_more=data.get('meta_learn_more', ''),
    )
    return entry


def get_catalog_tree():
    """
    Return the full catalog as a nested dict for the tree UI.
    Structure: categories > subcategories > entries
    """
    entries = CatalogEntry.objects.all()
    tree = {}

    for entry in entries:
        cat = entry.category_title
        subcat = entry.subcategory_title

        if cat not in tree:
            tree[cat] = {
                'title': cat,
                'icon': entry.category_icon,
                'subcategories': {},
            }

        subcats = tree[cat]['subcategories']
        if subcat not in subcats:
            subcats[subcat] = {
                'title': subcat,
                'entries': [],
            }

        subcats[subcat]['entries'].append({
            'id': str(entry.id),
            'product_code': entry.product_code,
            'title': entry.title,
            'summary': entry.summary,
            'layer_type': entry.layer_type,
            'layer_name': entry.layer_name,
            'layer_title': entry.layer_title,
            'wms_url': entry.wms_url,
            'tile_url': entry.tile_url,
            'file_url': entry.file_url,
            'render_layers_json': entry.render_layers_json,
            'extra_params_json': entry.extra_params_json,
            'multi_temporal': entry.multi_temporal,
            'enabled': entry.enabled,
            'status': entry.status,
            'origin': entry.origin,
            'meta_source': entry.meta_source,
            'meta_resolution': entry.meta_resolution,
            'meta_geographic_coverage': entry.meta_geographic_coverage,
            'meta_license': entry.meta_license,
            'meta_frequency_of_update': entry.meta_frequency_of_update,
            'meta_function': entry.meta_function,
            'meta_overview': entry.meta_overview,
            'meta_learn_more': entry.meta_learn_more,
        })

    # Convert to sorted list format
    result = []
    for cat_key in sorted(tree.keys()):
        cat = tree[cat_key]
        subcats_list = []
        for subcat_key in sorted(cat['subcategories'].keys()):
            subcat = cat['subcategories'][subcat_key]
            subcats_list.append(subcat)
        result.append({
            'title': cat['title'],
            'icon': cat['icon'],
            'subcategories': subcats_list,
        })

    return result
