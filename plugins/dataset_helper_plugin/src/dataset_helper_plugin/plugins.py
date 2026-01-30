from climweb.base.registries import Plugin


class PluginNamePlugin(Plugin):
    type = "dataset_helper_plugin"

    def get_urls(self):
        return []
