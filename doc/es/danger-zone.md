# Zona peligrosa

La pestaña **Danger Zone** y el botón **Reset Catalog** de la barra de herramientas agrupan las acciones **destructivas**. Todas son irreversibles; léalas con atención antes de hacer clic.

## Reset Catalog

Botón rojo en la barra del *Layer Catalog*. Esta acción:

1. **Elimina todos los `Dataset` Climweb provisionados por el plugin** (y solo esos: los datasets creados fuera del plugin se conservan).
2. Elimina los `Metadata` asociados.
3. Barre las `SubCategory` y `Category` que han quedado vacías.
4. **Vacía completamente la tabla `CatalogEntry`** (entradas `config`, `manual` y `wms_import` por igual).
5. Pone `CatalogState` a cero — el plugin olvida qué versión del catálogo estaba cargada.

Efecto neto: el plugin vuelve al estado del primer lanzamiento, y solo los datos Climweb creados fuera del plugin sobreviven.

**Cuándo usarlo:**

- Para empezar de cero antes de cargar un catálogo diferente.
- Tras una mala manipulación durante la fase de puesta en marcha.

**Cuándo no usarlo:**

- En producción, en una Climweb que sirve usuarios. Prefiera desactivar selectivamente las capas y sincronizar.

## Clear catalog-managed datasets

Botón en la pestaña *Danger Zone*. Variante menos agresiva de *Reset Catalog*:

1. Elimina los `Dataset` Climweb provisionados por el plugin (igual que arriba).
2. Elimina los `Metadata` asociados.
3. Barre las taxonomías vacías.
4. **Conserva** la tabla `CatalogEntry`: las entradas simplemente vuelven a `pending_add` 🟠.

Efecto neto: Climweb queda limpio del lado del plugin, pero su selección (qué capas están marcadas, sus añadidos manuales…) está intacta. Hacer clic luego en **Synchronize with Climweb** recrea todo desde cero con la selección actual.

**Caso de uso típico:** resolver una deriva persistente del contenido del lado de Climweb (títulos editados a mano, versiones antiguas de capas que quiere sobrescribir limpiamente).

## Clear All Datasets & Categories

Botón rojo en la parte inferior de la pestaña *Danger Zone*. **Nuclear**:

- Elimina **todos** los `Dataset`, `SubCategory` y `Category` del geomanager de Climweb, vengan del plugin o no.
- Elimina todos los `WmsLayer`, `WmsRequestLayer`, `RasterStyle`, `Metadata`.
- Pone a cero los `dataset_id` de los `CatalogEntry`.

Efecto neto: el mapviewer de Climweb se queda sin ninguna capa.

**Úselo solo si entiende exactamente lo que está haciendo** — por ejemplo durante una reinicialización completa del entorno.

## Tabla resumen

| Acción                              | `CatalogEntry` plugin | `Dataset` plugin | `Dataset` fuera del plugin | `Category` / `SubCategory` |
|-------------------------------------|:---------------------:|:----------------:|:--------------------------:|:--------------------------:|
| Desmarcar + Synchronize             | conservadas           | eliminados       | conservados                | conservadas si no vacías   |
| Clear catalog-managed datasets      | conservadas (`pending_add`) | eliminados | conservados                | sweep si vacías            |
| Reset Catalog                       | eliminadas            | eliminados       | conservados                | sweep si vacías            |
| Clear All Datasets & Categories     | `dataset_id` borrado  | eliminados       | **eliminados**             | **eliminadas**             |
