# Synchroniser avec Climweb

Le bouton **Synchronize with Climweb** (barre d'outils du *Layer Catalog*) propage l'état actuel du catalogue vers la base Climweb. C'est la seule action qui crée ou supprime réellement des `Dataset` côté geomanager.

## Ce que fait la synchro

Le plugin parcourt toutes les entrées et agit en fonction de leur statut :

| Statut             | Action                                                                                         |
|--------------------|------------------------------------------------------------------------------------------------|
| `pending_add` 🟠    | Provisionne dans Climweb : crée/réutilise `Category` et `SubCategory`, crée `Dataset`, `Metadata`, puis les objets de couche (`WmsLayer`, `WmsRequestLayer`, etc. selon le type). |
| `pending_remove` 🔴 | Déprovisionne : supprime le `Dataset` (et ses dépendances) côté Climweb, libère `dataset_id`. |
| `synced` 🟢         | Vérifie que le `Dataset` existe encore. Si le contenu du catalogue a bougé depuis la dernière sync, **re-provisionne** (le titre, l'URL ou les métadonnées sont mis à jour). |
| `disabled` ⚪       | Rien à faire.                                                                                   |

À la fin, un panneau de résultats résume la passe :

```
Sync complete: 12 added, 3 removed, 5 updated, 0 orphans cleared
```

## Cas particuliers

### Orphelins

Si une entrée est marquée `synced` mais que le `Dataset` Climweb a été supprimé entre-temps (par exemple via l'admin Wagtail), elle est détectée comme **orpheline** : `dataset_id` est remis à `null` et l'entrée repasse à `pending_add`. Une seconde sync la recréera.

Le compteur **orphans cleared** dans le panneau de résultats reflète ces réconciliations.

### Catégories et sous-catégories partagées

Le plugin **ne supprime jamais** une `Category` ou `SubCategory` qui contient encore des `Dataset` non gérés par le plugin. Si vous avez créé manuellement un dataset dans une catégorie qu'utilise aussi le plugin, déprovisionner les entrées du plugin n'effacera pas la catégorie.

Les catégories vides sont en revanche balayées en fin de cycle (voir [Zone dangereuse](./danger-zone.md)).

### Couches de type `raster_file`

Les couches `raster_file` (fichiers raster téléchargés et stockés dans Climweb) **ne sont pas re-provisionnées** automatiquement quand le catalogue change : ré-écraser détruirait les fichiers déjà téléversés. Le plugin signale ce cas via le compteur `raster_file drift` et laisse l'objet Climweb intact. Pour appliquer le nouveau contenu, supprimez l'entrée et recréez-la (ou videz les couches puis re-synchronisez).

## Que faire après la synchro

Après une sync réussie, les couches sont visibles dans le mapviewer Climweb. Côté plugin :

- toutes les entrées cochées sont à `synced`,
- toutes les entrées décochées sont à `disabled`.

Vous pouvez retoucher la sélection à tout moment et re-cliquer **Synchronize with Climweb** : seule la différence depuis la dernière sync sera appliquée.
