---
layout: home

hero:
  name: Dataset Helper
  text: El catálogo de capas WMS de Climweb
  tagline: Active, importe y sincronice las capas del mapviewer sin tocar la administración de Wagtail.
  actions:
    - theme: brand
      text: Primeros pasos
      link: /es/getting-started
    - theme: alt
      text: El catálogo
      link: /es/catalog
    - theme: alt
      text: GitHub
      link: https://github.com/fgg-consultant/dataset-helper-plugin

features:
  - icon: 📚
    title: Catálogo incluido
    details: ~119 capas WMS listas para usar (JRC eStation, ECMWF, CAMS, EUMETSAT, CGLS…) entregadas con el plugin.
  - icon: ✅
    title: Selección por casillas
    details: Elija las capas que quiere en un árbol Categoría › Subcategoría › Capa. Activación masiva por categoría.
  - icon: 🔄
    title: Sincronización controlada
    details: Nada se escribe en Climweb hasta que haga clic en Sincronizar. Las modificaciones manuales son detectadas y preservadas.
  - icon: ➕
    title: Catálogo extensible
    details: Añada sus propias capas manualmente, impórtelas desde un GetCapabilities WMS remoto o cargue un JSON personalizado.
---

## Visión general

El **Dataset Helper** es un plugin de Climweb que ayuda a los administradores a construir el catálogo de capas del mapviewer sin tener que crear manualmente cada `Dataset`, `Category`, `SubCategory` y `WmsLayer` en la administración de Wagtail.

El plugin incluye un catálogo por defecto y ofrece una interfaz para:

- activar o desactivar capas con un simple clic en una casilla,
- **sincronizar** la selección con la base de datos de Climweb (creación / eliminación de los `Dataset` correspondientes),
- **enriquecer** el catálogo con capas añadidas manualmente, importadas desde un WMS remoto o cargadas desde un archivo JSON,
- seguir las **actualizaciones** del catálogo incluido cuando se entrega una nueva versión con el plugin.

## Dónde encontrar el plugin

En la administración de Wagtail, abra el menú **GeoManager → Dataset helper**. La página se divide en dos pestañas:

- **Layer Catalog** — la pantalla principal de trabajo (configuración, árbol de capas, acciones de sincronización e importación).
- **Danger Zone** — las operaciones destructivas (purga de los datos provisionados, borrado completo).

## Modelo mental

El plugin mantiene su propio catálogo (`CatalogEntry`) **al lado** de los objetos de Climweb. Nada se escribe en Climweb hasta que hace clic en **Synchronize with Climweb**.

```
Catálogo (CatalogEntry)             Climweb (geomanager)
─────────────────────────           ───────────────────────────
Entry  enabled=true   ──┐
Entry  enabled=true   ──┼── Sync ──►  Category › SubCategory › Dataset › WmsLayer
Entry  enabled=false  ──┘
```

Cada entrada tiene un **estado** que resume su relación con Climweb:

| Punto | Estado            | Significado                                                            |
|-------|-------------------|------------------------------------------------------------------------|
| 🟢    | `synced`           | Marcada y ya provisionada en Climweb.                                  |
| 🟠    | `pending_add`      | Marcada pero aún no provisionada — se creará en la próxima sincro.    |
| 🔴    | `pending_remove`   | Desmarcada pero aún presente en Climweb — será eliminada.              |
| ⚪    | `disabled`         | Desmarcada y ausente de Climweb — nada que hacer.                      |

## Por dónde empezar

Si es su primera vez, siga el [recorrido en 5 pasos](./getting-started). De lo contrario, navegue por el menú lateral o use la búsqueda arriba a la derecha.
