# Añadir una capa manualmente

El botón **+ Add Layer** (barra de herramientas del *Layer Catalog*) abre un formulario para insertar en el catálogo una capa que no está en el catálogo incluido y que no proviene de una importación WMS.

Las capas añadidas por esta vía llevan el origen **`manual`**: las actualizaciones del catálogo incluido nunca las tocan y permanecen en el catálogo mientras no las elimine.

## Campos

| Campo              | Obligatorio | Descripción                                                                |
|--------------------|:-----------:|----------------------------------------------------------------------------|
| **Category**       | ✔           | Título de la categoría. Crea la categoría si no existe; en caso contrario adjunta la nueva capa. |
| **Subcategory**    | ✔           | Igual a nivel de subcategoría.                                              |
| **Title**          |             | Etiqueta mostrada. Si está vacía, se usa el identificador WMS de la capa.   |
| **WMS Layer Name** | ✔           | Identificador exacto de la capa tal como aparece en el GetCapabilities WMS (parámetro `LAYERS`). |
| **WMS Base URL**   | ✔           | URL base del servicio WMS, sin los parámetros de consulta.                  |
| **Source**         |             | Productor / organismo origen de los datos. Copiado a `Metadata`.            |
| **Resolution**     |             | Resolución espacial (`1km`, `0.05deg`, etc.). Copiada a `Metadata`.         |

Haga clic en **Add**: la entrada se crea inmediatamente con el estado `pending_add` 🟠. Aparece en el árbol bajo la categoría y subcategoría indicadas.

## Siguiente paso

Haga clic en **Synchronize with Climweb** para provisionar realmente la capa.

## Modificar o eliminar una capa añadida

Una capa `manual` se gestiona como cualquier otra entrada del catálogo:

- **Desactivarla** (desmarcarla) la marcará como `pending_remove`; la próxima sincronización eliminará el `Dataset` del lado de Climweb.
- **Reactivarla** la devuelve a `pending_add`; la próxima sincronización la recreará.

Para modificar la URL o los parámetros, lo más simple es desactivar la antigua y añadir una nueva. La edición fina de un `Dataset` provisionado se hace directamente en la administración de Wagtail (pero se considerará *local drift* — vea [Actualizaciones](./updates)).
