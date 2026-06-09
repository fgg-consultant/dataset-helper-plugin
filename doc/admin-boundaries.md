# Limites administratives

L'onglet **Admin Boundaries** initialise la couche des limites administratives de Climweb à partir des **Common Operational Datasets de l'OCHA (COD-AB)** publiés sur [HDX](https://data.humdata.org/). Cette fonctionnalité est indépendante du catalogue de couches WMS : elle alimente le *boundary manager* de Climweb, qui sert les limites en **tuiles vectorielles (MVT)**.

## Prérequis

- Le **pays** doit être renseigné dans les [réglages du plugin](./settings.md) (onglet *Settings*). Les codes ISO alpha-2 et alpha-3 servent à localiser et filtrer les données.
- L'instance Climweb doit embarquer le *boundary manager* (`adminboundarymanager`) et `geopandas`. Sinon, un avertissement s'affiche et le bouton d'import est désactivé.

## Importer les limites

Cliquez sur **Import boundaries from OCHA**. Le plugin enchaîne automatiquement :

1. **Localisation** du jeu de données COD-AB sur HDX via l'API CKAN (`cod-ab-<iso3>`) et choix de l'archive shapefile (`*.shp.zip`).
2. **Téléchargement** de l'archive globale (elle contient un shapefile par niveau administratif).
3. **Extraction** et détection des niveaux (`adm0`, `adm1`, …) ; les couches de lignes, points et chefs-lieux sont ignorées.
4. **Normalisation des colonnes** de chaque niveau vers le schéma attendu par le boundary manager (`ADM{n}_EN`/`ADM{n}_FR` et `ADM{n}_PCODE`), reprojection en EPSG:4326, et alignement de `ADM0_PCODE` sur le code pays.
5. **Ré-archivage par niveau** puis **chargement** de chaque niveau dans le boundary manager.

> Le pays est d'abord enregistré dans les réglages du boundary manager, faute de quoi ses signaux supprimeraient les lignes insérées.

À la fin, un panneau résume le nombre d'entités chargées par niveau :

```
Boundaries imported: 4 level(s), 416 features
```

## Niveaux chargés

Le tableau **Loaded admin levels** indique le nombre d'entités présentes par niveau pour le pays configuré :

| Niveau | Contenu typique |
|--------|-----------------|
| 0 | Pays |
| 1 | Régions |
| 2 | Provinces / départements |
| 3 | Communes |
| 4 | (selon le pays) |

## Aperçu cartographique

La carte en bas de l'onglet affiche les limites servies par le boundary manager en tuiles vectorielles :

```
/api/admin-boundary/tiles/{z}/{x}/{y}
```

Elle se recentre automatiquement sur l'emprise du pays. Après un import, la carte se rafraîchit pour montrer les données fraîchement chargées.

## Ré-import et suppression

- **Ré-importer** est idempotent : pour chaque niveau, les limites précédemment chargées pour ce pays sont remplacées.
- **Clear boundaries** supprime toutes les limites du pays configuré (tous niveaux). Action irréversible.

## Source des données

La source est **OCHA COD-AB** (Common Operational Datasets – Administrative Boundaries), les limites administratives de référence utilisées par les agences humanitaires, publiées sur HDX.
