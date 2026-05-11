import hashlib
import json as json_module
import logging
import re
import urllib.request
import uuid

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from geomanager.models.core import Category, Dataset, Metadata, SubCategory
from geomanager.models.raster_style import ColorValue, RasterStyle
from geomanager.models.raster_tile import RasterTileLayer
from geomanager.models.vector_tile import VectorTileLayer
from geomanager.models.wms import WmsLayer, WmsRequestLayer, WmsRequestParam

# raster_cog is on a separate geomanager branch — make the import optional so
# the plugin still loads on branches without it. _provision_raster_cog raises
# at sync time if the layer type is used while the model is missing.
try:
    from geomanager.models.raster_cog import RasterCOGLayer
except ImportError:
    RasterCOGLayer = None

from .models import CatalogEntry, CatalogState, PluginSettings
from .provisioners import PROVISIONERS as _PACKAGED_PROVISIONERS
from .provisioners._shared import (
    DEFAULT_RASTER_PALETTE,
    add_legend_kwargs,
    download_file,
    resolve_file_url,
    resolve_i18n,
)

logger = logging.getLogger(__name__)


ECMWF_TOKEN_PLACEHOLDER = '{ECMWF_TOKEN}'

# Highest catalog schema_version this code knows how to parse.
SUPPORTED_CATALOG_SCHEMA_VERSION = 1


def _parse_iso_dt(value):
    """Parse an ISO-8601 datetime string (supports trailing Z). Returns None on failure."""
    if not value:
        return None
    if isinstance(value, str) and value.endswith('Z'):
        value = value[:-1] + '+00:00'
    return parse_datetime(value) if isinstance(value, str) else None


def _apply_ecmwf_token(wms_url, token):
    """
    Apply the configured ECMWF token to an eccharts WMS URL.

    Rules (only for URLs containing 'eccharts.ecmwf.int'):
      - token=public in URL:
          * token configured -> replace 'public' with the token
          * no token         -> leave URL unchanged
      - token={ECMWF_TOKEN} placeholder in URL:
          * token configured -> replace placeholder with the token; mark as non-public
          * no token         -> skip (cannot sync a private layer without a token)

    Returns (new_url, public, skip).
    Non-ECMWF URLs are returned unchanged with public=True, skip=False.
    """
    if 'eccharts.ecmwf.int' not in wms_url:
        return wms_url, True, False

    has_token = bool(token)

    if ECMWF_TOKEN_PLACEHOLDER in wms_url:
        if has_token:
            return wms_url.replace(ECMWF_TOKEN_PLACEHOLDER, token), False, False
        return wms_url, False, True

    if 'token=public' in wms_url:
        if has_token:
            return re.sub(r'(token=)[^&]*', rf'\g<1>{token}', wms_url), True, False
        return wms_url, True, False

    return wms_url, True, False


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
    stats = {
        'created': 0,
        'updated': 0,
        'unchanged': 0,
        'skipped_estation': 0,
        'skipped_ecmwf_no_token': 0,
        'errors': [],
    }

    version = (json_data.get('version') or '').strip()
    schema_version = json_data.get('schema_version')
    if schema_version is not None and schema_version > SUPPORTED_CATALOG_SCHEMA_VERSION:
        stats['errors'].append(
            f"Unsupported catalog schema_version={schema_version}. "
            f"This plugin supports up to schema_version={SUPPORTED_CATALOG_SCHEMA_VERSION}."
        )
        return stats

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

    if stats['created'] + stats['updated'] + stats['unchanged'] > 0:
        state = CatalogState.load()
        state.loaded_version = version
        state.loaded_schema_version = schema_version or 0
        state.loaded_at = timezone.now()
        state.save()

    return stats


