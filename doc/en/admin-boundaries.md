# Administrative boundaries

The **Admin Boundaries** tab bootstraps Climweb's administrative boundaries layer from the **OCHA Common Operational Datasets (COD-AB)** published on [HDX](https://data.humdata.org/). This feature is independent of the WMS layer catalog: it feeds Climweb's *boundary manager*, which serves the boundaries as **vector tiles (MVT)**.

## Prerequisites

- The **country** must be set in the [plugin settings](./settings.md) (*Settings* tab). The ISO alpha-2 and alpha-3 codes are used to locate and filter the data.
- The Climweb instance must ship the *boundary manager* (`adminboundarymanager`) and `geopandas`. Otherwise a warning is shown and the import button is disabled.

## Importing boundaries

Click **Import boundaries from OCHA**. The plugin runs the whole pipeline automatically:

1. **Locate** the COD-AB dataset on HDX via the CKAN API (`cod-ab-<iso3>`) and pick the shapefile archive (`*.shp.zip`).
2. **Download** the global archive (it bundles one shapefile per admin level).
3. **Extract** and detect the levels (`adm0`, `adm1`, …); line, point and capital layers are skipped.
4. **Normalize the columns** of each level to the schema the boundary manager expects (`ADM{n}_EN`/`ADM{n}_FR` and `ADM{n}_PCODE`), reproject to EPSG:4326, and align `ADM0_PCODE` with the country code.
5. **Re-zip per level** then **load** each level into the boundary manager.

> The country is registered in the boundary manager settings first, otherwise its signals would purge the inserted rows.

When it finishes, a panel summarizes how many features were loaded per level:

```
Boundaries imported: 4 level(s), 416 features
```

## Loaded levels

The **Loaded admin levels** table shows how many features exist per level for the configured country:

| Level | Typical content |
|-------|-----------------|
| 0 | Country |
| 1 | Regions |
| 2 | Provinces / departments |
| 3 | Communes |
| 4 | (country-dependent) |

## Map preview

The map at the bottom of the tab shows the boundaries served by the boundary manager as vector tiles:

```
/api/admin-boundary/tiles/{z}/{x}/{y}
```

It auto-centers on the country's bounding box. After an import, the map refreshes to show the freshly loaded data.

## Re-import and clearing

- **Re-importing** is idempotent: for each level, the boundaries previously loaded for this country are replaced.
- **Clear boundaries** deletes every boundary for the configured country (all levels). This cannot be undone.

## Data source

The source is **OCHA COD-AB** (Common Operational Datasets – Administrative Boundaries), the reference administrative boundaries used by humanitarian agencies, published on HDX.
