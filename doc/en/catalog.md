# The layer catalog

The **Layer Catalog** tab is the plugin's main screen. It shows the **Category › SubCategory › Layer** tree and lets you control what gets provisioned into Climweb.

At the top of the tab a header recalls the context — *GeoManager · Layer catalog for the Climweb map viewer* — with a chip showing the currently loaded catalog version (or *not loaded*) and a link to this documentation.

## Overview

A card at the top summarizes the catalog state.

Three counters:

- **Catalog layers** — total number of `CatalogEntry`, all origins combined.
- **Enabled** — checked entries (those that will be or already are in Climweb).
- **Synced** — entries actually provisioned in Climweb.

A **status gauge** then breaks the catalog down by state — **Synced**, **To add**, **To remove**, **Disabled** — with a colored legend, so you can see at a glance how far the catalog is from Climweb.

A discreet line recalls the loaded version: *Catalog vX · loaded DATE*.

## Sync status

The plugin surfaces immediately whether Climweb is in sync with your local selection:

- **In sync** — nothing is shown; Climweb mirrors your catalog exactly.
- **Out of sync** — a prominent banner appears just below the overview: *Catalog out of sync with Climweb — N pending changes — X to create, Y to remove, Z to update*, together with a **Synchronize with Climweb** button.

After you run a sync (or load/reset), the **result** appears in the same place, in the same style — green on success, red on error — with a green **×** to dismiss it.

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
- Clicking a layer row opens / closes its **detail panel** (WMS URL, layer identifier, source metadata, multi-temporal, initially visible, near real-time, auto-update interval…).

## Check / uncheck

- **A single layer**: the checkbox to the left of the title enables or disables that entry.
- **A subcategory**: the checkbox in its header toggles **every layer** of the subcategory at once (bulk toggle).
- **A category**: same, but across the whole category.

The effect is immediate on the plugin side (status flips to `pending_add` / `pending_remove`) but **nothing is yet written to Climweb**. The out-of-sync banner then appears — click **Synchronize with Climweb** to apply.

## Layer origin

Every entry carries an **origin** describing how it ended up in the catalog:

| Origin       | How it appeared                                                                 |
|--------------|----------------------------------------------------------------------------------|
| `config`     | Loaded from the bundled JSON catalog. This is the only origin created today.    |
| `manual` / `wms_import` | Legacy origins from earlier plugin versions (manual add / WMS import). Those flows have been removed; such entries may still exist on older instances. |

The origin matters mostly for bundled-catalog **updates**: only `config` entries can be flagged `to_remove` when they disappear from a new catalog version. Legacy `manual` / `wms_import` entries are never touched by automatic updates.

## Empty catalog

When no catalog has been loaded yet, the tab shows **only** a warning block — *No catalog loaded yet* — with a **Load catalog** button. Clicking it loads the bundled catalog **directly** (no preview, since there is nothing to conflict with). The overview and the tree then appear. See [Getting started](./getting-started).

## Toolbar

Once a catalog is loaded, a single action remains in the toolbar:

- **Reset Catalog** — **destructive** operation; see [Danger zone](./danger-zone).

Loading and synchronizing are driven by the banners described above rather than by toolbar buttons:

- the **Load catalog** button (empty state) or the update banner's **Review changes** (see [Catalog updates](./updates)) populate the catalog,
- the **Synchronize with Climweb** button (out-of-sync banner) propagates the selection to Climweb (see [Synchronize](./sync)).
