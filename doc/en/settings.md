# Settings

**Settings** is now its own tab — the first one. It groups the plugin's global settings (a single set of values per Climweb instance) and acts as the gateway to the rest of the plugin: the **Country** is required, and the *Layer Catalog*, *Admin Boundaries* and *Danger Zone* tabs stay **locked** until it is saved.

On a fresh instance the page opens directly on this tab, with the other tabs locked. As soon as you save a valid configuration, the tab unlocks the others and reveals shortcuts to continue with the catalog or the boundaries.

## Language

Language in which the bundled catalog labels will be imported (titles, descriptions, metadata). The bundled catalog is multilingual; this preference just says *which* translation will be copied into the Climweb `Dataset` and `Metadata` at load time.

Possible values: `en`, `fr`, `es`, `pt`, `ar`.

Changing the language **after** a load will not rename the already-created datasets; you have to reload the catalog (`Review embedded catalog` → `Apply`) to propagate the new labels.

## Country *(required)*

The target country of the Climweb instance. Pick it from the dropdown (populated on open).

This value actually stores four related pieces of data:

- **alpha-3** (e.g. `bfa`) — substitutes `{country_alpha3}` in layer URLs.
- **alpha-2** (e.g. `bf`) — substitutes `{country_alpha2}`.
- **official name** (from OpenStreetMap Nominatim) — used for display.
- **bounding box** `[south, north, west, east]` (from Nominatim) — initial map framing.

While `Country` is empty, loading the bundled catalog will reject or skip layers whose URL contains a country placeholder.

## ECMWF Token

Token for the `eccharts.ecmwf.int` WMS service. Private layers in the bundled catalog use URLs like `…?token={ECMWF_TOKEN}`.

- **Empty**: private layers are **skipped** at load time (`skipped_ecmwf_no_token` counter). Public layers (`token=public`) load normally.
- **Filled**: `{ECMWF_TOKEN}` is substituted wherever the placeholder appears.

## Local eStation URL

URL of a local eStation instance, e.g. `https://burkina.example.org/http/c000/w04/climsa/mobile-app`.

- **Empty**: every eStation layer in the catalog is imported.
- **Filled**: the plugin queries the instance and **keeps only** the products it actually serves (`skipped_estation` counter for the rest).

Useful when you deploy Climweb backed by a local eStation that only exposes a subset of the JRC catalog.

## Saving

The **Save Settings** button persists the values and shows a short confirmation message. No side effect on Climweb: settings only propagate on the next load or sync action.


## Next steps

Once the settings are valid, the Settings tab shows two shortcuts:

- **Configure the catalog** — switches to the *Layer Catalog* tab.
- **Configure the boundaries** — switches to the *Admin Boundaries* tab.

They only change tabs; nothing is written until you act there.
