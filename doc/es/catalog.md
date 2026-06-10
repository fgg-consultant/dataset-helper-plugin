# El catálogo de capas

La pestaña **Layer Catalog** es la pantalla principal del plugin. Muestra el árbol **Category › SubCategory › Layer** y permite controlar lo que se provisionará en Climweb.

En la parte superior de la pestaña, una cabecera recuerda el contexto — *GeoManager · Layer catalog for the Climweb map viewer* — con una etiqueta que muestra la versión del catálogo cargada actualmente (o *not loaded*) y un enlace a esta documentación.

## Resumen

Una tarjeta en la parte superior resume el estado del catálogo.

Tres contadores:

- **Catalog layers** — número total de `CatalogEntry`, todos los orígenes combinados.
- **Enabled** — entradas marcadas (las que estarán o ya están en Climweb).
- **Synced** — entradas realmente provisionadas en Climweb.

Luego, un **indicador de estado** desglosa el catálogo por estado — **Synced**, **To add**, **To remove**, **Disabled** — con una leyenda en color, para que vea de un vistazo cuán lejos está el catálogo de Climweb.

Una línea discreta recuerda la versión cargada: *Catalog vX · loaded DATE*.

## Estado de sincronización

El plugin muestra de inmediato si Climweb está sincronizado con su selección local:

- **In sync** — no se muestra nada; Climweb refleja su catálogo exactamente.
- **Out of sync** — aparece una franja destacada justo debajo del resumen: *Catalog out of sync with Climweb — N pending changes — X to create, Y to remove, Z to update*, junto con un botón **Synchronize with Climweb**.

Después de ejecutar una sincronización (o de cargar/restablecer), el **resultado** aparece en el mismo lugar, con el mismo estilo — verde en caso de éxito, rojo en caso de error — con una **×** verde para descartarlo.

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

Una barra de control se sitúa encima del árbol: un **cuadro de búsqueda**, **chips de filtro por estado**, botones de **select-all / deselect-all** y botones para **desplegar / plegar todo**.

El árbol es totalmente plegable. Tres interacciones principales:

- Hacer clic en la cabecera de una **categoría** o **subcategoría** la despliega / pliega.
- Los botones de desplegar / plegar (arriba a la derecha de la barra de control) abren o cierran **todas** las categorías y subcategorías a la vez.
- Hacer clic en la línea de una capa abre / cierra su **panel de detalles** (nombre de la capa, URL del servicio, proveedor, resolución, frecuencia, origen y las opciones de Climweb — popup, leyenda WMS, multitemporal, visible inicialmente, casi en tiempo real — más una previsualización GetMap).

Cada línea muestra, de un vistazo: una **casilla** de tres estados, un **punto de estado** de color, el **nombre** de la capa y **etiquetas** para el proveedor, el tipo de capa y (para las entradas heredadas) el origen. Cada cabecera de categoría lleva además una pequeña **mini-barra de estado** que resume sus capas.

## Buscar y filtrar

La barra de control encima del árbol permite acotar lo que se muestra — puramente del lado del cliente, no se envía nada al servidor:

- **Cuadro de búsqueda** — escriba para conservar solo las capas cuyo nombre, identificador de capa, proveedor, categoría o subcategoría coincida. Las categorías y subcategorías coincidentes se despliegan automáticamente. Bórrelo con el botón **×** o la tecla **Esc**.
- **Chips de filtro** — **All**, **To add**, **To remove**, **Disabled** restringen el árbol a las capas en ese estado. Los chips muestran un recuento en vivo para cada estado pendiente.

Mientras una búsqueda o un filtro está activo, solo se muestran y despliegan las ramas coincidentes; al borrarlo el árbol se pliega de nuevo a su estado de plegado/desplegado anterior. Si no hay coincidencias, el árbol muestra *No layer matches your search.*

## Marcar / desmarcar

- **Una sola capa**: la casilla a la izquierda del título activa o desactiva esa entrada.
- **Una subcategoría**: la casilla en su cabecera conmuta **todas las capas** de la subcategoría a la vez (bulk toggle).
- **Una categoría**: igual, pero para toda la categoría.
- **Todo el catálogo**: los botones de **select-all** / **deselect-all** de la barra de control activan o desactivan *todas* las capas a la vez.

El efecto es inmediato del lado del plugin (el estado pasa a `pending_add` / `pending_remove`) pero **nada se escribe aún en Climweb**. Aparece entonces la franja de desincronización — haga clic en **Synchronize with Climweb** para aplicar.

## Origen de una capa

Cada entrada lleva un **origen** que describe cómo llegó al catálogo:

| Origen       | Cómo apareció                                                                   |
|--------------|----------------------------------------------------------------------------------|
| `config`     | Cargada desde el catálogo JSON incluido. Es el único origen creado hoy en día.  |
| `manual` / `wms_import` | Orígenes heredados de versiones anteriores del plugin (añadido manual / importación WMS). Esos flujos se han eliminado; tales entradas pueden seguir existiendo en instancias antiguas. |

El origen importa sobre todo para las **actualizaciones** del catálogo incluido: solo las entradas `config` pueden marcarse `to_remove` cuando desaparecen de una nueva versión del catálogo. Las entradas heredadas `manual` / `wms_import` nunca se ven afectadas por las actualizaciones automáticas.

## Catálogo vacío

Cuando aún no se ha cargado ningún catálogo, la pestaña muestra **únicamente** un bloque de advertencia — *No catalog loaded yet* — con un botón **Load catalog**. Al hacer clic, se carga el catálogo incluido **directamente** (sin previsualización, ya que no hay nada con lo que entrar en conflicto). Aparecen entonces el resumen y el árbol. Vea [Primeros pasos](./getting-started).

## Barra de herramientas

Una vez cargado un catálogo, queda una única acción en la barra de herramientas:

- **Reset Catalog** — operación **destructiva**; vea [Zona peligrosa](./danger-zone).

La carga y la sincronización se controlan mediante las franjas descritas arriba en lugar de mediante botones de la barra de herramientas:

- el botón **Load catalog** (estado vacío) o el botón **Review changes** de la franja de actualización (vea [Actualizaciones del catálogo](./updates)) rellenan el catálogo,
- el botón **Synchronize with Climweb** (franja de desincronización) propaga la selección a Climweb (vea [Sincronizar](./sync)).
