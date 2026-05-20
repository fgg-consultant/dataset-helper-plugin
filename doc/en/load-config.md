# Load a JSON file

The **Load Config JSON** button serves two distinct purposes:

1. **Preview the bundled catalog** shipped with the plugin (*Review embedded catalog* action).
2. **Load a custom JSON** that you paste into the text area.

In both cases, loading populates or updates the `CatalogEntry` table. **No Climweb object is created until you click *Synchronize with Climweb***.

## Bundled catalog (standard case)

See the dedicated page [Catalog updates](./updates). The normal flow is:

1. **Review embedded catalog** → see the diff between the on-disk JSON and the database catalog.
2. **Apply changes** → the `CatalogEntry` table is updated, `CatalogState` remembers the version.
3. **Synchronize with Climweb** → Climweb `Dataset` objects are created / removed / updated.

## Custom JSON

If you maintain your own catalog file (in addition to or instead of the bundled catalog), paste its content in the text area and click **Load into Catalog**.

The plugin:

- creates missing entries,
- updates those whose content changed,
- leaves the rest alone.

Entries created via this path carry the origin **`config`**, just like the bundled-catalog ones. Important consequence: if you later load the bundled catalog, `config` entries that do not appear in the bundled JSON will be flagged as **`to remove`** by the preview. Mixing multiple `config` sources thus requires care.

## Expected format

The JSON must follow the nested **Categories → Subcategories → Datasets → Layers** structure:

```json
{
  "version": "2026.05.18",
  "schema_version": 1,
  "categories": [
    {
      "title": "Rainfall",
      "icon": "raindrops",
      "subcategories": [
        {
          "title": "Observation",
          "datasets": [
            {
              "title": "10-day precipitation estimate",
              "description": "...",
              "multi_temporal": true,
              "public": true,
              "metadata": {
                "function": "...",
                "resolution": "0.05deg",
                "source": "JRC eStation",
                "geographic_coverage": "Africa",
                "license": "Open Data",
                "frequency_of_update": "Dekadal",
                "overview": "...",
                "learn_more": "https://..."
              },
              "layers": [
                {
                  "type": "wms",
                  "title": "RFE 10-day",
                  "layer_name": "rfe_10d",
                  "wms_url": "https://example.org/wms",
                  "default": true,
                  "popup": true,
                  "legend_from_capabilities": true
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Root fields:

| Field              | Role                                                                            |
|--------------------|---------------------------------------------------------------------------------|
| `version`          | Catalog version identifier. Used to detect updates.                              |
| `schema_version`   | JSON schema version. Bumped when the shape of entries changes.                   |
| `categories[]`     | List of top-level categories.                                                    |

For multilingual strings, the bundled catalog uses a `{ "en": "...", "fr": "...", … }` dictionary. The plugin picks the language configured in [Settings](./settings) at load time. A plain string is also accepted.

## Supported layer types

The `type` field inside `layers[]` accepts:

- `wms` — standard WMS service (the most common).
- `raster_tile` / `vector_tile` — XYZ or PMTiles tile services.
- `raster_file` / `vector_file` — downloadable files (with optional Bearer authentication).
- `raster_cog` — Cloud-Optimized GeoTIFF with a time template.

Each type has its own fields (URL template, time range, raster style, popup configuration…). Refer to the bundled catalog for complete examples.

### WMS-specific fields

For `wms` layers, two boolean options control what gets enabled on the Climweb side:

| Field                       | Default | Effect on the Climweb `WmsLayer`                                                                  |
|-----------------------------|---------|---------------------------------------------------------------------------------------------------|
| `popup`                     | `false` | Toggles **Enable popup** — a popup is shown when the user clicks the layer.                       |
| `legend_from_capabilities`  | `false` | Toggles **Load legend from WMS capabilities** — the legend is read from the GetCapabilities `<LegendURL>`. |

Both are opt-in and must be set explicitly per layer. On every resync, the JSON value overwrites the Climweb-side value.
