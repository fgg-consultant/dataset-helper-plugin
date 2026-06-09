# Getting started

This page walks through the minimum steps to make a first set of WMS layers appear in the Climweb mapviewer using the Dataset Helper plugin.

## Install the plugin in Climweb

Before using the plugin from the Wagtail admin, it needs to be installed on the Climweb side. Edit your Climweb instance's `.env` file:

1. Update Climweb to the compatible version:
   ```ini
   CLIMWEB_VERSION=1.1.3
   ```
2. Declare the plugin repository:
   ```ini
   CLIMWEB_PLUGIN_GIT_REPOS=https://github.com/fgg-consultant/dataset-helper-plugin
   ```

Then restart Climweb so the declared plugin is fetched and installed:

```bash
docker compose down
docker compose up -d
```

For the full procedure and advanced options (multiple plugins, specific branch/tag, private plugins…), see the [official Climweb documentation](https://climweb.readthedocs.io/en/v1.1.1/_docs/technical/extending-climweb/plugin-installation.html).

## 1. Open the Dataset helper page

In the Wagtail admin, open **GeoManager → Dataset helper**.

On the first launch the central tree is empty: the plugin knows that a default catalog exists on disk but has not yet loaded it into the database. A banner at the top of the page reminds you.

## 2. Fill in the required settings

Before loading the bundled catalog, expand the **Settings** panel (collapsed just under the counters). At minimum:

- **Country** *(required)* — pick the target country. This is used to substitute the `{country_alpha3}` / `{country_alpha2}` placeholders in layer URLs and to set the map's initial framing (bbox from Nominatim).
- **Language** — language in which titles and descriptions are imported (`en`, `fr`, `es`, `pt`, `ar`).

Optional, depending on which providers you want to enable:

- **ECMWF Token** — required for the private `eccharts.ecmwf.int` layers (the ones whose URL contains `token={ECMWF_TOKEN}`). Without a token, those layers are simply skipped on load.
- **Local eStation URL** — if filled in, only eStation products actually available on your local instance are imported. Leave empty to import everything.

Click **Save Settings**. While `Country` is missing the panel shows a warning.

See [Settings](./settings) for details.

## 3. Load the bundled catalog

Click **Load embedded catalog**. The plugin computes a *changeset* without writing anything and shows you:

- what will be **added** to the catalog,
- what will be **updated**,
- what will be **removed** (if you had loaded a previous version).

Click **Apply changes** to commit. The tree fills up and all entries default to `pending_add` (orange dot).

At this point **no Climweb object has been created yet**: the catalog has only been populated on the plugin side.

## 4. Refine the selection

In the tree:

- Uncheck the categories, subcategories or layers you don't want in Climweb.
- Every box is checked by default.
- You can collapse / expand the whole tree from the chevrons above it.

See [The layer catalog](./catalog).

## 5. Synchronize with Climweb

Click **Synchronize with Climweb**. The plugin:

- creates the `Category`, `SubCategory`, `Dataset`, `Metadata` and `WmsLayer` objects matching the checked entries,
- deletes those that correspond to entries you unchecked but were still in the database.

When the sync completes, entries become `synced` (green dot). The layers are now visible in the Climweb mapviewer.

See [Synchronize with Climweb](./sync).

## What's next?

- Later, when a new version of the plugin ships an updated catalog, see [Catalog updates](./updates).
