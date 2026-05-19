# Synchronize with Climweb

The **Synchronize with Climweb** button (toolbar of the *Layer Catalog*) propagates the current catalog state to the Climweb database. It is the only action that actually creates or removes `Dataset` objects in geomanager.

## What the sync does

The plugin walks every entry and acts on its status:

| Status              | Action                                                                                         |
|---------------------|------------------------------------------------------------------------------------------------|
| `pending_add` 🟠     | Provisions into Climweb: creates / reuses `Category` and `SubCategory`, creates `Dataset`, `Metadata`, then the layer objects (`WmsLayer`, `WmsRequestLayer`, etc. depending on the layer type). |
| `pending_remove` 🔴  | Deprovisions: deletes the `Dataset` (and dependents) on the Climweb side, clears `dataset_id`. |
| `synced` 🟢          | Checks that the `Dataset` still exists. If the catalog content has moved since the last sync, **re-provisions** (titles, URLs or metadata are updated). |
| `disabled` ⚪        | Nothing to do.                                                                                  |

At the end, a result panel summarizes the run:

```
Sync complete: 12 added, 3 removed, 5 updated, 0 orphans cleared
```

## Edge cases

### Orphans

If an entry is marked `synced` but its Climweb `Dataset` has been deleted in the meantime (for example via the Wagtail admin), it is detected as **orphaned**: `dataset_id` is reset to `null` and the entry falls back to `pending_add`. A second sync will recreate it.

The **orphans cleared** counter in the result panel reflects these reconciliations.

### Shared categories and subcategories

The plugin **never deletes** a `Category` or `SubCategory` that still contains non-plugin `Dataset` objects. If you manually created a dataset under a category also used by the plugin, deprovisioning the plugin's entries won't drop that category.

Empty categories *are* swept at the end of the run (see [Danger zone](./danger-zone)).

### `raster_file` layers

`raster_file` layers (raster files uploaded into Climweb) are **not automatically re-provisioned** when the catalog changes: overwriting them would destroy already-uploaded files. The plugin reports this via the `raster_file drift` counter and leaves the Climweb object alone. To apply the new content, delete the entry and recreate it (or wipe the layer and re-sync).

## After the sync

After a successful sync, the layers are visible in the Climweb mapviewer. On the plugin side:

- every checked entry is `synced`,
- every unchecked entry is `disabled`.

You can adjust the selection at any time and click **Synchronize with Climweb** again: only the diff since the last sync is applied.
