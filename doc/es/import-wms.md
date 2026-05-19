# Importar desde un WMS

El botón **Import from WMS** permite consultar un servidor WMS remoto y tomar una capa de su `GetCapabilities`. Es más rápido que rellenar manualmente la URL y el identificador: el plugin lee los metadatos directamente del proveedor.

Las capas importadas por esta vía llevan el origen **`wms_import`**: las actualizaciones del catálogo incluido nunca las tocan.

## El flujo en tres pasos

### 1. Indicar la URL del WMS

Escriba la URL base del servicio (p. ej. `https://example.org/wms`). El plugin construye automáticamente la URL `GetCapabilities` (`?service=WMS&request=GetCapabilities&version=1.3.0`).

Haga clic en **Fetch Layers**.

### 2. Elegir una capa

El plugin lista todas las capas devueltas por el servidor, con:

- el identificador (`name`),
- el título legible (`title`),
- el abstract,
- el bbox WGS84 cuando se expone.

Un campo de búsqueda filtra la lista por nombre / título / abstract. Haga clic en una línea para seleccionarla.

::: tip
Si ha escrito una URL incorrecta, el enlace *Change URL* junto al contador de capas le lleva de vuelta al paso 1 sin recargar la página.
:::

### 3. Configurar la capa elegida

Aparece un pequeño formulario verde con:

| Campo             | Descripción                                                                |
|-------------------|----------------------------------------------------------------------------|
| **Layer Name**    | Prellenado, en solo lectura. Es el identificador tal como lo devuelve el WMS. |
| **Title**         | Prellenado con el título del WMS. Editable.                                |
| **Category** *    | Categoría bajo la que se clasificará la capa. Creada si no existe.         |
| **Subcategory** * | Igual.                                                                      |
| **Description**   | Prellenado a partir del abstract del WMS. Sirve como resumen / metadata.   |

Haga clic en **Add to Catalog**: la entrada se crea con el estado `pending_add` 🟠 y aparece en el árbol.

El botón **Back to list** le devuelve a la lista de capas del mismo servidor — práctico para importar varias capas del mismo proveedor en serie.

## Siguiente paso

Como siempre, haga clic en **Synchronize with Climweb** para provisionar realmente la capa.

## Límites

- El plugin solo soporta **WMS 1.3.0**. Si el servidor solo expone versiones más antiguas, la llamada puede fallar.
- Los **estilos** y **CRS** disponibles del lado del servidor no se exponen en el formulario (solo se usa el CRS por defecto del plugin, `EPSG:3857`, para las solicitudes Climweb).
- El formulario crea **una capa a la vez**. Para una importación masiva desde un mismo servidor, prefiera preparar un archivo JSON y usar el botón [Load Config JSON](./load-config).
