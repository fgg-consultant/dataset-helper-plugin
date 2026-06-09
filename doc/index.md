---
layout: home

hero:
  name: Dataset Helper
  text: Le catalogue de couches de Climweb
  tagline: Activez, importez et synchronisez les couches du mapviewer sans toucher à l'admin Wagtail.
  actions:
    - theme: brand
      text: Premiers pas
      link: /getting-started
    - theme: alt
      text: Le catalogue
      link: /catalog
    - theme: alt
      text: GitHub
      link: https://github.com/fgg-consultant/dataset-helper-plugin

features:
  - icon: 📚
    title: Catalogue embarqué
    details: ~865 couches prêtes à l'emploi (JRC eStation, ECMWF, CAMS, EUMETSAT, CGLS…) livrées avec le plugin.
  - icon: ✅
    title: Sélection par cases à cocher
    details: Pickez les couches voulues dans un arbre Category › SubCategory › Layer. Activation en masse par catégorie.
  - icon: 🔄
    title: Synchronisation contrôlée
    details: Rien n'est écrit dans Climweb tant que vous n'avez pas cliqué sur Synchronize. Les modifications manuelles sont détectées et préservées.
  - icon: ➕
    title: Catalogue extensible
    details: Ajoutez vos propres couches manuellement, importez depuis un GetCapabilities WMS distant, ou chargez un JSON personnalisé.
---

## Vue d'ensemble

Le **Dataset Helper** est un plugin Climweb qui aide les administrateurs à constituer le catalogue de couches du mapviewer sans passer par la création manuelle de chaque `Dataset`, `Category`, `SubCategory` et `WmsLayer` dans l'admin Wagtail.

Le plugin embarque un catalogue par défaut et fournit une interface pour :

- activer ou désactiver des couches d'un simple coup de case à cocher,
- **synchroniser** la sélection vers la base Climweb (création / suppression des `Dataset` correspondants),
- **enrichir** le catalogue avec des couches ajoutées à la main, importées depuis un WMS distant ou chargées depuis un fichier JSON,
- suivre les **mises à jour** du catalogue embarqué quand une nouvelle version est livrée avec le plugin.

## Où trouver le plugin

Dans l'admin Wagtail, ouvrez le menu **GeoManager → Dataset helper**. La page se divise en quatre onglets :

- **Settings** — la configuration globale du plugin (pays, langue, jetons). Les autres onglets se déverrouillent une fois le pays obligatoire renseigné.
- **Layer Catalog** — l'écran principal de travail (arbre des couches, actions de synchronisation et d'import).
- **Admin Boundaries** — import des limites administratives (OCHA COD-AB).
- **Danger Zone** — les opérations destructives (purge des données provisionnées, wipe complet).

## Modèle mental

Le plugin maintient son propre catalogue (`CatalogEntry`) **à côté** des objets Climweb. Rien n'est écrit dans Climweb tant que vous n'avez pas cliqué sur **Synchronize with Climweb**.

```
Catalogue (CatalogEntry)            Climweb (geomanager)
─────────────────────────           ───────────────────────────
Entry  enabled=true   ──┐
Entry  enabled=true   ──┼── Sync ──►  Category › SubCategory › Dataset › WmsLayer
Entry  enabled=false  ──┘
```

Chaque entrée porte un **état** qui résume sa relation avec Climweb :

| Pastille | État              | Sens                                                                  |
|----------|-------------------|-----------------------------------------------------------------------|
| 🟢       | `synced`           | Cochée et déjà provisionnée dans Climweb.                            |
| 🟠       | `pending_add`      | Cochée mais pas encore provisionnée — sera créée à la prochaine sync. |
| 🔴       | `pending_remove`   | Décochée mais encore présente dans Climweb — sera supprimée.         |
| ⚪       | `disabled`         | Décochée et absente de Climweb — rien à faire.                       |

## Par où commencer

Si c'est votre première fois, suivez le [parcours en 5 étapes](./getting-started). Sinon, naviguez dans la barre latérale ou utilisez la recherche en haut à droite.
