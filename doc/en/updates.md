# Catalog updates

The plugin ships a `catalog.json` file that describes the layers delivered by default. This file carries a `version` (e.g. `2026.05.18`). When a new version of the plugin is deployed, that version changes and the plugin knows that a **catalog update** is available.

## The update banner

When the on-disk version differs from the loaded version, a banner appears at the top of the *Layer Catalog* tab:

> A new catalog version is available — vX.  *(with a one-line summary: N new · N updated · N conflicts · N removed)*

Clicking **Review changes** opens the preview; **Later** dismisses the banner for the session. **Nothing is written to the database** at this stage.

## The changeset

The preview classifies each entry of the new catalog into a **bucket** and shows the counters at the top:

| Bucket          | Meaning                                                                                       |
|-----------------|-----------------------------------------------------------------------------------------------|
| **new**         | Entries present in the new catalog, absent from the database.                                  |
| **updated**     | Source content changed (title, URL, metadata…) and **nothing was manually edited** on the Climweb side. Safe to apply. |
| **local drift** | Source content unchanged, but the Climweb `Dataset` was **manually edited** through the Wagtail admin. The plugin will not touch it. |
| **conflict**    | Source content **did change** AND the Climweb `Dataset` was edited by hand. Decision required. |
| **to remove**   | Entries of origin `config` present in the database but **missing** from the new version of the catalog. They will be flagged disabled. |
| **unchanged**   | Nothing to do.                                                                                 |

Each bucket is collapsible and lists the affected entries (title + location in the hierarchy).

## Applying the changeset

Up to two buttons are offered depending on what the changeset contains:

- **Apply — keep N local edits** *(default when there are conflicts)* — applies all changes **except** the conflicts. Hand-made changes in the Wagtail admin are preserved; conflicting entries remain in `local drift` until your next decision.
- **Apply — overwrite N conflicts** — applies everything, including conflicts. Manual changes are **overwritten** by the catalog content.
- **Cancel** — closes the preview, do nothing.

If there are **no conflicts**, a single **Apply changes** button is enough.

::: tip
The preview is strictly read-only. You can open it, close it, reopen it as many times as needed without risk.
:::

## What applying actually does

Applying the changeset updates the `CatalogEntry` table (and `CatalogState` to remember the newly loaded version). It does **not** provision the new datasets or remove existing Climweb datasets — that is the job of **Synchronize with Climweb**:

```
1. Review changes   → updates the plugin catalog (CatalogEntry)
2. Synchronize      → propagates the selection to Climweb (Dataset)
```

Concretely, after an *Apply*:

- **new** entries appear as `pending_add` 🟠 in the tree,
- **updated** entries stay `synced` 🟢 but their source content is refreshed — the next sync will re-provision the `Dataset`,
- **to remove** entries flip to `pending_remove` 🔴 — the next sync removes them from Climweb,
- **local drift** entries are left as-is (your manual edits remain until you click `overwrite`).

## When to click Synchronize?

Right after *Apply*. Without a sync, Climweb keeps serving the old content for the affected layers.