def _load_nested_format(json_data, stats, lang='en', ecmwf_token='', estation_product_ids=None, estation_url=''):
    """Load from the nested categories > subcategories > datasets > layers format."""

    def is_estation_layer(layer_name):
        """Check if a layer_name is an eStation product."""
        if estation_product_ids is None:
            return True  # No filtering
        return layer_name in estation_product_ids

    entry_counter = 0

    for cat_idx, cat_data in enumerate(json_data.get('categories', [])):
        cat_title = resolve_i18n(cat_data.get('title', ''), lang)
        cat_icon = cat_data.get('icon', 'map')

        for subcat_idx, subcat_data in enumerate(cat_data.get('subcategories', [])):
            subcat_title = resolve_i18n(subcat_data.get('title', ''), lang)

            for dataset_data in subcat_data.get('datasets', []):
                layers_data = dataset_data.get('layers', [])
                metadata = dataset_data.get('metadata', {})

                for layer_data in layers_data:
                    layer_type = layer_data.get('type', 'wms')
                    dataset_title = resolve_i18n(dataset_data.get('title', '?'), lang)

                    public = True

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

                        wms_url, public, skip = _apply_ecmwf_token(wms_url, ecmwf_token)
                        if skip:
                            stats['skipped_ecmwf_no_token'] += 1
                            continue

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

                    elif layer_type == 'raster_cog':
                        cog_url = layer_data.get('url_template', '')
                        time_start_raw = layer_data.get('time_start', '')
                        time_end_raw = layer_data.get('time_end', '')
                        if not cog_url or not time_start_raw or not time_end_raw:
                            stats['errors'].append(
                                f"Skipping raster_cog layer in '{cat_title}/{subcat_title}/"
                                f"{dataset_title}': missing url_template, time_start or time_end"
                            )
                            continue
                        product_code = f"raster_cog_{hashlib.md5(cog_url.encode()).hexdigest()[:12]}"

                    else:
                        stats['errors'].append(
                            f"Skipping layer in '{cat_title}/{subcat_title}/"
                            f"{dataset_title}': unknown type '{layer_type}'"
                        )
                        continue

                    defaults = {
                        'title': resolve_i18n(dataset_data.get('title', ''), lang) or product_code,
                        'summary': resolve_i18n(dataset_data.get('summary', ''), lang),
                        'category_title': cat_title,
                        'category_icon': cat_icon,
                        'subcategory_title': subcat_title,
                        'category_order': cat_idx,
                        'subcategory_order': subcat_idx,
                        'entry_order': entry_counter,
                        'layer_type': layer_type,
                        'layer_name': layer_data.get('layer_name', ''),
                        'wms_url': wms_url if layer_type == 'wms' else '',
                        'public': public,
                        'layer_title': resolve_i18n(layer_data.get('title', ''), lang),
                        'tile_url': layer_data.get('tile_url', ''),
                        'is_pmtiles': bool(layer_data.get('is_pmtiles', False)),
                        'file_url': layer_data.get('url', ''),
                        'file_bearer': (layer_data.get('bearer') or '').strip(),
                        'cog_url_template': layer_data.get('url_template', '') if layer_type == 'raster_cog' else '',
                        'cog_time_start': _parse_iso_dt(layer_data.get('time_start')) if layer_type == 'raster_cog' else None,
                        'cog_time_end': _parse_iso_dt(layer_data.get('time_end')) if layer_type == 'raster_cog' else None,
                        'cog_time_step_value': int(layer_data.get('time_step_value', 1)) if layer_type == 'raster_cog' else 1,
                        'cog_time_step_unit': layer_data.get('time_step_unit', 'years') if layer_type == 'raster_cog' else 'years',
                        'cog_date_format': layer_data.get('date_format', '') if layer_type == 'raster_cog' else '',
                        'raster_style_json': layer_data.get('raster_style') or None,
                        'render_layers_json': layer_data.get('render_layers') or None,
                        'popup_config_json': layer_data.get('popup_config') or None,
                        'extra_params_json': layer_data.get('extra_params') or None,
                        'legend_json': layer_data.get('legend') or None,
                        'multi_temporal': dataset_data.get('multi_temporal', True),
                        'near_realtime': dataset_data.get('near_realtime', False),
                        'origin': CatalogEntry.ORIGIN_CONFIG,
                        'meta_source': metadata.get('source', ''),
                        'meta_resolution': metadata.get('resolution', ''),
                        'meta_geographic_coverage': resolve_i18n(metadata.get('geographic_coverage', ''), lang),
                        'meta_license': metadata.get('license', ''),
                        'meta_frequency_of_update': resolve_i18n(metadata.get('frequency_of_update', ''), lang),
                        'meta_function': resolve_i18n(metadata.get('function', ''), lang),
                        'meta_overview': resolve_i18n(metadata.get('overview', ''), lang),
                        'meta_learn_more': metadata.get('learn_more', ''),
                    }
                    entry_counter += 1

                    _upsert_entry(product_code, defaults, stats)


