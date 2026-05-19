# Zone dangereuse

L'onglet **Danger Zone** et le bouton **Reset Catalog** de la barre d'outils regroupent les actions **destructives**. Toutes sont irréversibles ; lisez attentivement avant de cliquer.

## Reset Catalog

Bouton rouge dans la barre d'outils du *Layer Catalog*. Cette action :

1. **Supprime tous les `Dataset` Climweb provisionnés par le plugin** (et seulement ceux-là : les datasets créés hors plugin sont préservés).
2. Supprime les `Metadata` associées.
3. Balaie les `SubCategory` et `Category` devenues vides.
4. **Vide entièrement la table `CatalogEntry`** (entrées `config`, `manual` et `wms_import` confondues).
5. Remet `CatalogState` à zéro — le plugin oublie quelle version du catalogue était chargée.

Effet net : le plugin se retrouve dans l'état du premier lancement, et seules les données Climweb créées hors plugin survivent.

**Quand l'utiliser :**

- Pour repartir d'une feuille blanche avant de recharger un catalogue différent.
- Après une mauvaise manipulation pendant la phase de mise en place.

**Quand ne pas l'utiliser :**

- En production, sur un Climweb qui sert des utilisateurs. Préférez désactiver sélectivement les couches et synchroniser.

## Clear catalog-managed datasets

Bouton dans l'onglet *Danger Zone*. Variante moins agressive de *Reset Catalog* :

1. Supprime les `Dataset` Climweb provisionnés par le plugin (idem que ci-dessus).
2. Supprime les `Metadata` associées.
3. Balaie les taxonomies vides.
4. **Conserve** la table `CatalogEntry` : les entrées sont simplement remises à `pending_add` 🟠.

Effet net : Climweb est nettoyé côté plugin, mais votre sélection (quelles couches sont cochées, vos ajouts manuels…) est intacte. Cliquer ensuite sur **Synchronize with Climweb** recrée tout depuis zéro avec votre sélection actuelle.

**Cas d'usage typique :** résoudre une dérive durable du contenu côté Climweb (titres édités à la main, anciennes versions des couches que vous voulez ré-écraser proprement).

## Clear All Datasets & Categories

Bouton rouge en bas de l'onglet *Danger Zone*. **Nucléaire** :

- Supprime **tous** les `Dataset`, `SubCategory` et `Category` du geomanager Climweb, qu'ils viennent du plugin ou non.
- Supprime tous les `WmsLayer`, `WmsRequestLayer`, `RasterStyle`, `Metadata`.
- Met à zéro les `dataset_id` des `CatalogEntry`.

Effet net : le mapviewer Climweb n'a plus aucune couche.

**À n'utiliser que si vous comprenez exactement ce que vous faites** — par exemple lors d'une reprise complète d'environnement.

## Tableau récapitulatif

| Action                              | `CatalogEntry` plugin | `Dataset` plugin | `Dataset` hors plugin | `Category` / `SubCategory` |
|-------------------------------------|:---------------------:|:----------------:|:---------------------:|:--------------------------:|
| Décocher + Synchronize              | conservées            | supprimés        | conservés             | conservées si non vides    |
| Clear catalog-managed datasets      | conservées (`pending_add`) | supprimés    | conservés             | sweep si vides             |
| Reset Catalog                       | supprimées            | supprimés        | conservés             | sweep si vides             |
| Clear All Datasets & Categories     | `dataset_id` effacé   | supprimés        | **supprimés**         | **supprimés**              |
