# Configuración

**Settings** es ahora una pestaña propia — la primera. Agrupa la configuración global del plugin (un único juego de valores por instancia Climweb) y actúa como puerta de entrada al resto del plugin: el **país** es obligatorio, y las pestañas *Layer Catalog*, *Admin Boundaries* y *Danger Zone* permanecen **bloqueadas** hasta que se guarde.

En una instancia nueva, la página se abre directamente en esta pestaña, con las demás bloqueadas. En cuanto guarde una configuración válida, la pestaña desbloquea las demás y muestra accesos directos para continuar con el catálogo o los límites.

## Language

Idioma en el que se importarán las etiquetas del catálogo incluido (títulos, descripciones, metadatos). El catálogo incluido es multilingüe; esta preferencia solo dice *qué* traducción se copiará en los `Dataset` y `Metadata` de Climweb en el momento de la carga.

Valores posibles: `en`, `fr`, `es`, `pt`, `ar`.

Cambiar el idioma **después** de una carga no renombra los datasets ya creados; hay que recargar el catálogo (`Review embedded catalog` → `Apply`) para propagar las nuevas etiquetas.

## Country *(obligatorio)*

El país objetivo de la instancia Climweb. Elíjalo en la lista desplegable (alimentada al abrir).

Este valor en realidad almacena cuatro datos vinculados:

- **alpha-3** (p. ej. `bfa`) — sustituye `{country_alpha3}` en las URL de las capas.
- **alpha-2** (p. ej. `bf`) — sustituye `{country_alpha2}`.
- **nombre oficial** (desde OpenStreetMap Nominatim) — usado para la visualización.
- **bounding box** `[south, north, west, east]` (desde Nominatim) — encuadre inicial de las capas en el mapa.

Mientras `Country` no esté definido, la carga del catálogo incluido rechazará o ignorará las capas cuya URL contenga un marcador de país.

## ECMWF Token

Token para el servicio WMS `eccharts.ecmwf.int`. Las capas privadas del catálogo incluido tienen una URL del tipo `…?token={ECMWF_TOKEN}`.

- **Vacío**: las capas privadas se **omiten** al cargar (contador `skipped_ecmwf_no_token`). Las capas públicas (`token=public`) se cargan con normalidad.
- **Relleno**: `{ECMWF_TOKEN}` se sustituye allí donde aparezca el marcador.

## Local eStation URL

URL de una instancia eStation local, por ejemplo `https://burkina.example.org/http/c000/w04/climsa/mobile-app`.

- **Vacía**: se importan todas las capas eStation del catálogo.
- **Rellena**: el plugin consulta la instancia y **solo conserva** los productos realmente disponibles (contador `skipped_estation` para los demás).

Útil cuando despliega Climweb sobre una eStation local que solo expone una parte de los productos del catálogo JRC.

## Guardar

El botón **Save Settings** persiste los valores y muestra un breve mensaje de confirmación. Sin efecto colateral en Climweb: la configuración solo se propaga en la siguiente acción de carga o sincronización.


## Próximos pasos

Una vez que los ajustes son válidos, la pestaña Settings muestra dos accesos directos:

- **Configurar el catálogo** — cambia a la pestaña *Layer Catalog*.
- **Configurar los límites** — cambia a la pestaña *Admin Boundaries*.

Solo cambian de pestaña; no se escribe nada hasta que actúe allí.