def _load_products_format(json_data, stats, lang='en', ecmwf_token='', estation_product_ids=None, estation_url=''):
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

    cat_order_map = {}
    entry_counter = 0

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

        if cat_title not in cat_order_map:
            cat_order_map[cat_title] = len(cat_order_map)

        defaults = {
            'title': descriptive_name,
            'summary': descriptive_name,
            'category_title': cat_title,
            'category_icon': 'map',
            'subcategory_title': 'Observation',
            'category_order': cat_order_map[cat_title],
            'subcategory_order': 0,
            'entry_order': entry_counter,
            'layer_type': 'wms',
            'layer_name': layer_name,
            'wms_url': wms_url,
            'layer_title': descriptive_name,
            'multi_temporal': True,
            'origin': CatalogEntry.ORIGIN_CONFIG,
            'meta_source': 'JRC eStation',
            'meta_learn_more': product.get('resource_url', ''),
        }
        entry_counter += 1

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
        'public_updated': 0,
        'errors': [],
    }

    entries = CatalogEntry.objects.all()

    for entry in entries:
        status = entry.status

        if status == CatalogEntry.STATUS_SYNCED:
            try:
                with transaction.atomic():
                    dataset = Dataset.objects.filter(id=entry.dataset_id).first()
                    if dataset is None:
                        entry.dataset_id = None
                        entry.save(update_fields=['dataset_id', 'updated_at'])
                        stats['orphans_cleared'] += 1
                    else:
                        if dataset.public != entry.public:
                            dataset.public = entry.public
                            dataset.save(update_fields=['public'])
                            stats['public_updated'] += 1
                        stats['already_synced'] += 1
            except Exception as e:
                stats['errors'].append(f"Failed to reconcile '{entry.title}': {e}")
                logger.exception("Failed to reconcile catalog entry %s", entry.product_code)

        elif status == CatalogEntry.STATUS_PENDING_ADD:
            try:
                with transaction.atomic():
                    dataset_id = _provision_entry(entry)
                    entry.dataset_id = dataset_id
                    entry.save(update_fields=['dataset_id', 'updated_at'])
                stats['added'] += 1
            except Exception as e:
                stats['errors'].append(f"Failed to provision '{entry.title}': {e}")
                logger.exception("Failed to provision catalog entry %s", entry.product_code)

        elif status == CatalogEntry.STATUS_PENDING_REMOVE:
            try:
                with transaction.atomic():
                    _deprovision_entry(entry)
                    entry.dataset_id = None
                    entry.save(update_fields=['dataset_id', 'updated_at'])
                stats['removed'] += 1
            except Exception as e:
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
    # Persist the JSON-driven position into Category.order (wagtail-adminsortable).
    # We update on every sync so admins re-loading the catalog get the order
    # reflected, but we don't touch icon/active/public to preserve manual edits.
    if category.order != entry.category_order:
        category.order = entry.category_order
        category.save(update_fields=['order'])

    subcategory, _ = SubCategory.objects.get_or_create(
        title=entry.subcategory_title,
        category=category,
        defaults={
            'active': True,
            'public': True,
        },
    )
    # SubCategory uses Orderable's ``sort_order`` (not AdminSortable's ``order``).
    if subcategory.sort_order != entry.subcategory_order:
        subcategory.sort_order = entry.subcategory_order
        subcategory.save(update_fields=['sort_order'])

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

    # raster_file datasets require a time dimension on every LayerRasterFile,
    # so the parent Dataset must always be multi_temporal.
    multi_temporal = True if entry.layer_type == CatalogEntry.LAYER_TYPE_RASTER_FILE else entry.multi_temporal

    dataset = Dataset.objects.create(
        title=entry.title,
        category=category,
        sub_category=subcategory,
        layer_type=entry.layer_type,
        metadata=metadata,
        published=True,
        public=entry.public,
        multi_temporal=multi_temporal,
        multi_layer=False,
        near_realtime=entry.near_realtime,
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
    kwargs = dict(
        dataset=dataset,
        title=entry.layer_title or entry.title,
        base_url=entry.tile_url,
        default=True,
    )

    if entry.legend_json:
        add_legend_kwargs(kwargs, entry.legend_json, RasterTileLayer,
                            lang=PluginSettings.load().language)

    RasterTileLayer.objects.create(**kwargs)


def _provision_vector_tile(entry, dataset):
    """Create a VectorTileLayer for an MVT vector tile catalog entry."""
    lang = PluginSettings.load().language
    kwargs = dict(
        dataset=dataset,
        title=entry.layer_title or entry.title,
        base_url=entry.tile_url,
        default=True,
        is_pmtiles=entry.is_pmtiles,
        use_render_layers_json=bool(entry.render_layers_json),
        render_layers_json=entry.render_layers_json,
    )

    popup_stream = _build_popup_stream_value(entry.popup_config_json, lang=lang)
    if popup_stream:
        kwargs['popup_config'] = popup_stream

    if entry.legend_json:
        add_legend_kwargs(kwargs, entry.legend_json, VectorTileLayer, lang=lang)

    VectorTileLayer.objects.create(**kwargs)


def _provision_raster_cog(entry, dataset):
    """Create a RasterCOGLayer + RasterStyle from catalog entry config."""
    if RasterCOGLayer is None:
        raise RuntimeError(
            "raster_cog layer type requires geomanager with the raster_cog model "
            "(branch 'cog'). Current geomanager build does not expose it."
        )
    style = _create_raster_style_from_config(
        entry.raster_style_json or {},
        name=entry.layer_title or entry.title,
        lang=PluginSettings.load().language,
    )
    RasterCOGLayer.objects.create(
        dataset=dataset,
        title=entry.layer_title or entry.title,
        default=True,
        url_template=entry.cog_url_template,
        time_start=entry.cog_time_start,
        time_end=entry.cog_time_end,
        time_step_value=entry.cog_time_step_value,
        time_step_unit=entry.cog_time_step_unit,
        date_format=entry.cog_date_format or None,
        style=style,
    )


_PROVISIONERS = {
    'wms': _provision_wms,
    'raster_tile': _provision_raster_tile,
    'vector_tile': _provision_vector_tile,
    'raster_cog': _provision_raster_cog,
    **_PACKAGED_PROVISIONERS,  # adds 'raster_file' (provisioners/raster_file.py)
}


_VALID_RASTER_LEGEND_TYPES = (
    'basic', 'choropleth', 'choropleth_vertical', 'gradient', 'gradient_vertical',
)


_HEX_RE = re.compile(r'^#[0-9a-fA-F]+$')


def _normalize_hex_color(value, default='#ff0000'):
    """
    Normalize a hex color string to 6-digit ``#RRGGBB``.

    Accepts ``#RGB``, ``#RRGGBB``, ``#RRGGBBAA`` (alpha stripped with a warning).
    Returns ``default`` if the value is empty/invalid.
    """
    if not value or not isinstance(value, str):
        return default
    if not _HEX_RE.match(value):
        logger.warning("Invalid hex color %r — using %s", value, default)
        return default
    body = value[1:]
    if len(body) == 3:
        return '#' + ''.join(c * 2 for c in body)
    if len(body) == 6:
        return value
    if len(body) == 8:
        logger.info("Stripping alpha channel from color %s → #%s", value, body[:6])
        return '#' + body[:6]
    logger.warning("Unexpected hex length for %r — using %s", value, default)
    return default


def _create_raster_style_from_config(config, name='', lang='en'):
    """
    Create a RasterStyle from an explicit JSON config dict.

    Recognized keys (all optional; defaults applied):
      name, unit, min, max, steps, palette, interpolate, legend_type,
      use_custom_colors, custom_colors, custom_color_for_rest.

    When ``use_custom_colors`` is true (or ``custom_colors`` is non-empty),
    a ColorValue is created for each entry in ``custom_colors``
    (keys: threshold, color, label?, show_on_legend?). ``label`` may be
    a multilingual dict ({en, fr, ...}) — resolved via the configured ``lang``.
    ``custom_color_for_rest`` is the fallback color for values outside
    the defined thresholds.
    """
    cfg = config or {}
    legend_type = cfg.get('legend_type', 'choropleth_vertical')
    if legend_type not in _VALID_RASTER_LEGEND_TYPES:
        legend_type = 'choropleth_vertical'

    custom_colors = cfg.get('custom_colors') or []
    use_custom_colors = bool(cfg.get('use_custom_colors') or custom_colors)

    style = RasterStyle.objects.create(
        name=(cfg.get('name') or name or 'raster')[:256],
        unit=resolve_i18n(cfg.get('unit'), lang) or '',
        min=int(cfg.get('min', 0)),
        max=int(cfg.get('max', 100)),
        steps=int(cfg.get('steps', 9)),
        palette=cfg.get('palette') or DEFAULT_RASTER_PALETTE,
        interpolate=bool(cfg.get('interpolate', False)),
        legend_type=legend_type,
        use_custom_colors=use_custom_colors,
        custom_color_for_rest=_normalize_hex_color(cfg.get('custom_color_for_rest'), default='#ff0000'),
    )

    for item in custom_colors:
        ColorValue.objects.create(
            layer=style,
            threshold=float(item['threshold']),
            color=_normalize_hex_color(item.get('color'), default='#000000'),
            show_on_legend=bool(item.get('show_on_legend', True)),
            label=resolve_i18n(item.get('label'), lang) or None,
        )

    return style


def _build_popup_stream_value(popup_config, lang='en'):
    """
    Build a StreamField value for ``VectorTileLayer.popup_config`` from the
    catalog's ``popup_config_json`` list.

    Each input item: ``{"data_key", "label", "data_type"}``.
    ``label`` may be an i18n dict; it's resolved with ``resolve_i18n``.
    """
    if not popup_config or not isinstance(popup_config, list):
        return None

    blocks = []
    for item in popup_config:
        data_key = (item.get('data_key') or '').strip()
        if not data_key:
            continue
        label = resolve_i18n(item.get('label'), lang) or data_key
        data_type = item.get('data_type') or 'string'
        if data_type not in ('string', 'number'):
            data_type = 'string'
        blocks.append({
            'type': 'popup_fields',
            'id': str(uuid.uuid4()),
            'value': {
                'data_key': data_key,
                'label': label,
                'data_type': data_type,
            },
        })
    return blocks or None


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

    # Place manual/imported entries at the end of their category/subcategory
    from django.db.models import Max
    max_orders = CatalogEntry.objects.aggregate(
        max_cat=Max('category_order'),
        max_entry=Max('entry_order'),
    )
    cat_order = max_orders['max_cat'] or 0
    # Check if this category already exists to reuse its order
    existing_cat = CatalogEntry.objects.filter(
        category_title=data['category_title']
    ).values('category_order', 'subcategory_order').first()
    if existing_cat:
        cat_order = existing_cat['category_order']
        # Get max subcategory_order within that category
        existing_subcat = CatalogEntry.objects.filter(
            category_title=data['category_title'],
            subcategory_title=data['subcategory_title'],
        ).values('subcategory_order').first()
        if existing_subcat:
            subcat_order = existing_subcat['subcategory_order']
        else:
            max_subcat = CatalogEntry.objects.filter(
                category_title=data['category_title']
            ).aggregate(m=Max('subcategory_order'))['m'] or 0
            subcat_order = max_subcat + 1
    else:
        cat_order = (max_orders['max_cat'] or 0) + 1
        subcat_order = 0
    entry_order = (max_orders['max_entry'] or 0) + 1

    entry = CatalogEntry.objects.create(
        product_code=product_code,
        title=data.get('title', identifier or 'Untitled'),
        summary=data.get('summary', ''),
        category_title=data['category_title'],
        category_icon=data.get('category_icon', 'map'),
        subcategory_title=data['subcategory_title'],
        category_order=cat_order,
        subcategory_order=subcat_order,
        entry_order=entry_order,
        layer_type=layer_type,
        layer_name=layer_name,
        wms_url=wms_url,
        layer_title=data.get('layer_title', ''),
        tile_url=tile_url,
        is_pmtiles=bool(data.get('is_pmtiles', False)),
        file_url=file_url,
        render_layers_json=data.get('render_layers_json'),
        popup_config_json=data.get('popup_config_json'),
        extra_params_json=data.get('extra_params_json'),
        legend_json=data.get('legend_json'),
        multi_temporal=data.get('multi_temporal', True),
        near_realtime=data.get('near_realtime', False),
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
            'is_pmtiles': entry.is_pmtiles,
            'file_url': entry.file_url,
            'render_layers_json': entry.render_layers_json,
            'popup_config_json': entry.popup_config_json,
            'extra_params_json': entry.extra_params_json,
            'legend_json': entry.legend_json,
            'multi_temporal': entry.multi_temporal,
            'near_realtime': entry.near_realtime,
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

    # Convert to list, preserving insertion order (driven by DB ordering)
    result = []
    for cat in tree.values():
        subcats_list = list(cat['subcategories'].values())
        result.append({
            'title': cat['title'],
            'icon': cat['icon'],
            'subcategories': subcats_list,
        })

    return result
