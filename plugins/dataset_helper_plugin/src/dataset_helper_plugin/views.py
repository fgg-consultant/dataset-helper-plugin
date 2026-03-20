from geomanager.models.core import Dataset, Category, SubCategory, Metadata
from geomanager.models.wms import WmsLayer, WmsRequestLayer
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
import json

from .models import CatalogEntry
from . import services

# Valid layer types from Dataset.DATASET_TYPE_CHOICES
VALID_LAYER_TYPES = ('raster_file', 'vector_file', 'wms', 'raster_tile', 'vector_tile')


def index(request):
    # Retrieve all Dataset objects from the database
    datasets = Dataset.objects.all()
    # All categories for the listing view
    categories = Category.objects.all().order_by('title')
    # Active/public categories for defaults
    active_categories = Category.objects.filter(active=True, public=True)
    # Get the first category and its first subcategory as defaults
    default_category = active_categories.first()
    default_subcategory = default_category.sub_categories.first() if default_category else None

    template_name = "dataset_helper_plugin/index.html"
    context = {
        'datasets': datasets,
        'categories': categories,
        'default_category_id': default_category.pk if default_category else None,
        'default_subcategory_id': default_subcategory.pk if default_subcategory else None,
    }
    return render(request, template_name, context)


# ── Catalog API ──────────────────────────────────────────────────────────────


