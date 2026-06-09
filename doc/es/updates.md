# Actualizaciones del catálogo incluido

El plugin incluye un archivo `catalog.json` que describe el conjunto de capas entregadas por defecto. Este archivo lleva una `version` (por ejemplo `2026.05.18`). Cuando se despliega una nueva versión del plugin, esta versión cambia y el plugin sabe entonces que hay una **actualización del catálogo** disponible.

## La franja de actualización

Si la versión en disco difiere de la versión cargada en base, aparece una franja en la parte superior de la pestaña *Layer Catalog*:

> A new catalog version is available — review changes

Al hacer clic en **Review changes** se abre la previsualización. **Nada se escribe aún en la base** en esta etapa.

También puede disparar la previsualización manualmente con el botón **Load embedded catalog**.

## El changeset

La previsualización clasifica cada entrada del nuevo catálogo en un **bucket** y muestra los contadores arriba:

| Bucket           | Significado                                                                                  |
|------------------|-----------------------------------------------------------------------------------------------|
| **new**          | Entradas presentes en el nuevo catálogo, ausentes de la base.                                |
| **updated**      | El contenido de origen ha cambiado (título, URL, metadatos…) y **nada se ha modificado a mano** del lado de Climweb. Aplicación segura. |
| **local drift**  | El contenido de origen no ha cambiado pero el `Dataset` Climweb ha sido **editado manualmente** en la administración de Wagtail. El plugin no tocará nada. |
| **conflict**     | El contenido de origen **ha cambiado** Y el `Dataset` Climweb ha sido editado a mano. Decisión requerida. |
| **to remove**    | Entradas de origen `config` presentes en la base pero **ausentes** de la nueva versión del catálogo. Serán marcadas como desactivadas. |
| **unchanged**    | Nada que hacer.                                                                               |

Cada bucket es desplegable y lista las entradas afectadas (título + ubicación en la jerarquía).

## Aplicar el changeset

Se ofrecen dos botones según el contenido del changeset:

- **Apply — keep N local edits** *(por defecto cuando hay conflictos)* — aplica todos los cambios **salvo** los conflictos. Las modificaciones hechas a mano en la administración de Wagtail se conservan; las entradas en conflicto permanecen en `local drift` hasta su próxima decisión.
- **Apply — overwrite N conflicts** — aplica todo, incluidos los conflictos. Las modificaciones manuales son **sobrescritas** por el contenido del catálogo.
- **Cancel** — cierra la previsualización, no hace nada.

Si **no hay conflictos**, basta con un único botón **Apply changes**.

::: tip
La previsualización es estrictamente de solo lectura. Puede abrirla, cerrarla y reabrirla tantas veces como sea necesario sin riesgo.
:::

## Lo que modifica la aplicación

Aplicar el changeset actualiza la tabla `CatalogEntry` (y `CatalogState` para memorizar la nueva versión cargada). **No provisiona** los nuevos datasets ni elimina los datasets Climweb existentes — esa es la responsabilidad de **Synchronize with Climweb**:

```
1. Review changes   → actualiza el catálogo del plugin (CatalogEntry)
2. Synchronize      → propaga la selección a Climweb (Dataset)
```

En concreto, después de un *Apply*:

- las **new** aparecen como `pending_add` 🟠 en el árbol,
- las **updated** siguen en `synced` 🟢 pero su contenido de origen se refresca — la próxima sincro re-provisionará el `Dataset`,
- las **to remove** pasan a `pending_remove` 🔴 — la próxima sincro las eliminará de Climweb,
- las **local drift** se dejan tal cual (conservará así sus ediciones manuales mientras no haga clic en `overwrite`).

## ¿Cuándo hacer clic en Synchronize?

Justo después de *Apply*. Sin sincronización, Climweb sigue sirviendo el contenido antiguo para las capas afectadas.
