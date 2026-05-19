# El catálogo de capas

La pestaña **Layer Catalog** es la pantalla principal del plugin. Muestra el árbol de capas **Category › SubCategory › Layer** y permite pilotar lo que se provisionará en Climweb.

## Contadores

En la parte superior de la página, tres contadores resumen el estado del catálogo:

- **Total Layers** — número total de `CatalogEntry`, todos los orígenes incluidos.
- **Enabled** — entradas marcadas (que estarán o ya están en Climweb).
- **Synced** — entradas realmente provisionadas en Climweb.

La diferencia entre *Enabled* y *Synced* es lo que se modificará en la próxima sincronización.

## Estado de una capa

Cada línea de capa lleva un punto de color:

| Punto | Estado            | Significado                                                       |
|-------|-------------------|-------------------------------------------------------------------|
| 🟢    | `synced`           | Marcada y provisionada en Climweb.                                |
| 🟠    | `pending_add`      | Marcada pero aún no provisionada.                                 |
| 🔴    | `pending_remove`   | Desmarcada pero aún presente en Climweb.                          |
| ⚪    | `disabled`         | Desmarcada y ausente de Climweb.                                  |

Solo **Synchronize with Climweb** resuelve los estados naranja y rojo.

## Navegar en el árbol

El árbol es totalmente plegable. Tres interacciones principales:

- Hacer clic en la cabecera de una **categoría** o **subcategoría** la despliega / pliega.
- Los botones ▼ y ▶ encima del árbol despliegan o pliegan **todo**.
- Hacer clic en la línea de una capa abre / cierra su **panel de detalles** (URL WMS, identificador de capa, metadatos de origen…).

## Marcar / desmarcar

- **Una capa**: la casilla a la izquierda del título activa o desactiva esa entrada.
- **Una subcategoría**: la casilla en su cabecera conmuta **todas las capas** de la subcategoría a la vez (bulk toggle).
- **Una categoría**: igual, pero para toda la categoría.

El efecto es inmediato del lado del plugin (el estado pasa a `pending_add`/`pending_remove`) pero **nada se escribe aún del lado de Climweb**. Hay que hacer clic en **Synchronize with Climweb**.

## Origen de una capa

Cada entrada lleva un **origen** que describe cómo llegó al catálogo:

| Origen       | Cómo apareció                                                                |
|--------------|------------------------------------------------------------------------------|
| `config`     | Cargada desde el catálogo JSON incluido (o un JSON importado manualmente).   |
| `manual`     | Añadida mediante el formulario *+ Add Layer*.                                |
| `wms_import` | Importada desde un GetCapabilities WMS remoto.                               |

El origen importa sobre todo para las **actualizaciones** del catálogo incluido: solo las entradas `config` pueden marcarse `to_remove` cuando desaparecen de una nueva versión del JSON. Las entradas `manual` y `wms_import` nunca se ven afectadas por las actualizaciones automáticas.

## Acciones de la barra

Debajo del panel de configuración, la barra de herramientas agrupa las acciones principales:

- **Synchronize with Climweb** — aplica la selección actual (vea [Sincronizar](./sync)).
- **+ Add Layer** — añade una capa manualmente (vea [Añadir una capa](./add-layer)).
- **Import from WMS** — toma capas de un GetCapabilities remoto (vea [Importar desde un WMS](./import-wms)).
- **Load Config JSON** — carga un archivo JSON o previsualiza el catálogo incluido (vea [Cargar un JSON](./load-config) y [Actualizaciones](./updates)).
- **Reset Catalog** — operación **destructiva**; vea [Zona peligrosa](./danger-zone).
