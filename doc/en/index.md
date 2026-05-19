---
layout: home

hero:
  name: Dataset Helper
  text: The WMS layer catalog for Climweb
  tagline: Enable, import and synchronize mapviewer layers without touching the Wagtail admin.
  actions:
    - theme: brand
      text: Getting started
      link: /en/getting-started
    - theme: alt
      text: The catalog
      link: /en/catalog
    - theme: alt
      text: GitHub
      link: https://github.com/fgg-consultant/dataset-helper-plugin

features:
  - icon: 📚
    title: Bundled catalog
    details: ~119 ready-to-use WMS layers (JRC eStation, ECMWF, CAMS, EUMETSAT, CGLS…) shipped with the plugin.
  - icon: ✅
    title: Checkbox-driven selection
    details: Pick the layers you want in a Category › SubCategory › Layer tree. Bulk-toggle per category.
  - icon: 🔄
    title: Controlled synchronization
    details: Nothing is written to Climweb until you click Synchronize. Manual edits are detected and preserved.
  - icon: ➕
    title: Extensible catalog
    details: Add your own layers manually, import them from a remote WMS GetCapabilities, or load a custom JSON.
---

## Overview

The **Dataset Helper** is a Climweb plugin that helps administrators build the mapviewer's layer catalog without having to create each `Dataset`, `Category`, `SubCategory` and `WmsLayer` by hand in the Wagtail admin.

The plugin ships with a default catalog and provides a UI to:

- enable or disable layers with a single checkbox,
- **synchronize** the selection into the Climweb database (the matching `Dataset` objects are created or removed),
- **extend** the catalog with manually added layers, layers imported from a remote WMS, or layers loaded from a JSON file,
- track **updates** to the bundled catalog when a new version is delivered with the plugin.

## Where to find the plugin

In the Wagtail admin, open the **GeoManager → Dataset helper** menu. The page is split into two tabs:

- **Layer Catalog** — the main working screen (settings, layer tree, synchronization and import actions).
- **Danger Zone** — destructive operations (purge of provisioned data, full wipe).

## Mental model

The plugin maintains its own catalog (`CatalogEntry`) **next to** the Climweb objects. Nothing is written to Climweb until you click **Synchronize with Climweb**.

```
Catalog (CatalogEntry)              Climweb (geomanager)
─────────────────────────           ───────────────────────────
Entry  enabled=true   ──┐
Entry  enabled=true   ──┼── Sync ──►  Category › SubCategory › Dataset › WmsLayer
Entry  enabled=false  ──┘
```

Every entry carries a **state** that summarizes its relationship with Climweb:

| Dot | State              | Meaning                                                                |
|-----|--------------------|------------------------------------------------------------------------|
| 🟢  | `synced`            | Checked and already provisioned in Climweb.                            |
| 🟠  | `pending_add`       | Checked but not yet provisioned — will be created on the next sync.    |
| 🔴  | `pending_remove`    | Unchecked but still in Climweb — will be removed on the next sync.     |
| ⚪  | `disabled`          | Unchecked and absent from Climweb — nothing to do.                     |

## Where to start

If this is your first time, follow the [5-step walkthrough](./getting-started). Otherwise, use the side menu or the search box in the top right.
