---
title: Embedded catalog browser
pageClass: cb-page
outline: false
---

# Embedded catalog browser

This page loads the `catalog.json` shipped with the plugin in the browser and renders it as an interactive tree. You can:

- expand / collapse categories and subcategories,
- open each dataset to inspect its metadata and the list of layers,
- for **WMS** layers, see a `GetMap` thumbnail rendered by the remote server.

::: tip
The WMS thumbnail is built the same way as in the plugin: `EPSG:3857`, world BBOX, 320×240. Layers whose URL still contains an unresolved placeholder (`{country_alpha3}`, `{country_alpha2}`…) are not previewed here, since they are specific to the Climweb instance where the plugin is installed. For private ECMWF layers the `{ECMWF_TOKEN}` placeholder is substituted with `public` (non-public layers may therefore fail).
:::

<CatalogBrowser />
