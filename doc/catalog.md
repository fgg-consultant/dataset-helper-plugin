# Le catalogue de couches

L'onglet **Layer Catalog** est l'écran principal du plugin. Il affiche l'arbre des couches **Category › SubCategory › Layer** et permet de piloter ce qui sera provisionné dans Climweb.

## Compteurs

En haut de page, trois compteurs résument l'état du catalogue :

- **Total Layers** — nombre total de `CatalogEntry`, toutes origines confondues.
- **Enabled** — entrées cochées (qui seront ou sont déjà dans Climweb).
- **Synced** — entrées effectivement provisionnées dans Climweb.

L'écart entre *Enabled* et *Synced* est ce qui sera modifié à la prochaine synchro.

## Statuts d'une couche

Chaque ligne de couche affiche une pastille colorée :

| Pastille | Statut          | Signification                                                    |
|----------|-----------------|------------------------------------------------------------------|
| 🟢       | `synced`         | Cochée et provisionnée dans Climweb.                            |
| 🟠       | `pending_add`    | Cochée mais pas encore provisionnée.                            |
| 🔴       | `pending_remove` | Décochée mais encore présente dans Climweb.                     |
| ⚪       | `disabled`       | Décochée et absente de Climweb.                                  |

C'est le passage à **Synchronize with Climweb** qui résorbe les états orange et rouge.

## Naviguer dans l'arbre

L'arbre est entièrement repliable. Trois interactions principales :

- Cliquer sur l'en-tête d'une **catégorie** ou d'une **sous-catégorie** la déplie / replie.
- Les boutons ▼ et ▶ en haut de l'arbre déplient ou replient **tout** l'arbre.
- Cliquer sur la ligne d'une couche ouvre / referme son **panneau de détails** (URL WMS, identifiant de couche, métadonnées sources…).

## Cocher / décocher

- **Une couche** : la case à cocher à gauche du titre active ou désactive cette entrée.
- **Une sous-catégorie** : la case dans l'en-tête bascule **toutes les couches** de la sous-catégorie en une fois (bulk toggle).
- **Une catégorie** : idem, mais sur l'ensemble des couches de la catégorie.

L'effet est immédiat côté plugin (le statut passe à `pending_add`/`pending_remove`) mais **rien n'est encore écrit côté Climweb**. Il faut cliquer sur **Synchronize with Climweb**.

## Origine d'une couche

Chaque entrée porte une **origine** qui décrit comment elle est arrivée dans le catalogue :

| Origine      | Comment elle est apparue                                                    |
|--------------|------------------------------------------------------------------------------|
| `config`     | Chargée depuis le catalogue JSON embarqué (ou un JSON importé manuellement). |
| `manual`     | Ajoutée via le formulaire *+ Add Layer*.                                     |
| `wms_import` | Importée depuis un GetCapabilities WMS distant.                              |

L'origine compte surtout pour les **mises à jour** du catalogue embarqué : seules les entrées `config` peuvent être déclarées `to_remove` quand elles disparaissent d'une nouvelle version du JSON. Les entrées `manual` et `wms_import` ne sont jamais touchées par les mises à jour automatiques.

## Actions de la barre d'outils

Sous le panneau de réglages, la barre d'outils regroupe les actions principales :

- **Synchronize with Climweb** — applique la sélection actuelle (voir [Synchroniser](./sync.md)).
- **+ Add Layer** — ajoute manuellement une couche (voir [Ajouter une couche](./add-layer.md)).
- **Import from WMS** — pioche des couches dans un GetCapabilities distant (voir [Importer depuis un WMS](./import-wms.md)).
- **Load Config JSON** — charge un fichier JSON ou prévisualise le catalogue embarqué (voir [Charger un JSON](./load-config.md) et [Mises à jour](./updates.md)).
- **Reset Catalog** — opération **destructive** ; voir [Zone dangereuse](./danger-zone.md).
