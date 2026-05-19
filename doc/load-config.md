# Charger un fichier JSON

Le bouton **Load Config JSON** sert à deux usages distincts :

1. **Prévisualiser le catalogue embarqué** livré avec le plugin (action *Review embedded catalog*).
2. **Charger un JSON personnalisé** que vous collez dans la zone de texte.

Dans les deux cas, le chargement remplit ou met à jour la table des `CatalogEntry`. **Aucun objet Climweb n'est créé tant que vous n'avez pas cliqué sur *Synchronize with Climweb***.

## Catalogue embarqué (cas standard)

Voir la page dédiée [Mises à jour du catalogue](./updates.md). Le flux normal est :

1. **Review embedded catalog** → vous voyez le diff entre le JSON sur disque et le catalogue en base.
2. **Apply changes** → la table `CatalogEntry` est mise à jour, `CatalogState` mémorise la version.
3. **Synchronize with Climweb** → les `Dataset` Climweb sont créés / supprimés / mis à jour.

## JSON personnalisé

Si vous gérez votre propre fichier de catalogue (en plus ou à la place du catalogue embarqué), collez son contenu dans la zone de texte puis cliquez sur **Load into Catalog**.

Le plugin :

- crée les entrées absentes,
- met à jour celles dont le contenu a changé,
- laisse les autres intactes.

Les entrées créées par cette voie portent l'origine **`config`**, comme celles du catalogue embarqué. Conséquence importante : si vous chargez ensuite le catalogue embarqué, les entrées `config` qui n'apparaissent pas dans le JSON embarqué seront détectées comme **`to remove`** par la prévisualisation. Mélanger plusieurs sources `config` demande donc un peu d'attention.

## Format attendu

Le JSON doit suivre la structure imbriquée **Categories → Subcategories → Datasets → Layers** :

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
                  "default": true
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

Champs racines :

| Champ              | Rôle                                                                            |
|--------------------|----------------------------------------------------------------------------------|
| `version`          | Identifiant de version du catalogue. Utilisé pour détecter les mises à jour.    |
| `schema_version`   | Version du schéma JSON. Incrémentée quand la forme des entrées change.          |
| `categories[]`     | Liste des catégories de plus haut niveau.                                       |

Pour les chaînes multilingues, le catalogue embarqué utilise un dictionnaire `{ "en": "...", "fr": "...", … }`. Le plugin sélectionne la langue configurée dans les [Réglages](./settings.md) au chargement. Une chaîne simple est aussi acceptée.

## Types de couches supportés

Le champ `type` à l'intérieur de `layers[]` peut prendre :

- `wms` — service WMS standard (le plus courant).
- `raster_tile` / `vector_tile` — services de tuiles XYZ ou PMTiles.
- `raster_file` / `vector_file` — fichiers téléchargeables (avec authentification Bearer optionnelle).
- `raster_cog` — Cloud-Optimized GeoTIFF avec gabarit temporel.

Chaque type a ses propres champs (URL de gabarit, intervalle temporel, style raster, configuration de popup…). Référez-vous au catalogue embarqué pour des exemples complets.
