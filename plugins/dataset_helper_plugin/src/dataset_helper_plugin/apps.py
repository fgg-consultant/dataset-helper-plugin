from django.apps import AppConfig

from climweb.base.registries import plugin_registry


class PluginNameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "dataset_helper_plugin"

    def ready(self):
        from .plugins import PluginNamePlugin

        plugin_registry.register(PluginNamePlugin())
