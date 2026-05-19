# Mises à jour du catalogue embarqué

Le plugin embarque un fichier `catalog.json` qui décrit l'ensemble des couches livrées par défaut. Ce fichier porte une `version` (par exemple `2026.05.18`). Quand une nouvelle version du plugin est déployée, cette version change, et le plugin sait alors qu'une **mise à jour du catalogue** est disponible.

## Le bandeau de mise à jour

Si la version sur disque diffère de la version chargée en base, un bandeau apparaît en haut de l'onglet *Layer Catalog* :

> A new catalog version is available — review changes

Cliquer sur **Review changes** ouvre la pré-visualisation. **Rien n'est encore écrit en base** à ce stade.

Vous pouvez aussi déclencher la pré-visualisation manuellement : **Load Config JSON → Review embedded catalog**.

## Le changeset

La pré-visualisation classe chaque entrée du nouveau catalogue dans un **bucket** et affiche les compteurs en haut :

| Bucket          | Sens                                                                                          |
|-----------------|-----------------------------------------------------------------------------------------------|
| **new**         | Entrées présentes dans le nouveau catalogue, absentes de la base.                              |
| **updated**     | Le contenu d'origine a changé (titre, URL, métadonnées…) et **rien n'a été modifié à la main** côté Climweb. Application sûre. |
| **local drift** | Le contenu d'origine est inchangé mais le `Dataset` Climweb a été **édité manuellement** dans l'admin Wagtail. Le plugin ne touchera à rien. |
| **conflict**    | Le contenu d'origine **a changé** ET le `Dataset` Climweb a été édité à la main. Décision requise. |
| **to remove**   | Entrées d'origine `config` présentes en base mais **absentes** de la nouvelle version du catalogue. Elles seront marquées désactivées. |
| **unchanged**   | Rien à faire.                                                                                  |

Chaque bucket est déroulant et liste les entrées concernées (titre + emplacement dans la hiérarchie).

## Appliquer le changeset

Deux boutons sont proposés selon ce que contient le changeset :

- **Apply — keep N local edits** *(par défaut quand il y a des conflits)* — applique tous les changements **sauf** les conflits. Les modifications faites à la main dans l'admin Wagtail sont préservées ; les entrées conflictuelles restent en `local drift` jusqu'à votre prochaine décision.
- **Apply — overwrite N conflicts** — applique tout, y compris les conflits. Les modifications manuelles sont **écrasées** par le contenu du catalogue.
- **Cancel** — referme la pré-visualisation, ne rien faire.

S'il n'y a **aucun conflit**, un simple bouton **Apply changes** suffit.

::: tip
La pré-visualisation est strictement en lecture. Vous pouvez l'ouvrir, la fermer, la rouvrir autant de fois que nécessaire sans risque.
:::

## Ce que l'application modifie

L'application du changeset met à jour la table `CatalogEntry` (et `CatalogState` pour mémoriser la nouvelle version chargée). Elle **ne provisionne pas** les nouveaux datasets ni ne supprime les datasets Climweb existants — c'est la responsabilité de **Synchronize with Climweb** :

```
1. Review changes   → met à jour le catalogue plugin (CatalogEntry)
2. Synchronize      → propage la sélection vers Climweb (Dataset)
```

Concrètement, après un *Apply* :

- les **new** apparaissent comme `pending_add` 🟠 dans l'arbre,
- les **updated** restent `synced` 🟢 mais leur contenu d'origine est rafraîchi — la prochaine sync re-provisionnera le `Dataset`,
- les **to remove** passent à `pending_remove` 🔴 — la prochaine sync les supprimera de Climweb,
- les **local drift** sont laissées en l'état (vous garderez ainsi vos éditions manuelles tant que vous n'avez pas cliqué `overwrite`).

## Quand cliquer sur Synchronize ?

Juste après *Apply*. Sans synchro, Climweb continue de servir l'ancien contenu pour les couches concernées.
