# Cargar un archivo JSON

El botón **Load Config JSON** sirve para dos usos distintos:

1. **Previsualizar el catálogo incluido** entregado con el plugin (acción *Review embedded catalog*).
2. **Cargar un JSON personalizado** que pega en la zona de texto.

En ambos casos, la carga rellena o actualiza la tabla de `CatalogEntry`. **No se crea ningún objeto Climweb hasta que hace clic en *Synchronize with Climweb***.

## Catálogo incluido (caso estándar)

Vea la página dedicada [Actualizaciones del catálogo](./updates). El flujo normal es:

1. **Review embedded catalog** → ve el diff entre el JSON en disco y el catálogo en base.
2. **Apply changes** → la tabla `CatalogEntry` se actualiza, `CatalogState` memoriza la versión.
3. **Synchronize with Climweb** → los `Dataset` Climweb se crean / eliminan / actualizan.

## JSON personalizado

Si gestiona su propio archivo de catálogo (además del catálogo incluido o en su lugar), pegue su contenido en la zona de texto y haga clic en **Load into Catalog**.

El plugin:

- crea las entradas ausentes,
- actualiza aquellas cuyo contenido haya cambiado,
- deja las demás intactas.

Las entradas creadas por esta vía llevan el origen **`config`**, igual que las del catálogo incluido. Consecuencia importante: si carga después el catálogo incluido, las entradas `config` que no aparezcan en el JSON incluido serán detectadas como **`to remove`** por la previsualización. Mezclar varias fuentes `config` requiere por tanto algo de cuidado.

## Formato esperado

El JSON debe seguir la estructura anidada **Categories → Subcategories → Datasets → Layers**:

```json
{
  "version": "2026.05.18",
  "schema_version": 1,
  "categories": [
    {
      "title": "Rainfall",
      "icon": "raindrops",
      "subcategories": [
        {
          "title": "Observation",
          "datasets": [
            {
              "title": "10-day precipitation estimate",
              "description": "...",
              "multi_temporal": true,
              "public": true,
              "metadata": {
                "function": "...",
                "resolution": "0.05deg",
                "source": "JRC eStation",
                "geographic_coverage": "Africa",
                "license": "Open Data",
                "frequency_of_update": "Dekadal",
                "overview": "...",
                "learn_more": "https://..."
              },
              "layers": [
                {
                  "type": "wms",
                  "title": "RFE 10-day",
                  "layer_name": "rfe_10d",
                  "wms_url": "https://example.org/wms",
                  "default": true,
                  "popup": true,
                  "legend_from_capabilities": true
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Campos raíz:

| Campo              | Función                                                                          |
|--------------------|----------------------------------------------------------------------------------|
| `version`          | Identificador de versión del catálogo. Usado para detectar las actualizaciones. |
| `schema_version`   | Versión del esquema JSON. Incrementada cuando la forma de las entradas cambia.  |
| `categories[]`     | Lista de categorías de máximo nivel.                                            |

Para las cadenas multilingües, el catálogo incluido usa un diccionario `{ "en": "...", "fr": "...", … }`. El plugin selecciona el idioma configurado en [Configuración](./settings) al cargar. También se acepta una cadena simple.

## Tipos de capas soportados

El campo `type` dentro de `layers[]` puede tomar:

- `wms` — servicio WMS estándar (el más común).
- `raster_tile` / `vector_tile` — servicios de teselas XYZ o PMTiles.
- `raster_file` / `vector_file` — archivos descargables (con autenticación Bearer opcional).
- `raster_cog` — Cloud-Optimized GeoTIFF con plantilla temporal.

Cada tipo tiene sus propios campos (URL plantilla, intervalo temporal, estilo ráster, configuración de popup…). Consulte el catálogo incluido para ver ejemplos completos.

### Campos específicos de WMS

Para las capas `wms`, dos opciones booleanas controlan lo que se activa en el lado de Climweb:

| Campo                       | Por defecto | Efecto en el `WmsLayer` de Climweb                                                                  |
|-----------------------------|-------------|-----------------------------------------------------------------------------------------------------|
| `popup`                     | `false`     | Activa **Enable popup**: se muestra un popup al hacer clic en la capa.                              |
| `legend_from_capabilities`  | `false`     | Activa **Load legend from WMS capabilities**: la leyenda se lee desde el `<LegendURL>` del GetCapabilities. |

Ambos son opt-in y deben definirse explícitamente por capa. En cada resincronización, el valor del JSON sobrescribe el valor del lado de Climweb.
