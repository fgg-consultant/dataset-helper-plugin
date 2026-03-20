from django.urls import path
from . import views

urlpatterns = [
    # Catalog API
    path('catalog/', views.catalog_tree, name='catalog_tree'),
    path('catalog/load-config/', views.catalog_load_config, name='catalog_load_config'),
    path('catalog/sync/', views.catalog_sync, name='catalog_sync'),
    path('catalog/<uuid:entry_id>/toggle/', views.catalog_toggle, name='catalog_toggle'),
    path('catalog/entry/', views.catalog_add_entry, name='catalog_add_entry'),
    path('catalog/reset/', views.catalog_reset, name='catalog_reset'),
    path('catalog/wms-capabilities/', views.catalog_wms_capabilities, name='catalog_wms_capabilities'),

    # Legacy endpoints
    path('action/', views.vue_action, name='vue_action'),
    path('bulk-import/', views.bulk_import, name='bulk_import'),
    path('clear-all/', views.clear_all, name='clear_all'),
    path('', views.index, name='index'),
]

