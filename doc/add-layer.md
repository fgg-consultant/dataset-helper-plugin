# Ajouter une couche manuellement

Le bouton **+ Add Layer** (barre d'outils du *Layer Catalog*) ouvre un formulaire pour insérer dans le catalogue une couche qui n'est pas dans le catalogue embarqué et qui ne provient pas d'un import WMS.

Les couches ajoutées par ce biais portent l'origine **`manual`** : elles ne sont jamais touchées par les mises à jour du catalogue embarqué et restent dans le catalogue tant que vous ne les supprimez pas.

## Champs

| Champ              | Obligatoire | Description                                                                 |
|--------------------|:-----------:|-----------------------------------------------------------------------------|
| **Category**       | ✔           | Titre de la catégorie. Crée la catégorie si elle n'existe pas, sinon y rattache la nouvelle couche. |
| **Subcategory**    | ✔           | Idem au niveau sous-catégorie.                                              |
| **Title**          |             | Libellé affiché. Si vide, l'identifiant de couche WMS est utilisé.          |
| **WMS Layer Name** | ✔           | Identifiant exact de la couche tel qu'il apparaît dans le GetCapabilities WMS (paramètre `LAYERS`). |
| **WMS Base URL**   | ✔           | URL de base du service WMS, sans les paramètres de requête.                 |
| **Source**         |             | Producteur / organisme à l'origine de la donnée. Recopié dans `Metadata`.   |
| **Resolution**     |             | Résolution spatiale (`1km`, `0.05deg`, etc.). Recopié dans `Metadata`.      |

Cliquez sur **Add** : l'entrée est créée immédiatement dans le catalogue avec l'état `pending_add` 🟠. Elle apparaît dans l'arbre dans la catégorie et sous-catégorie indiquées.

## Étape suivante

Cliquez sur **Synchronize with Climweb** pour provisionner réellement la couche.

## Modifier ou supprimer une couche ajoutée

Une couche `manual` se gère comme n'importe quelle entrée du catalogue :

- la **désactiver** (décocher) la marquera `pending_remove` ; la prochaine synchro supprimera le `Dataset` côté Climweb.
- la **réactiver** la remet en `pending_add` ; la prochaine synchro la recréera.

Pour modifier l'URL ou les paramètres, le plus simple reste de désactiver l'ancienne et d'en ajouter une nouvelle. L'édition fine d'un `Dataset` provisionné se fait directement dans l'admin Wagtail (mais elle sera considérée comme *local drift* — voir [Mises à jour](./updates.md)).
