# Import from a WMS

The **Import from WMS** button queries a remote WMS server and picks a layer from its `GetCapabilities`. It is faster than typing the URL and the identifier by hand: the plugin reads the metadata directly from the provider.

Layers imported this way carry the origin **`wms_import`**: they are never touched by bundled-catalog updates.

## The three-step flow

### 1. Enter the WMS URL

Type the base URL of the service (e.g. `https://example.org/wms`). The plugin builds the `GetCapabilities` URL automatically (`?service=WMS&request=GetCapabilities&version=1.3.0`).

Click **Fetch Layers**.

### 2. Pick a layer

The plugin lists every layer returned by the server, with:

- the identifier (`name`),
- the human title (`title`),
- the abstract,
- the WGS84 bbox when exposed.

A search field filters the list by name / title / abstract. Click a row to select it.

::: tip
If you typed the wrong URL, the *Change URL* link next to the layer count brings you back to step 1 without reloading the page.
:::

### 3. Configure the chosen layer

A small green form appears with:

| Field            | Description                                                                |
|------------------|----------------------------------------------------------------------------|
| **Layer Name**   | Pre-filled, read-only. The identifier as returned by the WMS.              |
| **Title**        | Pre-filled with the WMS title. Editable.                                    |
| **Category** *   | Category under which the layer will be classified. Created if it does not exist. |
| **Subcategory** *| Same.                                                                       |
| **Description**  | Pre-filled from the WMS abstract. Used as summary / metadata.               |

Click **Add to Catalog**: the entry is created with status `pending_add` 🟠 and appears in the tree.

The **Back to list** button returns to the layer list of the same server — handy to import multiple layers from the same provider in a row.

## What to do next

As always, click **Synchronize with Climweb** to actually provision the layer.

## Limits

- The plugin only supports **WMS 1.3.0**. If the server only exposes older versions, the call may fail.
- Server-side **styles** and **CRS** are not exposed in the form (only the plugin's default CRS, `EPSG:3857`, is used for Climweb requests).
- The form creates **one layer at a time**. For a bulk import from the same server, prefer building a JSON file and using [Load Config JSON](./load-config).
