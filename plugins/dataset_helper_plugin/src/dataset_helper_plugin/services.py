import logging

from django.db import transaction
from geomanager.models.core import Category, Dataset, Metadata, SubCategory
from geomanager.models.wms import WmsLayer, WmsRequestLayer

from .models import CatalogEntry

logger = logging.getLogger(__name__)


def load_catalog_from_config(json_data):
    """
    Parse a config JSON and populate the CatalogEntry table.
    Uses update_or_create keyed on product_code for idempotency.

    Supports two formats:
    1. Nested: {"categories": [{"title":..., "subcategories": [{"datasets": [...]}]}]}
    2. Flat products: {"products": [{"category":..., "product_id":..., "descriptive_name":..., "wms_getmap_url":...}]}

    Returns stats dict with created/updated/unchanged counts.
    """
    stats = {'created': 0, 'updated': 0, 'unchanged': 0, 'errors': []}

    if json_data.get('categories'):
        _load_nested_format(json_data, stats)
    elif json_data.get('products'):
        _load_products_format(json_data, stats)
    else:
        stats['errors'].append(
            'Unrecognized format: expected top-level "categories" (nested format) '
            'or "products" (flat format).'
        )

    return stats


def _load_nested_format(json_data, stats):
    """Load from the nested categories > subcategories > datasets > layers format."""
    for cat_data in json_data.get('categories', []):
        cat_title = cat_data.get('title', '')
        cat_icon = cat_data.get('icon', 'map')

        for subcat_data in cat_data.get('subcategories', []):
            subcat_title = subcat_data.get('title', '')

            for dataset_data in subcat_data.get('datasets', []):
                layers_data = dataset_data.get('layers', [])
                metadata = dataset_data.get('metadata', {})

                for layer_data in layers_data:
                    layer_name = layer_data.get('layer_name', '')
                    wms_url = layer_data.get('wms_url', '')

                    if not layer_name or not wms_url:
                        stats['errors'].append(
                            f"Skipping layer in '{cat_title}/{subcat_title}/"
                            f"{dataset_data.get('title', '?')}': missing layer_name or wms_url"
                        )
                        continue

                    product_code = layer_name

                    defaults = {
                        'title': dataset_data.get('title', layer_name),
                        'description': dataset_data.get('description', ''),
                        'category_title': cat_title,
                        'category_icon': cat_icon,
                        'subcategory_title': subcat_title,
                        'layer_name': layer_name,
                        'wms_url': wms_url,
                        'layer_title': layer_data.get('title', ''),
                        'multi_temporal': dataset_data.get('multi_temporal', True),
                        'origin': CatalogEntry.ORIGIN_CONFIG,
                        'meta_source': metadata.get('source', ''),
                        'meta_resolution': metadata.get('resolution', ''),
                        'meta_geographic_coverage': metadata.get('geographic_coverage', ''),
                        'meta_license': metadata.get('license', ''),
                        'meta_frequency_of_update': metadata.get('frequency_of_update', ''),
                        'meta_function': metadata.get('function', ''),
                        'meta_overview': metadata.get('overview', ''),
                        'meta_learn_more': metadata.get('learn_more', ''),
                    }

                    _upsert_entry(product_code, defaults, stats)


def _load_products_format(json_data, stats):
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

        descriptive_name = product.get('descriptive_name', product_id)

        defaults = {
            'title': descriptive_name,
            'description': descriptive_name,
            'category_title': cat_title,
            'category_icon': 'map',
            'subcategory_title': 'Observation',
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
                # Verify the Dataset still exists in Climweb
                if not Dataset.objects.filter(id=entry.dataset_id).exists():
                    entry.dataset_id = None
                    entry.save(update_fields=['dataset_id', 'updated_at'])
                    stats['orphans_cleared'] += 1
                else:
                    stats['already_synced'] += 1

            elif status == CatalogEntry.STATUS_PENDING_ADD:
                try:
                    dataset_id = _provision_entry(entry)
                    entry.dataset_id = dataset_id
                    entry.save(update_fields=['dataset_id', 'updated_at'])
                    stats['added'] += 1
                except Exception as e:
                    stats['errors'].append(f"Failed to provision '{entry.title}': {e}")
                    logger.exception("Failed to provision catalog entry %s", entry.product_code)

            elif status == CatalogEntry.STATUS_PENDING_REMOVE:
                try:
                    _deprovision_entry(entry)
                    entry.dataset_id = None
                    entry.save(update_fields=['dataset_id', 'updated_at'])
                    stats['removed'] += 1
                except Exception as e:
                    stats['errors'].append(f"Failed to deprovision '{entry.title}': {e}")
                    logger.exception("Failed to deprovision catalog entry %s", entry.product_code)

            # STATUS_DISABLED: nothing to do

    return stats


def _provision_entry(entry):
    """
    Create Climweb objects (Category, SubCategory, Metadata, Dataset,
    WmsLayer, WmsRequestLayer) for a single CatalogEntry.

    Returns the new Dataset UUID.
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
        layer_type='wms',
        metadata=metadata,
        published=True,
        public=True,
        multi_temporal=entry.multi_temporal,
        multi_layer=False,
        near_realtime=False,
        can_clip=False,
        initial_visible=False,
    )

    if entry.description:
        dataset.summary = entry.description
        dataset.save(update_fields=['summary'])

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
    )

    WmsRequestLayer.objects.create(
        layer=wms_layer,
        name=entry.layer_name,
    )

    return dataset.id


def _deprovision_entry(entry):
    """
    Delete the Climweb Dataset associated with a CatalogEntry.
    Cascading deletes handle WmsLayer and WmsRequestLayer.
    """
    if entry.dataset_id:
        Dataset.objects.filter(id=entry.dataset_id).delete()


def add_entry(data, origin=CatalogEntry.ORIGIN_MANUAL):
    """
    Add a new CatalogEntry from manual input or WMS import.
    """
    layer_name = data['layer_name']
    wms_url = data['wms_url']

    product_code = data.get('product_code')
    if not product_code:
        product_code = CatalogEntry.generate_product_code(layer_name, wms_url, origin)

    entry = CatalogEntry.objects.create(
        product_code=product_code,
        title=data.get('title', layer_name),
        description=data.get('description', ''),
        category_title=data['category_title'],
        category_icon=data.get('category_icon', 'map'),
        subcategory_title=data['subcategory_title'],
        layer_name=layer_name,
        wms_url=wms_url,
        layer_title=data.get('layer_title', ''),
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
            'layer_name': entry.layer_name,
            'wms_url': entry.wms_url,
            'enabled': entry.enabled,
            'status': entry.status,
            'origin': entry.origin,
            'meta_source': entry.meta_source,
            'meta_resolution': entry.meta_resolution,
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
