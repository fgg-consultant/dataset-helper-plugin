# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dataset Helper Plugin for Climweb (Django/Wagtail framework). The plugin provides wizards to quickly create WMS reference datasets for the Climweb mapviewer, bootstrapping climate data platforms with pre-configured map layers.

**Domain Model:**
- **Category** → **SubCategory** → **Dataset** → **WmsLayer** → **WmsRequestLayer**
- Datasets are WMS-based and belong to categories/subcategories
- The plugin bulk-creates these objects from WMS endpoint capabilities
- The models are defined in `/__temp/models.py` and `./__tmp/wms.py`

## Architecture

**Dual-stack application:**
- **Backend**: Django plugin at `plugins/dataset_helper_plugin/` - Wagtail admin integration, API endpoints
- **Frontend**: Vue 3 SPA at `plugins/frontend/` - WMS layer discovery and selection UI

**Communication**: Vue frontend uses `window.postMessage()` to send selected layers to Django backend, which creates Dataset/WmsLayer objects via AJAX to `/admin/dataset_helper/action/`.

**Key Models** (from geomanager library):
- `Dataset`, `Category`, `SubCategory`, `WmsLayer`, `WmsRequestLayer`, `Metadata`


**Important**
You must not consider the frontend.
When asking for code, just generate backend code in the plugin folder.

## Plugin Vision

The plugin acts as a **managed catalog** of WMS layers for Climweb:

1. **Ships a default layer catalog** (~119 layers from various sources: JRC, ECMWF, CAMS, CGLS, etc.) defined in a JSON config
2. **Admin selects layers** via a collapsible tree UI (Category > SubCategory > Layer) with checkboxes — all checked by default
3. **"Load Layers" provisions** checked layers into Climweb DB (Category, SubCategory, Dataset, WmsLayer, Metadata)
4. **Tracks sync state** between the catalog and Climweb via the `CatalogEntry` model:
   - Each catalog entry has a `product_code` (natural key) and a nullable `dataset_id` (loose UUID ref to Climweb Dataset)
   - Status: `synced` (green), `pending_add` (orange), `pending_remove` (red), `disabled` (gray)
5. **Origin tracking**: each entry carries an `origin`. New entries are created with `config` (loaded from the embedded/JSON catalog). The `manual` and `wms_import` origins are retained on the model for backward compatibility with legacy data — the in-app "Add Layer" and "Import from WMS" creation flows have been removed. Automatic catalog updates only touch `config` entries.

## Documentation & Translations

**IMPORTANT — keep docs and translations in sync with every feature change.**
Whenever you add or change a plugin behavior, you must update **all languages**, not just one.

### User documentation (VitePress)

Located in `doc/`. Five languages, kept in **strict parity** (same set of pages, same structure):

| Locale | Folder      | Label     |
|--------|-------------|-----------|
| French (default) | `doc/` (root) | Français |
| English | `doc/en/`  | English   |
| Spanish | `doc/es/`  | Español   |
| Portuguese | `doc/pt/` | Português |
| Arabic | `doc/ar/`  | العربية   |

- Locales and sidebars are declared in `doc/.vitepress/config.mjs`.
- When you add/rename/remove a doc page or document a new feature, apply the change to **all five locales** and update the sidebar for each in `config.mjs`.

### UI strings (Django gettext)

Located in `plugins/dataset_helper_plugin/src/dataset_helper_plugin/locale/`. Translated languages: **fr, es, pt, ar** (`django.po` for Python/templates, `djangojs.po` for JS in `index.html`). English is the source (the `gettext(...)` / `{% trans %}` msgid — no English `.po`).

- Wrap every new user-facing string in `gettext(...)` (JS) or `{% trans %}` (templates).
- After adding strings, regenerate the catalogs (`makemessages -a` + `makemessages -d djangojs -a`), translate the new `msgid`s in **all four** `.po` files, then `compilemessages`.

## Development Commands

### Backend (from `plugins/dataset_helper_plugin/`)

### Docker
```bash
docker compose build    # Build dev image (requires climweb_dev:latest base)
docker compose up -d    # Run all services
# Access at http://localhost/admin
```

## Key Files

| Purpose             | Path                                                                                      |
|---------------------|-------------------------------------------------------------------------------------------|
| API Views           | `plugins/dataset_helper_plugin/src/dataset_helper_plugin/views.py`                        |
| Wagtail Integration | `plugins/dataset_helper_plugin/src/dataset_helper_plugin/wagtail_hooks.py`                |
| Admin Template      | `plugins/dataset_helper_plugin/src/dataset_helper_plugin/templates/dataset_helper_plugin/index.html` |
| mapviewer models    | `__tmp/models.py` |
| mapviewer wms model | `__tmp/wms.py` |

## WMS Defaults

When creating datasets, the plugin uses:
- Version: 1.3.0
- Format: image/png
- SRS: EPSG:3857
- Tile size: 256x256
- Multi-temporal: enabled
