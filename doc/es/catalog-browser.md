---
title: Explorar el catálogo incluido
pageClass: cb-page
outline: false
---

# Explorar el catálogo incluido

Esta página carga en el navegador el archivo `catalog.json` entregado con el plugin y lo presenta como un árbol interactivo. Puede:

- expandir / colapsar las categorías y subcategorías,
- abrir cada dataset para ver sus metadatos y la lista de capas,
- para las capas **WMS**, ver una miniatura `GetMap` generada por el servidor remoto.

::: tip
La miniatura WMS se construye de la misma forma que en el plugin: `EPSG:3857`, BBOX mundial, 320×240. Las capas cuya URL contiene un marcador sin resolver (`{country_alpha3}`, `{country_alpha2}`…) no tienen vista previa aquí, ya que son específicas a la instancia de Climweb donde se instala el plugin. Para las capas ECMWF privadas, el marcador `{ECMWF_TOKEN}` se sustituye por `public` (las capas no públicas pueden fallar).
:::

<CatalogBrowser />
