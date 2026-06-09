# The layer catalog

The **Layer Catalog** tab is the plugin's main screen. It shows the **Category › SubCategory › Layer** tree and lets you control what gets provisioned into Climweb.

## Counters

Three counters at the top of the page summarize the catalog state:

- **Total Layers** — total number of `CatalogEntry`, all origins combined.
- **Enabled** — checked entries (those that will be or already are in Climweb).
- **Synced** — entries actually provisioned in Climweb.

The gap between *Enabled* and *Synced* is what will be modified by the next sync.

## Layer status

Each layer row carries a colored dot:

| Dot | Status              | Meaning                                                          |
|-----|---------------------|------------------------------------------------------------------|
| 🟢  | `synced`             | Checked and provisioned in Climweb.                              |
| 🟠  | `pending_add`        | Checked but not yet provisioned.                                 |
| 🔴  | `pending_remove`     | Unchecked but still in Climweb.                                   |
| ⚪  | `disabled`           | Unchecked and absent from Climweb.                                |

Only **Synchronize with Climweb** clears the orange and red states.

## Navigating the tree

The tree is fully collapsible. Three main interactions:

- Clicking a **category** or **subcategory** header expands / collapses it.
- The ▼ and ▶ buttons above the tree expand or collapse **everything**.
- Clicking a layer row opens / closes its **detail panel** (WMS URL, layer identifier, source metadata…).

## Check / uncheck

- **A single layer**: the checkbox to the left of the title enables or disables that entry.
- **A subcategory**: the checkbox in its header toggles **every layer** of the subcategory at once (bulk toggle).
- **A category**: same, but across the whole category.

The effect is immediate on the plugin side (status flips to `pending_add` / `pending_remove`) but **nothing is yet written to Climweb**. Click **Synchronize with Climweb** to apply.

## Layer origin

Every entry carries an **origin** describing how it ended up in the catalog:

| Origin       | How it appeared                                                                 |
|--------------|----------------------------------------------------------------------------------|
| `config`     | Loaded from the bundled JSON catalog (or a manually imported JSON).             |
| `manual`     | Added via the *+ Add Layer* form.                                                |
| `wms_import` | Imported from a remote WMS GetCapabilities.                                     |

The origin matters mostly for bundled-catalog **updates**: only `config` entries can be flagged `to_remove` when they disappear from a new JSON version. `manual` and `wms_import` entries are never touched by automatic updates.

## Toolbar actions

Below the settings panel, the toolbar groups the main actions:

- **Synchronize with Climweb** — applies the current selection (see [Synchronize](./sync)).
- **Load embedded catalog** — previews and applies the catalog bundled with the plugin (see [Catalog updates](./updates)).
- **Reset Catalog** — **destructive** operation; see [Danger zone](./danger-zone).
