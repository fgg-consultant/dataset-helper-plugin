# Réglages

**Settings** est désormais un onglet à part entière — le premier. Il regroupe les paramètres globaux du plugin (un seul jeu de réglages par instance Climweb) et sert de porte d'entrée au reste du plugin : le **pays** est obligatoire, et les onglets *Layer Catalog*, *Admin Boundaries* et *Danger Zone* restent **verrouillés** tant qu'il n'est pas enregistré.

Sur une instance neuve, la page s'ouvre directement sur cet onglet, les autres étant verrouillés. Dès que vous enregistrez une configuration valide, l'onglet déverrouille les autres et propose des raccourcis pour poursuivre avec le catalogue ou les limites.

## Language

Langue dans laquelle les libellés du catalogue embarqué seront importés (titres, descriptions, métadonnées). Le catalogue embarqué est multilingue ; cette préférence dit simplement *quelle* traduction sera copiée dans les `Dataset` et `Metadata` Climweb au moment du chargement.

Valeurs possibles : `en`, `fr`, `es`, `pt`, `ar`.

Changer la langue **après** un chargement ne renomme pas les datasets déjà créés ; il faut recharger le catalogue (`Review embedded catalog` → `Apply`) pour propager les nouveaux libellés.

## Country *(obligatoire)*

Le pays cible de l'instance Climweb. Sélectionnez-le dans la liste déroulante (alimentée à l'ouverture).

Cette valeur stocke en réalité quatre informations liées :

- **alpha-3** (ex. `bfa`) — substitue `{country_alpha3}` dans les URLs des couches.
- **alpha-2** (ex. `bf`) — substitue `{country_alpha2}`.
- **nom officiel** (depuis OpenStreetMap Nominatim) — utilisé pour l'affichage.
- **bounding box** `[south, north, west, east]` (depuis Nominatim) — cadrage initial des couches sur la carte.

Tant que `Country` n'est pas renseigné, le chargement du catalogue embarqué refusera ou ignorera les couches dont l'URL contient un placeholder de pays.

## ECMWF Token

Jeton pour le service WMS `eccharts.ecmwf.int`. Les couches privées du catalogue embarqué ont une URL du type `…?token={ECMWF_TOKEN}`.

- **Vide** : les couches privées sont **ignorées** au chargement (statistique `skipped_ecmwf_no_token`). Les couches publiques (`token=public`) passent normalement.
- **Rempli** : `{ECMWF_TOKEN}` est substitué partout où le placeholder apparaît.

## Local eStation URL

URL d'une instance eStation locale, par exemple `https://burkina.example.org/http/c000/w04/climsa/mobile-app`.

- **Vide** : toutes les couches eStation du catalogue sont importées.
- **Renseignée** : le plugin interroge l'instance et **ne garde que** les produits qui y sont effectivement disponibles (statistique `skipped_estation` pour les autres).

Utile quand vous déployez Climweb adossé à une eStation locale qui n'expose qu'une partie des produits du catalogue JRC.

## Enregistrer

Le bouton **Save Settings** persiste les valeurs et affiche un court message de confirmation. Aucun effet de bord côté Climweb : les réglages ne se propagent qu'à la prochaine action de chargement ou de synchro.


## Étapes suivantes

Une fois les réglages valides, l'onglet Settings affiche deux raccourcis :

- **Configurer le catalogue** — bascule sur l'onglet *Layer Catalog*.
- **Configurer les limites** — bascule sur l'onglet *Admin Boundaries*.

Ces boutons ne font que changer d'onglet ; rien n'est écrit tant que vous n'agissez pas dans ces onglets.
