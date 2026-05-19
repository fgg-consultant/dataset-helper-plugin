---
title: Explorar o catálogo embarcado
pageClass: cb-page
outline: false
---

# Explorar o catálogo embarcado

Esta página carrega no navegador o arquivo `catalog.json` entregue com o plugin e o exibe como uma árvore interativa. Você pode:

- expandir / recolher as categorias e subcategorias,
- abrir cada dataset para ver seus metadados e a lista de camadas,
- para as camadas **WMS**, ver uma miniatura `GetMap` gerada pelo servidor remoto.

::: tip
A miniatura WMS é construída da mesma forma que no plugin: `EPSG:3857`, BBOX mundial, 320×240. As camadas cuja URL contém um marcador não resolvido (`{country_alpha3}`, `{country_alpha2}`…) não têm pré-visualização aqui, pois são específicas da instância Climweb onde o plugin é instalado. Para as camadas ECMWF privadas, o marcador `{ECMWF_TOKEN}` é substituído por `public` (camadas não públicas podem falhar).
:::

<CatalogBrowser />
