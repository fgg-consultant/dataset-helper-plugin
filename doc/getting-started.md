# Premiers pas

Cette page décrit le parcours minimal pour faire apparaître un premier jeu de couches WMS dans le mapviewer Climweb avec le plugin Dataset Helper.

## Installer le plugin dans Climweb

Avant d'utiliser le plugin dans l'admin Wagtail, il doit être installé côté Climweb. Éditez le fichier `.env` de votre instance Climweb :

1. Mettez à jour Climweb à la version compatible :
   ```ini
   CLIMWEB_VERSION=1.1.3
   ```
2. Déclarez le dépôt du plugin :
   ```ini
   CLIMWEB_PLUGIN_GIT_REPOS=https://github.com/fgg-consultant/dataset-helper-plugin
   ```

Puis relancez Climweb pour que le plugin déclaré soit récupéré et installé :

```bash
docker compose down
docker compose up -d
```

Pour la procédure complète et les options avancées (plusieurs plugins, branche/tag spécifique, plugins privés…), voir la [documentation officielle Climweb](https://climweb.readthedocs.io/en/v1.1.1/_docs/technical/extending-climweb/plugin-installation.html).

## 1. Ouvrir la page Dataset helper

Dans l'admin Wagtail, ouvrez le menu **GeoManager → Dataset helper**.

Au premier lancement, l'arbre central est vide : le plugin sait qu'un catalogue par défaut existe sur disque mais il ne l'a pas encore chargé en base. Un bandeau en haut de page vous le rappelle.

## 2. Renseigner les réglages obligatoires

Avant de charger le catalogue embarqué, rendez-vous sur l'onglet **Settings** — le premier, qui s'ouvre automatiquement sur une instance neuve (les autres onglets restent verrouillés tant que vous n'avez pas terminé ici). Au minimum :

- **Country** *(obligatoire)* — choisissez le pays cible. Cette information sert à substituer les placeholders `{country_alpha3}` / `{country_alpha2}` dans les URLs des couches et à définir le cadrage initial de la carte (bbox issue de Nominatim).
- **Language** — langue dans laquelle les titres et descriptions seront importés (`en`, `fr`, `es`, `pt`, `ar`).

Optionnel selon les fournisseurs que vous voulez activer :

- **ECMWF Token** — nécessaire pour les couches `eccharts.ecmwf.int` privées (celles dont l'URL contient `token={ECMWF_TOKEN}`). Sans token, ces couches sont simplement ignorées au chargement.
- **Local eStation URL** — si renseigné, seules les couches eStation effectivement disponibles sur votre instance locale seront importées. Laissez vide pour tout importer.

Cliquez sur **Save Settings**. Tant que `Country` n'est pas défini, les autres onglets restent verrouillés ; une fois enregistré, l'onglet Settings les déverrouille et propose des raccourcis vers le catalogue et les limites.

Voir [Réglages](./settings) pour le détail.

## 3. Charger le catalogue embarqué

Tant que le catalogue est vide, l'onglet affiche un unique bloc d'avertissement — *No catalog loaded yet* — avec un bouton **Load catalog**. Cliquez dessus : le catalogue local étant vide, le catalogue embarqué est **appliqué directement** (pas de prévisualisation nécessaire — il n'y a rien avec quoi entrer en conflit).

L'arbre se remplit et toutes les entrées passent par défaut à l'état `pending_add` (pastille orange).

À ce stade, **aucun objet Climweb n'a encore été créé** : le catalogue n'a été rempli que côté plugin.

::: tip
L'étape de prévisualisation / diff ne sert que **plus tard**, pour les *mises à jour* : lorsqu'une version plus récente du catalogue est livrée, un bandeau vous permet de passer en revue le changeset avant de l'appliquer. Voir [Mises à jour du catalogue](./updates).
:::

## 4. Affiner la sélection

Dans l'arbre :

- Décochez les catégories, sous-catégories ou couches que vous ne voulez pas dans Climweb.
- Toutes les cases sont cochées par défaut.
- Vous pouvez tout déplier / replier via les chevrons en haut de l'arbre.

Voir [Le catalogue de couches](./catalog).

## 5. Synchroniser avec Climweb

Dès que votre sélection diffère de Climweb, un **bandeau out-of-sync** apparaît sous la vue d'ensemble et résume ce qui est en attente. Cliquez sur son bouton **Synchronize with Climweb**. Le plugin :

- crée les `Category`, `SubCategory`, `Dataset`, `Metadata` et `WmsLayer` correspondant aux entrées cochées,
- supprime ceux qui correspondent à des entrées décochées mais encore présentes en base.

Quand la synchro est terminée, les entrées passent à `synced` (pastille verte). Les couches sont alors visibles dans le mapviewer Climweb.

Voir [Synchroniser avec Climweb](./sync).

## Et ensuite ?

- Plus tard, quand une nouvelle version du plugin livre un catalogue mis à jour, voir [Mises à jour du catalogue](./updates).
