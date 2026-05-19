# Sincronizar con Climweb

El botón **Synchronize with Climweb** (barra de herramientas del *Layer Catalog*) propaga el estado actual del catálogo a la base de datos de Climweb. Es la única acción que realmente crea o elimina `Dataset` en geomanager.

## Lo que hace la sincronización

El plugin recorre todas las entradas y actúa según su estado:

| Estado              | Acción                                                                                         |
|---------------------|------------------------------------------------------------------------------------------------|
| `pending_add` 🟠     | Provisiona en Climweb: crea / reutiliza `Category` y `SubCategory`, crea `Dataset`, `Metadata`, luego los objetos de capa (`WmsLayer`, `WmsRequestLayer`, etc. según el tipo). |
| `pending_remove` 🔴  | Desprovisiona: elimina el `Dataset` (y sus dependientes) del lado de Climweb, libera `dataset_id`. |
| `synced` 🟢          | Verifica que el `Dataset` aún existe. Si el contenido del catálogo ha cambiado desde la última sincronización, **re-provisiona** (título, URL o metadatos se actualizan). |
| `disabled` ⚪        | Nada que hacer.                                                                                 |

Al final, un panel de resultados resume la pasada:

```
Sync complete: 12 added, 3 removed, 5 updated, 0 orphans cleared
```

## Casos particulares

### Huérfanos

Si una entrada está marcada como `synced` pero el `Dataset` Climweb ha sido eliminado mientras tanto (por ejemplo desde la administración de Wagtail), se detecta como **huérfana**: `dataset_id` se reinicia a `null` y la entrada vuelve a `pending_add`. Una segunda sincronización la recreará.

El contador **orphans cleared** del panel de resultados refleja estas reconciliaciones.

### Categorías y subcategorías compartidas

El plugin **nunca elimina** una `Category` o `SubCategory` que aún contenga `Dataset` no gestionados por el plugin. Si ha creado manualmente un dataset en una categoría que también usa el plugin, desprovisionar las entradas del plugin no borrará esa categoría.

Las categorías vacías sí se barren al final del ciclo (vea [Zona peligrosa](./danger-zone)).

### Capas de tipo `raster_file`

Las capas `raster_file` (archivos ráster descargados y almacenados en Climweb) **no se re-provisionan** automáticamente cuando cambia el catálogo: sobrescribirlas destruiría los archivos ya subidos. El plugin señala este caso con el contador `raster_file drift` y deja intacto el objeto Climweb. Para aplicar el nuevo contenido, elimine la entrada y créela de nuevo (o vacíe las capas y vuelva a sincronizar).

## Qué hacer después de la sincronización

Tras una sincro exitosa, las capas son visibles en el mapviewer de Climweb. Del lado del plugin:

- todas las entradas marcadas están en `synced`,
- todas las desmarcadas están en `disabled`.

Puede retocar la selección en cualquier momento y volver a hacer clic en **Synchronize with Climweb**: solo se aplicará la diferencia respecto a la última sincronización.
