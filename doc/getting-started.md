# Premiers pas

Cette page décrit le parcours minimal pour faire apparaître un premier jeu de couches WMS dans le mapviewer Climweb avec le plugin Dataset Helper.

## 1. Ouvrir la page Dataset helper

Dans l'admin Wagtail, ouvrez le menu **GeoManager → Dataset helper**.

Au premier lancement, l'arbre central est vide : le plugin sait qu'un catalogue par défaut existe sur disque mais il ne l'a pas encore chargé en base. Un bandeau d'information vous le rappelle en haut de page.

## 2. Renseigner les réglages obligatoires

Avant de pouvoir charger le catalogue embarqué, ouvrez le panneau **Settings** (replié juste sous les compteurs). Au minimum :

- **Country** *(obligatoire)* — choisissez le pays cible. Cette information sert à substituer les placeholders `{country_alpha3}` / `{country_alpha2}` dans les URLs des couches, et à remplir le cadrage initial de la carte (bbox issue de Nominatim).
- **Language** — langue dans laquelle les titres et descriptions seront importés (`en`, `fr`, `es`, `pt`, `ar`).

Optionnel selon les fournisseurs que vous voulez activer :

- **ECMWF Token** — nécessaire pour les couches `eccharts.ecmwf.int` privées (celles dont l'URL contient `token={ECMWF_TOKEN}`). Sans token, ces couches sont simplement ignorées au chargement.
- **Local eStation URL** — si renseigné, seules les couches eStation effectivement disponibles sur votre instance locale seront importées. Laissez vide pour tout importer.

Cliquez sur **Save Settings**. Tant que `Country` n'est pas défini, le panneau affiche un avertissement.

Voir [Réglages](./settings.md) pour le détail.

## 3. Charger le catalogue embarqué

Cliquez sur **Load Config JSON** puis **Review embedded catalog**. Le plugin calcule un *changeset* sans rien écrire et vous montre :

- ce qui sera **ajouté** au catalogue,
- ce qui sera **mis à jour**,
- ce qui sera **retiré** (si vous aviez chargé une version antérieure).

Cliquez sur **Apply changes** pour valider. L'arbre se remplit, et toutes les entrées passent par défaut à l'état `pending_add` (pastille orange).

À ce stade, **aucun objet Climweb n'a encore été créé** : le catalogue est juste rempli côté plugin.

## 4. Affiner la sélection

Dans l'arbre :

- Décochez les catégories, sous-catégories ou couches que vous ne voulez pas dans Climweb.
- Toutes les cases sont cochées par défaut.
- Vous pouvez tout déplier / replier via les chevrons en haut de l'arbre.

Voir [Le catalogue de couches](./catalog.md).

## 5. Synchroniser avec Climweb

Cliquez sur **Synchronize with Climweb**. Le plugin :

- crée les `Category`, `SubCategory`, `Dataset`, `Metadata` et `WmsLayer` correspondant aux entrées cochées,
- supprime ceux qui correspondent à des entrées décochées mais encore présentes en base.

Quand la synchro est terminée, les entrées passent à `synced` (pastille verte). Les couches sont alors visibles dans le mapviewer Climweb.

Voir [Synchroniser avec Climweb](./sync.md).

## Et ensuite ?

- [Ajouter manuellement une couche](./add-layer.md) qui n'est pas dans le catalogue.
- [Importer toutes les couches d'un serveur WMS](./import-wms.md).
- [Charger un autre fichier JSON](./load-config.md) (autre fournisseur, catalogue maison…).
- Plus tard, quand une nouvelle version du plugin livre un catalogue mis à jour, voir [Mises à jour du catalogue](./updates.md).
