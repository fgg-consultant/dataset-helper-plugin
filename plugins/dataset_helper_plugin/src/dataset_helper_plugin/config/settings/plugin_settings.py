def setup(settings):
    """
    This function is called after climweb has setup its own Django settings file but
    before Django starts. Read and modify provided settings object as appropriate
    just like you would in a normal Django settings file. E.g.:

    settings.INSTALLED_APPS += ["some_custom_plugin_dep"]
    """

    import os
    plugin_dir = os.environ.get("CLIMWEB_PLUGIN_DIR")
    if not plugin_dir:
        raise RuntimeError("CLIMWEB_PLUGIN_DIR environment variable is not set.")

    static_dir = os.path.join(plugin_dir, "dataset_helper_plugin", "static")
    STATICFILES_DIRS = list(getattr(settings, "STATICFILES_DIRS", []))
    STATICFILES_DIRS.append(static_dir)
    settings.STATICFILES_DIRS = STATICFILES_DIRS
