from geomanager.models.core import Dataset, Category, SubCategory, Metadata
from geomanager.models.raster_style import RasterStyle
from geomanager.models.wms import WmsLayer, WmsRequestLayer
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
import json
import logging

logger = logging.getLogger(__name__)

from .models import CatalogEntry, CatalogState, PluginSettings
from . import services

# Valid layer types from Dataset.DATASET_TYPE_CHOICES
VALID_LAYER_TYPES = ('raster_file', 'vector_file', 'wms', 'raster_tile', 'vector_tile')


def index(request):
    template_name = "dataset_helper_plugin/index.html"
    return render(request, template_name, {'plugin_settings': PluginSettings.load()})


# ── Catalog API ──────────────────────────────────────────────────────────────


def catalog_tree(request):
    """Return the full catalog as a JSON tree for the UI."""
    try:
        tree = services.get_catalog_tree()
        total = CatalogEntry.objects.count()
        enabled = CatalogEntry.objects.filter(enabled=True).count()
        synced = CatalogEntry.objects.exclude(dataset_id=None).filter(enabled=True).count()

        embedded_version, embedded_schema = services.get_embedded_catalog_version()
        state = CatalogState.load()
        update_available = bool(
            embedded_version and embedded_version != state.loaded_version
        )

        return JsonResponse({
            'status': 'success',
            'total': total,
            'enabled': enabled,
            'synced': synced,
            'categories': tree,
            'embedded_version': embedded_version,
            'embedded_schema_version': embedded_schema,
            'loaded_version': state.loaded_version,
            'loaded_schema_version': state.loaded_schema_version,
            'loaded_at': state.loaded_at.isoformat() if state.loaded_at else None,
            'update_available': update_available,
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

        msg = f"Catalog loaded: {stats['created']} created, {stats['updated']} updated"
        if stats.get('skipped_estation'):
            msg += f", {stats['skipped_estation']} skipped (not on local eStation)"

        return JsonResponse({
            'status': 'success',
            'message': msg,
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
        logger.exception("catalog_sync failed")
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
def catalog_bulk_toggle(request):
    """Set enabled flag for multiple catalog entries at once."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {e}'}, status=400)

    entry_ids = data.get('entry_ids', [])
    enabled = data.get('enabled', True)

    if not entry_ids:
        return JsonResponse({'status': 'error', 'message': 'No entry_ids provided'}, status=400)

    updated = CatalogEntry.objects.filter(id__in=entry_ids).update(enabled=enabled)
    return JsonResponse({
        'status': 'success',
        'updated': updated,
        'enabled': enabled,
    })


@csrf_exempt
@require_POST
def catalog_reset(request):
    """Delete all CatalogEntry objects, resetting the catalog to empty."""
    try:
        count = CatalogEntry.objects.count()
        CatalogEntry.objects.all().delete()

        # An empty DB means no catalog is loaded — drop the recorded version
        # so the admin UI offers the "Load embedded catalog" banner again.
        state = CatalogState.load()
        state.loaded_version = ''
        state.loaded_schema_version = 0
        state.loaded_at = None
        state.save()

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

    # Always required
    required = ['category_title', 'subcategory_title']
    # Type-specific required fields
    layer_type = data.get('layer_type', 'wms')
    if layer_type == 'wms':
        required += ['layer_name', 'wms_url']
    elif layer_type in ('raster_tile', 'vector_tile'):
        required += ['tile_url']
    elif layer_type in ('raster_file', 'vector_file'):
        required += ['file_url']
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


# ── Settings API ────────────────────────────────────────────────────────────


def settings_get(request):
    """Return current plugin settings."""
    s = PluginSettings.load()
    return JsonResponse({
        'status': 'success',
        'language': s.language,
        'ecmwf_token': s.ecmwf_token,
        'estation_url': s.estation_url,
        'country_alpha3': s.country_alpha3,
        'country_alpha2': s.country_alpha2,
        'country_name': s.country_name,
        'country_bbox': s.country_bbox,
    })


@csrf_exempt
@require_POST
def settings_save(request):
    """Update plugin settings."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {e}'}, status=400)

    s = PluginSettings.load()

    if 'language' in data:
        lang = data['language']
        if lang not in dict(PluginSettings.LANGUAGE_CHOICES):
            return JsonResponse({'status': 'error', 'message': f'Invalid language: {lang}'}, status=400)
        s.language = lang

    if 'ecmwf_token' in data:
        s.ecmwf_token = (data['ecmwf_token'] or '').strip()

    if 'estation_url' in data:
        s.estation_url = data['estation_url'] or ''

    # Country is mandatory: alpha3 + alpha2 + name + bbox are saved together.
    if any(k in data for k in ('country_alpha3', 'country_alpha2', 'country_name', 'country_bbox')):
        alpha3 = (data.get('country_alpha3') or '').strip().lower()[:3]
        if not alpha3 or len(alpha3) != 3 or not alpha3.isalpha():
            return JsonResponse(
                {'status': 'error', 'message': 'country_alpha3 is required (ISO 3166-1 alpha-3)'},
                status=400,
            )
        alpha2 = (data.get('country_alpha2') or '').strip().lower()[:2]
        if not alpha2 or len(alpha2) != 2 or not alpha2.isalpha():
            return JsonResponse(
                {'status': 'error', 'message': 'country_alpha2 is required (ISO 3166-1 alpha-2)'},
                status=400,
            )
        name = (data.get('country_name') or '').strip()[:255]
        if not name:
            return JsonResponse(
                {'status': 'error', 'message': 'country_name is required'},
                status=400,
            )
        bbox = data.get('country_bbox')
        if not (isinstance(bbox, list) and len(bbox) == 4
                and all(isinstance(v, (int, float)) for v in bbox)):
            return JsonResponse(
                {'status': 'error',
                 'message': 'country_bbox must be a list of 4 numbers [south, north, west, east]'},
                status=400,
            )
        s.country_alpha3 = alpha3
        s.country_alpha2 = alpha2
        s.country_name = name
        s.country_bbox = [float(v) for v in bbox]

    s.save()
    return JsonResponse({
        'status': 'success',
        'message': 'Settings saved',
        'language': s.language,
        'ecmwf_token': s.ecmwf_token,
        'estation_url': s.estation_url,
        'country_alpha3': s.country_alpha3,
        'country_bbox': s.country_bbox,
    })


@csrf_exempt
@require_POST
def clear_all(request):
    """
    Clear all datasets and categories.
    This will delete all WmsRequestLayer, WmsLayer, Metadata, Dataset, SubCategory, and Category objects.
    """
    deleted = {
        'wms_request_layers': 0,
        'wms_layers': 0,
        'raster_styles': 0,
        'datasets': 0,
        'metadata': 0,
        'subcategories': 0,
        'categories': 0,
    }
    errors = []

    # Delete in order (respecting foreign key constraints)
    # Bulk deletes for child models that are unlikely to have external references
    for model, key in [
        (WmsRequestLayer, 'wms_request_layers'),
        (WmsLayer, 'wms_layers'),
    ]:
        try:
            count, _ = model.objects.all().delete()
            deleted[key] = count
        except Exception as e:
            errors.append(f"Failed to bulk delete {key}: {e}")

    # Delete datasets, metadata, subcategories, categories one by one to skip protected ones
    # (raster styles are deleted after datasets because RasterFileLayer.style uses SET_NULL,
    # so they aren't removed by the dataset cascade)
    for model, key in [
        (Metadata, 'metadata'),
        (Dataset, 'datasets'),
        (RasterStyle, 'raster_styles'),
        (SubCategory, 'subcategories'),
        (Category, 'categories'),
    ]:
        for obj in model.objects.all():
            try:
                obj.delete()
                deleted[key] += 1
            except Exception as e:
                errors.append(f"Could not delete {key[:-1]} '{obj}': {e}")

    # Clear dataset_id references in catalog entries
    CatalogEntry.objects.exclude(dataset_id=None).update(dataset_id=None)

    if errors:
        return JsonResponse({
            'status': 'partial',
            'message': f'Completed with {len(errors)} error(s)',
            'deleted': deleted,
            'errors': errors,
        })

    return JsonResponse({
        'status': 'success',
        'message': 'All data cleared successfully',
        'deleted': deleted,
    })