def catalog_tree(request):
    """Return the full catalog as a JSON tree for the UI."""
    try:
        tree = services.get_catalog_tree()
        total = CatalogEntry.objects.count()
        enabled = CatalogEntry.objects.filter(enabled=True).count()
        synced = CatalogEntry.objects.exclude(dataset_id=None).filter(enabled=True).count()
        return JsonResponse({
            'status': 'success',
            'total': total,
            'enabled': enabled,
            'synced': synced,
            'categories': tree,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Server error: {e}'}, status=500)


@csrf_exempt
@require_POST
def catalog_load_config(request):
    """Load a JSON config into the catalog (CatalogEntry table)."""
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {e}'}, status=400)

        if not isinstance(data, dict):
            return JsonResponse({'status': 'error', 'message': 'Expected a JSON object'}, status=400)

        stats = services.load_catalog_from_config(data)

        if stats['created'] == 0 and stats['updated'] == 0 and stats['errors']:
            return JsonResponse({
                'status': 'error',
                'message': stats['errors'][0],
                **stats,
            }, status=400)

        return JsonResponse({
            'status': 'success',
            'message': f"Catalog loaded: {stats['created']} created, {stats['updated']} updated",
            **stats,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Server error: {e}'}, status=500)


@csrf_exempt
@require_POST
def catalog_sync(request):
    """Provision enabled entries to Climweb and deprovision disabled ones."""
    try:
        stats = services.sync_catalog_to_climweb()
        return JsonResponse({
            'status': 'success',
            'message': (
                f"Sync complete: {stats['added']} added, "
                f"{stats['removed']} removed, "
                f"{stats['orphans_cleared']} orphans cleared"
            ),
            **stats,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Sync failed: {e}'}, status=500)


@csrf_exempt
@require_POST
def catalog_toggle(request, entry_id):
    """Toggle the enabled flag on a single catalog entry."""
    try:
        entry = CatalogEntry.objects.get(id=entry_id)
    except CatalogEntry.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Entry not found'}, status=404)

    entry.enabled = not entry.enabled
    entry.save(update_fields=['enabled', 'updated_at'])
    return JsonResponse({
        'status': 'success',
        'id': str(entry.id),
        'enabled': entry.enabled,
        'new_status': entry.status,
    })


@csrf_exempt
@require_POST
def catalog_reset(request):
    """Delete all CatalogEntry objects, resetting the catalog to empty."""
    try:
        count = CatalogEntry.objects.count()
        CatalogEntry.objects.all().delete()
        return JsonResponse({
            'status': 'success',
            'message': f'Catalog reset: {count} entries deleted',
            'deleted': count,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Reset failed: {e}'}, status=500)


@csrf_exempt
@require_POST
def catalog_add_entry(request):
    """Add a manual catalog entry."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {e}'}, status=400)

    required = ['layer_name', 'wms_url', 'category_title', 'subcategory_title']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return JsonResponse({
            'status': 'error',
            'message': f"Missing required fields: {', '.join(missing)}",
        }, status=400)

    try:
        entry = services.add_entry(data, origin=CatalogEntry.ORIGIN_MANUAL)
        return JsonResponse({
            'status': 'success',
            'message': f"Entry '{entry.title}' added",
            'id': str(entry.id),
            'product_code': entry.product_code,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
@require_POST
def catalog_wms_capabilities(request):
    """
    Fetch layers from a remote WMS GetCapabilities.
    Expects: { "wms_url": "https://..." }
    Returns list of layers with name, title, abstract for the UI picker.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {e}'}, status=400)

    wms_url = data.get('wms_url', '').strip()
    if not wms_url:
        return JsonResponse({'status': 'error', 'message': 'Missing wms_url'}, status=400)

    # Build proper GetCapabilities URL
    separator = '&' if '?' in wms_url else '?'
    caps_url = f"{wms_url}{separator}service=WMS&request=GetCapabilities&version=1.3.0"

    try:
        from owslib.wms import WebMapService
        wms = WebMapService(caps_url, version='1.3.0')
    except ImportError:
        return JsonResponse({
            'status': 'error',
            'message': 'owslib is not installed. Cannot read WMS capabilities.',
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to read WMS capabilities: {e}',
        }, status=400)

    layers = []
    for layer_name, layer_meta in wms.contents.items():
        layer_info = {
            'name': layer_name,
            'title': layer_meta.title or layer_name,
            'abstract': layer_meta.abstract or '',
        }
        # Extract bounding box if available
        if hasattr(layer_meta, 'boundingBoxWGS84') and layer_meta.boundingBoxWGS84:
            layer_info['bbox'] = list(layer_meta.boundingBoxWGS84)
        # Extract available SRS/CRS
        if hasattr(layer_meta, 'crsOptions') and layer_meta.crsOptions:
            layer_info['crs'] = list(layer_meta.crsOptions)[:5]
        layers.append(layer_info)

    return JsonResponse({
        'status': 'success',
        'wms_url': wms_url,
        'total': len(layers),
        'layers': layers,
    })


# ── Legacy endpoints (kept for backward compatibility) ───────────────────────


@csrf_exempt
def vue_action(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            category_id = data.get('category_id')
            sub_category_id = data.get('sub_category_id')

            # Layer information
            layer_title = data.get('layer_title')
            layer_name = data.get('layer_name')
            wms_url = data.get('wms_url')

            # Optional WMS configuration
            wms_version = data.get('wms_version', '1.3.0')  # Default to 1.3.0
            wms_format = data.get('wms_format', 'image/png')
            wms_srs = data.get('wms_srs', 'EPSG:3857')
            wms_transparent = data.get('wms_transparent', True)
            wms_width = data.get('wms_width', 256)
            wms_height = data.get('wms_height', 256)
            request_time_from_capabilities = data.get('request_time_from_capabilities', True)

            if not (title and category_id and sub_category_id):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            category = Category.objects.get(id=category_id)
            sub_category = SubCategory.objects.get(id=sub_category_id)

            # Create the dataset
            dataset = Dataset.objects.create(
                title=title,
                category=category,
                sub_category=sub_category,
                layer_type='wms',
                published=True,
                public=True,
                multi_temporal=True,  # WMS layers are often multi-temporal
                multi_layer=False,    # Single layer by default
                near_realtime=False,
                can_clip=False,       # WMS doesn't support clipping
                initial_visible=False
            )

            # Create WMS layer if layer information is provided
            wms_layer = None
            if layer_title and layer_name and wms_url:
                wms_layer = WmsLayer.objects.create(
                    dataset=dataset,
                    title=layer_title,
                    base_url=wms_url,
                    version=wms_version,
                    width=wms_width,
                    height=wms_height,
                    transparent=wms_transparent,
                    srs=wms_srs,
                    format=wms_format,
                    default=True,
                    request_time_from_capabilities=request_time_from_capabilities
                )

                # Create the required WmsRequestLayer (min_num=1 in the model)
                WmsRequestLayer.objects.create(
                    layer=wms_layer,
                    name=layer_name
                )

            response_data = {
                'status': 'success',
                'message': 'Dataset created',
                'dataset_id': str(dataset.id)
            }

            if wms_layer:
                response_data['layer_id'] = str(wms_layer.id)
                response_data['message'] = 'Dataset and WMS layer created successfully'

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt
def bulk_import(request):
    """
    Bulk import endpoint for creating categories, subcategories, datasets and layers.

    Expected JSON format:
    {
        "categories": [
            {
                "title": "Category Name",
                "icon": "leaf",
                "subcategories": [
                    {
                        "title": "Subcategory Name",
                        "datasets": [
                            {
                                "title": "Dataset Title",
                                "description": "Dataset description",
                                "multi_temporal": true,
                                "metadata": {
                                    "title": "Metadata title",
                                    "function": "Short summary",
                                    "resolution": "1km",
                                    "geographic_coverage": "Africa",
                                    "source": "Copernicus",
                                    "license": "CC-BY-4.0",
                                    "frequency_of_update": "Daily",
                                    "overview": "Detailed description...",
                                    "learn_more": "https://example.com"
                                },
                                "layers": [
                                    {
                                        "type": "wms",
                                        "title": "Layer Title",
                                        "layer_name": "wms_layer_name",
                                        "wms_url": "https://example.com/wms",
                                        "default": true
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {str(e)}'}, status=400)

    categories_data = data.get('categories', [])

    if not categories_data:
        return JsonResponse({'status': 'error', 'message': 'No categories provided'}, status=400)

    results = {
        'categories_created': 0,
        'categories_existing': 0,
        'subcategories_created': 0,
        'subcategories_existing': 0,
        'datasets_created': 0,
        'datasets_skipped': 0,
        'layers_created': 0,
        'metadata_created': 0,
        'errors': [],
        'created_items': []
    }

    try:
        with transaction.atomic():
            for cat_data in categories_data:
                cat_title = cat_data.get('title')
                if not cat_title:
                    results['errors'].append('Category missing title field')
                    continue

                # Get or create category
                category, cat_created = Category.objects.get_or_create(
                    title=cat_title,
                    defaults={
                        'icon': cat_data.get('icon', 'map'),
                        'active': True,
                        'public': True
                    }
                )

                if cat_created:
                    results['categories_created'] += 1
                    results['created_items'].append({
                        'type': 'category',
                        'title': cat_title
                    })
                else:
                    results['categories_existing'] += 1

                # Process subcategories
                for subcat_data in cat_data.get('subcategories', []):
                    subcat_title = subcat_data.get('title')
                    if not subcat_title:
                        results['errors'].append(f'Subcategory missing title in category "{cat_title}"')
                        continue

                    # Get or create subcategory
                    subcategory, subcat_created = SubCategory.objects.get_or_create(
                        title=subcat_title,
                        category=category,
                        defaults={
                            'active': True,
                            'public': True
                        }
                    )

                    if subcat_created:
                        results['subcategories_created'] += 1
                        results['created_items'].append({
                            'type': 'subcategory',
                            'title': subcat_title,
                            'category': cat_title
                        })
                    else:
                        results['subcategories_existing'] += 1

                    # Process datasets
                    for dataset_data in subcat_data.get('datasets', []):
                        dataset_title = dataset_data.get('title')

                        if not dataset_title:
                            results['errors'].append(
                                f'Dataset missing title in "{cat_title}/{subcat_title}"'
                            )
                            continue

                        # Check for duplicate dataset
                        existing = Dataset.objects.filter(
                            title=dataset_title,
                            category=category,
                            sub_category=subcategory
                        ).exists()

                        if existing:
                            results['datasets_skipped'] += 1
                            results['errors'].append(
                                f'Dataset "{dataset_title}" already exists in "{cat_title}/{subcat_title}"'
                            )
                            continue

                        # Determine layer_type from first layer's type (default: wms)
                        layers_data = dataset_data.get('layers', [])
                        layer_type = 'wms'
                        if layers_data:
                            first_layer_type = layers_data[0].get('type', 'wms')
                            if first_layer_type in VALID_LAYER_TYPES:
                                layer_type = first_layer_type

                        multi_layer = len(layers_data) > 1

                        # Create metadata if provided
                        metadata = None
                        metadata_data = dataset_data.get('metadata')
                        if metadata_data:
                            metadata = Metadata.objects.create(
                                title=metadata_data.get('title', dataset_title),
                                subtitle=metadata_data.get('subtitle'),
                                function=metadata_data.get('function'),
                                resolution=metadata_data.get('resolution'),
                                geographic_coverage=metadata_data.get('geographic_coverage'),
                                source=metadata_data.get('source'),
                                license=metadata_data.get('license'),
                                frequency_of_update=metadata_data.get('frequency_of_update'),
                                overview=metadata_data.get('overview'),
                                cautions=metadata_data.get('cautions'),
                                citation=metadata_data.get('citation'),
                                download_data=metadata_data.get('download_data'),
                                learn_more=metadata_data.get('learn_more')
                            )
                            results['metadata_created'] += 1

                        # Create dataset
                        dataset = Dataset.objects.create(
                            title=dataset_title,
                            category=category,
                            sub_category=subcategory,
                            layer_type=layer_type,
                            metadata=metadata,
                            published=True,
                            public=True,
                            multi_temporal=dataset_data.get('multi_temporal', True),
                            multi_layer=multi_layer,
                            near_realtime=False,
                            can_clip=layer_type != 'wms',
                            initial_visible=False
                        )

                        # Add summary/description if provided
                        description = dataset_data.get('description', '')
                        if description:
                            dataset.summary = description
                            dataset.save()

                        results['datasets_created'] += 1
                        results['created_items'].append({
                            'type': 'dataset',
                            'title': dataset_title,
                            'layer_type': layer_type,
                            'category': cat_title,
                            'subcategory': subcat_title
                        })

                        # Process layers for this dataset (currently only WMS supported)
                        for layer_data in layers_data:
                            layer_type_value = layer_data.get('type', 'wms')

                            # Only WMS layers are currently supported
                            if layer_type_value != 'wms':
                                results['errors'].append(
                                    f'Layer type "{layer_type_value}" not yet supported in dataset "{dataset_title}"'
                                )
                                continue

                            layer_name = layer_data.get('layer_name')
                            layer_title = layer_data.get('title', dataset_title)
                            wms_url = layer_data.get('wms_url')

                            if not layer_name or not wms_url:
                                results['errors'].append(
                                    f'Layer missing layer_name or wms_url in dataset "{dataset_title}"'
                                )
                                continue

                            # WMS configuration (layer-level or defaults)
                            wms_version = layer_data.get('wms_version', '1.3.0')
                            wms_format = layer_data.get('wms_format', 'image/png')
                            wms_srs = layer_data.get('wms_srs', 'EPSG:3857')
                            wms_width = layer_data.get('wms_width', 256)
                            wms_height = layer_data.get('wms_height', 256)

                            # Create WMS layer
                            wms_layer = WmsLayer.objects.create(
                                dataset=dataset,
                                title=layer_title,
                                base_url=wms_url,
                                version=wms_version,
                                width=wms_width,
                                height=wms_height,
                                transparent=True,
                                srs=wms_srs,
                                format=wms_format,
                                default=layer_data.get('default', False),
                                request_time_from_capabilities=True
                            )

                            # Create WmsRequestLayer
                            WmsRequestLayer.objects.create(
                                layer=wms_layer,
                                name=layer_name
                            )

                            results['layers_created'] += 1

        results['status'] = 'success'
        results['message'] = (
            f"Import complete: {results['datasets_created']} datasets, "
            f"{results['layers_created']} layers created, "
            f"{results['datasets_skipped']} skipped"
        )
        return JsonResponse(results)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Import failed: {str(e)}',
            'partial_results': results
        }, status=500)


@csrf_exempt
@require_POST
def clear_all(request):
    """
    Clear all datasets and categories.
    This will delete all WmsRequestLayer, WmsLayer, Metadata, Dataset, SubCategory, and Category objects.
    """
    try:
        with transaction.atomic():
            # Count items before deletion
            counts = {
                'wms_request_layers': WmsRequestLayer.objects.count(),
                'wms_layers': WmsLayer.objects.count(),
                'datasets': Dataset.objects.count(),
                'metadata': Metadata.objects.count(),
                'subcategories': SubCategory.objects.count(),
                'categories': Category.objects.count(),
            }

            # Delete in order (respecting foreign key constraints)
            WmsRequestLayer.objects.all().delete()
            WmsLayer.objects.all().delete()

            # Delete metadata associated with datasets
            Metadata.objects.filter(dataset__isnull=False).delete()

            Dataset.objects.all().delete()
            SubCategory.objects.all().delete()
            Category.objects.all().delete()

            # Clear dataset_id references in catalog entries
            CatalogEntry.objects.exclude(dataset_id=None).update(dataset_id=None)

            return JsonResponse({
                'status': 'success',
                'message': 'All data cleared successfully',
                'deleted': counts
            })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Clear failed: {str(e)}'
        }, status=500)
