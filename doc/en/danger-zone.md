# Danger zone

The **Danger Zone** tab and the **Reset Catalog** button in the toolbar group the **destructive** actions. They are all irreversible; read carefully before clicking.

## Reset Catalog

Red button in the *Layer Catalog* toolbar. This action:

1. **Deletes every Climweb `Dataset` provisioned by the plugin** (and only those: datasets created outside the plugin are preserved).
2. Deletes the associated `Metadata`.
3. Sweeps any `SubCategory` and `Category` that became empty.
4. **Wipes the entire `CatalogEntry` table** (`config`, `manual` and `wms_import` entries alike).
5. Resets `CatalogState` — the plugin forgets which version of the catalog was loaded.

Net effect: the plugin is back to the first-launch state, and only Climweb data created outside the plugin survives.

**When to use it:**

- To start from a clean slate before loading a different catalog.
- After a mistake during the initial setup phase.

**When not to use it:**

- In production, on a Climweb that serves users. Prefer selectively disabling layers and synchronizing.

## Clear catalog-managed datasets

Button in the *Danger Zone* tab. Less aggressive variant of *Reset Catalog*:

1. Deletes the Climweb `Dataset` objects provisioned by the plugin (same as above).
2. Deletes the associated `Metadata`.
3. Sweeps empty taxonomy nodes.
4. **Keeps** the `CatalogEntry` table: entries are reset to `pending_add` 🟠.

Net effect: Climweb is cleaned on the plugin side, but your selection (which layers are checked, your manual additions…) is intact. Clicking **Synchronize with Climweb** afterwards rebuilds everything from scratch with the current selection.

**Typical use case:** clearing persistent content drift on the Climweb side (titles edited by hand, stale versions of layers you want to overwrite cleanly).

## Clear All Datasets & Categories

Red button at the bottom of the *Danger Zone* tab. **Nuclear**:

- Deletes **every** `Dataset`, `SubCategory` and `Category` in the Climweb geomanager, whether from the plugin or not.
- Deletes every `WmsLayer`, `WmsRequestLayer`, `RasterStyle`, `Metadata`.
- Resets `dataset_id` on `CatalogEntry` rows.

Net effect: the Climweb mapviewer has no layer left.

**Only use it if you know exactly what you are doing** — for example during a full environment reset.

## Summary table

| Action                              | Plugin `CatalogEntry` | Plugin `Dataset` | Non-plugin `Dataset` | `Category` / `SubCategory` |
|-------------------------------------|:---------------------:|:----------------:|:--------------------:|:--------------------------:|
| Uncheck + Synchronize               | kept                  | deleted          | kept                 | kept if not empty          |
| Clear catalog-managed datasets      | kept (`pending_add`)  | deleted          | kept                 | swept if empty             |
| Reset Catalog                       | deleted               | deleted          | kept                 | swept if empty             |
| Clear All Datasets & Categories     | `dataset_id` cleared  | deleted          | **deleted**          | **deleted**                |
