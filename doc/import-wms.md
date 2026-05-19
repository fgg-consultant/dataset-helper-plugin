# Importer depuis un WMS

Le bouton **Import from WMS** permet d'interroger un serveur WMS distant et de piocher une couche dans son `GetCapabilities`. C'est plus rapide que de remplir manuellement l'URL et l'identifiant : le plugin lit les métadonnées directement chez le fournisseur.

Les couches importées par ce biais portent l'origine **`wms_import`** : elles ne sont jamais touchées par les mises à jour du catalogue embarqué.

## Le flux en trois étapes

### 1. Renseigner l'URL du WMS

Saisissez l'URL de base du service (ex. `https://example.org/wms`). Le plugin construit automatiquement l'URL `GetCapabilities` (`?service=WMS&request=GetCapabilities&version=1.3.0`).

Cliquez sur **Fetch Layers**.

### 2. Choisir une couche

Le plugin liste toutes les couches retournées par le serveur, avec :

- l'identifiant (`name`),
- le titre humain (`title`),
- l'abstract,
- la bbox WGS84 quand elle est exposée.

Un champ de recherche permet de filtrer la liste par nom / titre / abstract. Cliquez sur une ligne pour la sélectionner.

::: tip
Si vous avez tapé la mauvaise URL, le lien *Change URL* à côté du compteur de couches vous ramène à l'étape 1 sans recharger la page.
:::

### 3. Configurer la couche choisie

Un petit formulaire vert apparaît avec :

| Champ            | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| **Layer Name**   | Pré-rempli, en lecture seule. C'est l'identifiant tel que renvoyé par le WMS. |
| **Title**        | Pré-rempli avec le titre du WMS. Modifiable.                                |
| **Category** *   | Catégorie sous laquelle la couche sera classée. Créée si elle n'existe pas. |
| **Subcategory** *| Idem.                                                                       |
| **Description**  | Pré-remplie depuis l'abstract du WMS. Sert de résumé / metadata.            |

Cliquez sur **Add to Catalog** : l'entrée est créée avec le statut `pending_add` 🟠 et apparaît dans l'arbre.

Le bouton **Back to list** vous ramène à la liste des couches du même serveur — pratique pour importer plusieurs couches du même fournisseur en série.

## Étape suivante

Comme toujours, cliquez sur **Synchronize with Climweb** pour provisionner réellement la couche.

## Limites

- Le plugin ne prend en charge que **WMS 1.3.0**. Si le serveur n'expose que des versions plus anciennes, l'appel peut échouer.
- Les **styles** et **CRS** disponibles côté serveur ne sont pas exposés dans le formulaire (seul le CRS par défaut du plugin, `EPSG:3857`, sera utilisé pour les requêtes Climweb).
- Le formulaire crée **une couche à la fois**. Pour un import en masse depuis un même serveur, préférez la pré-construction d'un fichier JSON et le bouton [Load Config JSON](./load-config.md).
