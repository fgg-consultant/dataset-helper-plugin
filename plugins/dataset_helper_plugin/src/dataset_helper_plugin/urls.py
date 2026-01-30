from django.urls import path
from . import views

urlpatterns = [
    path('action/', views.vue_action, name='vue_action'),
    path('bulk-import/', views.bulk_import, name='bulk_import'),
    path('clear-all/', views.clear_all, name='clear_all'),
    path('', views.index, name='index'),
]

