---
title: Explorer le catalogue embarqué
pageClass: cb-page
outline: false
---

# Explorer le catalogue embarqué

Cette page charge en clair le fichier `catalog.json` livré avec le plugin et le restitue sous forme d'arbre interactif. Vous pouvez :

- déplier / replier les catégories et sous-catégories,
- ouvrir chaque jeu de données pour voir ses métadonnées et la liste des couches,
- pour les couches **WMS**, voir une vignette `GetMap` rendue par le serveur distant.

::: tip
La vignette WMS est générée comme dans le plugin : `EPSG:3857`, BBOX monde, taille 320×240. Les couches dont l'URL contient un placeholder non résolu (`{country_alpha3}`, `{country_alpha2}`…) n'ont pas de vignette ici, puisqu'elles sont propres à l'instance Climweb dans laquelle le plugin est installé. Pour les couches ECMWF privées, le placeholder `{ECMWF_TOKEN}` est remplacé par `public` (les couches non publiques peuvent donc échouer).
:::

<CatalogBrowser />
