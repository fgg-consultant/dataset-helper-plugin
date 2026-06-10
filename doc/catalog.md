# Le catalogue de couches

L'onglet **Layer Catalog** est l'écran principal du plugin. Il affiche l'arbre **Category › SubCategory › Layer** et permet de piloter ce qui sera provisionné dans Climweb.

En haut de l'onglet, un en-tête rappelle le contexte — *GeoManager · Layer catalog for the Climweb map viewer* — avec une pastille indiquant la version du catalogue actuellement chargée (ou *not loaded*) et un lien vers cette documentation.

## Vue d'ensemble

Une carte en haut de page résume l'état du catalogue.

Trois compteurs :

- **Catalog layers** — nombre total de `CatalogEntry`, toutes origines confondues.
- **Enabled** — entrées cochées (celles qui seront ou sont déjà dans Climweb).
- **Synced** — entrées effectivement provisionnées dans Climweb.

Une **jauge de statut** décompose ensuite le catalogue par état — **Synced**, **To add**, **To remove**, **Disabled** — avec une légende colorée, pour voir d'un coup d'œil l'écart entre le catalogue et Climweb.

Une ligne discrète rappelle la version chargée : *Catalog vX · loaded DATE*.

## État de synchronisation

Le plugin indique immédiatement si Climweb est aligné avec votre sélection locale :

- **In sync** — rien n'est affiché ; Climweb reflète exactement votre catalogue.
- **Out of sync** — un bandeau bien visible apparaît juste sous la vue d'ensemble : *Catalog out of sync with Climweb — N pending changes — X to create, Y to remove, Z to update*, accompagné d'un bouton **Synchronize with Climweb**.

Après l'exécution d'une synchro (ou d'un chargement / reset), le **résultat** s'affiche au même endroit, dans le même style — vert en cas de succès, rouge en cas d'erreur — avec un **×** vert pour le masquer.

## Statut d'une couche

Chaque ligne de couche affiche une pastille colorée :

| Pastille | Statut              | Signification                                                    |
|----------|---------------------|------------------------------------------------------------------|
| 🟢       | `synced`             | Cochée et provisionnée dans Climweb.                            |
| 🟠       | `pending_add`        | Cochée mais pas encore provisionnée.                            |
| 🔴       | `pending_remove`     | Décochée mais encore présente dans Climweb.                     |
| ⚪       | `disabled`           | Décochée et absente de Climweb.                                  |

Seul **Synchronize with Climweb** résorbe les états orange et rouge.

## Naviguer dans l'arbre

Une barre de contrôle se trouve au-dessus de l'arbre : un **champ de recherche**, des **puces de filtre par statut**, des boutons **select-all / deselect-all** et des boutons **tout déplier / tout replier**.

L'arbre est entièrement repliable. Trois interactions principales :

- Cliquer sur l'en-tête d'une **catégorie** ou d'une **sous-catégorie** la déplie / replie.
- Les boutons déplier / replier (en haut à droite de la barre de contrôle) ouvrent ou ferment **toutes** les catégories et sous-catégories d'un coup.
- Cliquer sur la ligne d'une couche ouvre / referme son **panneau de détails** (nom de la couche, URL du service, fournisseur, résolution, fréquence, origine, ainsi que les options Climweb — popup, légende WMS, multi-temporel, visible au départ, temps quasi réel — plus un aperçu GetMap).

Chaque ligne affiche, d'un coup d'œil : une **case à cocher** à trois états, une **pastille de statut** colorée, le **nom** de la couche, et des **badges** pour le fournisseur, le type de couche et (pour les entrées héritées) l'origine. Chaque en-tête de catégorie porte aussi une petite **mini-barre de statut** qui résume ses couches.

## Rechercher et filtrer

La barre de contrôle au-dessus de l'arbre permet de restreindre ce qui est affiché — entièrement côté client, rien n'est envoyé au serveur :

- **Champ de recherche** — tapez pour ne conserver que les couches dont le nom, l'identifiant de couche, le fournisseur, la catégorie ou la sous-catégorie correspond. Les catégories et sous-catégories correspondantes se déplient automatiquement. Effacez-le avec le bouton **×** ou la touche **Esc**.
- **Puces de filtre** — **All**, **To add**, **To remove**, **Disabled** restreignent l'arbre aux couches dans cet état. Les puces affichent un compteur en direct pour chaque état en attente.

Tant qu'une recherche ou un filtre est actif, seules les branches correspondantes sont affichées et dépliées ; les effacer replie l'arbre vers votre état de dépliage / repliage précédent. Si rien ne correspond, l'arbre affiche *No layer matches your search.*

## Cocher / décocher

- **Une seule couche** : la case à cocher à gauche du titre active ou désactive cette entrée.
- **Une sous-catégorie** : la case dans son en-tête bascule **toutes les couches** de la sous-catégorie en une fois (bulk toggle).
- **Une catégorie** : idem, mais sur l'ensemble de la catégorie.
- **Tout le catalogue** : les boutons **select-all** / **deselect-all** de la barre de contrôle activent ou désactivent *toutes* les couches en une fois.

L'effet est immédiat côté plugin (le statut passe à `pending_add` / `pending_remove`) mais **rien n'est encore écrit côté Climweb**. Le bandeau out-of-sync apparaît alors — cliquez sur **Synchronize with Climweb** pour appliquer.

## Origine d'une couche

Chaque entrée porte une **origine** qui décrit comment elle est arrivée dans le catalogue :

| Origine      | Comment elle est apparue                                                        |
|--------------|----------------------------------------------------------------------------------|
| `config`     | Chargée depuis le catalogue JSON embarqué. C'est la seule origine créée aujourd'hui. |
| `manual` / `wms_import` | Origines héritées de versions antérieures du plugin (ajout manuel / import WMS). Ces parcours ont été supprimés ; de telles entrées peuvent encore exister sur d'anciennes instances. |

L'origine compte surtout pour les **mises à jour** du catalogue embarqué : seules les entrées `config` peuvent être déclarées `to_remove` lorsqu'elles disparaissent d'une nouvelle version du catalogue. Les entrées héritées `manual` / `wms_import` ne sont jamais touchées par les mises à jour automatiques.

## Catalogue vide

Tant qu'aucun catalogue n'a été chargé, l'onglet n'affiche **qu'un** bloc d'avertissement — *No catalog loaded yet* — avec un bouton **Load catalog**. Cliquer dessus charge le catalogue embarqué **directement** (pas de prévisualisation, puisqu'il n'y a rien avec quoi entrer en conflit). La vue d'ensemble et l'arbre apparaissent alors. Voir [Premiers pas](./getting-started).

## Barre d'outils

Une fois un catalogue chargé, une seule action subsiste dans la barre d'outils :

- **Reset Catalog** — opération **destructive** ; voir [Zone dangereuse](./danger-zone).

Le chargement et la synchronisation sont pilotés par les bandeaux décrits plus haut plutôt que par des boutons de la barre d'outils :

- le bouton **Load catalog** (état vide) ou le **Review changes** du bandeau de mise à jour (voir [Mises à jour du catalogue](./updates)) remplissent le catalogue,
- le bouton **Synchronize with Climweb** (bandeau out-of-sync) propage la sélection vers Climweb (voir [Synchroniser](./sync)).
