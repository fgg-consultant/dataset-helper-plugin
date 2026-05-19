# Add a layer manually

The **+ Add Layer** button (toolbar of the *Layer Catalog*) opens a form to insert into the catalog a layer that is not in the bundled catalog and does not come from a WMS import.

Layers added this way carry the origin **`manual`**: they are never touched by bundled-catalog updates and stay in the catalog until you delete them.

## Fields

| Field              | Required | Description                                                                |
|--------------------|:--------:|----------------------------------------------------------------------------|
| **Category**       | ✔        | Category title. Creates the category if it does not exist, otherwise attaches the new layer to it. |
| **Subcategory**    | ✔        | Same at the subcategory level.                                              |
| **Title**          |          | Displayed label. If empty, the WMS layer identifier is used.                |
| **WMS Layer Name** | ✔        | Exact layer identifier as it appears in the WMS GetCapabilities (`LAYERS` parameter). |
| **WMS Base URL**   | ✔        | Base WMS service URL, without query parameters.                             |
| **Source**         |          | Producer / organization at the origin of the data. Copied into `Metadata`.  |
| **Resolution**     |          | Spatial resolution (`1km`, `0.05deg`, etc.). Copied into `Metadata`.        |

Click **Add**: the entry is created immediately with status `pending_add` 🟠. It appears in the tree under the requested category / subcategory.

## What to do next

Click **Synchronize with Climweb** to actually provision the layer.

## Editing or deleting a manually added layer

A `manual` layer is managed like any other catalog entry:

- **Disable** (uncheck) it to flag it `pending_remove`; the next sync removes the `Dataset` from Climweb.
- **Re-enable** it to flip it back to `pending_add`; the next sync recreates it.

To change the URL or parameters, the simplest path is to disable the old one and add a fresh entry. Fine editing of a provisioned `Dataset` happens in the Wagtail admin (but it will be considered *local drift* — see [Catalog updates](./updates)).
