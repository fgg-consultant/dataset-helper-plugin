# Límites administrativos

La pestaña **Admin Boundaries** inicializa la capa de límites administrativos de Climweb a partir de los **Common Operational Datasets de OCHA (COD-AB)** publicados en [HDX](https://data.humdata.org/). Esta funcionalidad es independiente del catálogo de capas WMS: alimenta el *boundary manager* de Climweb, que sirve los límites como **teselas vectoriales (MVT)**.

## Requisitos

- El **país** debe estar configurado en los [ajustes del plugin](./settings.md) (pestaña *Settings*). Los códigos ISO alfa-2 y alfa-3 se usan para localizar y filtrar los datos.
- La instancia de Climweb debe incluir el *boundary manager* (`adminboundarymanager`) y `geopandas`. De lo contrario, se muestra una advertencia y el botón de importación queda deshabilitado.

## Importar límites

Haga clic en **Import boundaries from OCHA**. El plugin ejecuta toda la cadena automáticamente:

1. **Localiza** el conjunto de datos COD-AB en HDX mediante la API CKAN (`cod-ab-<iso3>`) y elige el archivo shapefile (`*.shp.zip`).
2. **Descarga** el archivo global (contiene un shapefile por nivel administrativo).
3. **Extrae** y detecta los niveles (`adm0`, `adm1`, …); las capas de líneas, puntos y capitales se omiten.
4. **Normaliza las columnas** de cada nivel al esquema que espera el boundary manager (`ADM{n}_EN`/`ADM{n}_FR` y `ADM{n}_PCODE`), reproyecta a EPSG:4326 y alinea `ADM0_PCODE` con el código del país.
5. **Vuelve a comprimir por nivel** y luego **carga** cada nivel en el boundary manager.

> El país se registra primero en los ajustes del boundary manager; de lo contrario, sus señales eliminarían las filas insertadas.

Al finalizar, un panel resume cuántas entidades se cargaron por nivel:

```
Boundaries imported: 4 level(s), 416 features
```

## Niveles cargados

La tabla **Loaded admin levels** muestra cuántas entidades hay por nivel para el país configurado:

| Nivel | Contenido típico |
|-------|------------------|
| 0 | País |
| 1 | Regiones |
| 2 | Provincias / departamentos |
| 3 | Municipios |
| 4 | (según el país) |

## Vista previa del mapa

El mapa en la parte inferior de la pestaña muestra los límites servidos por el boundary manager como teselas vectoriales:

```
/api/admin-boundary/tiles/{z}/{x}/{y}
```

Se centra automáticamente en el recuadro delimitador del país. Tras una importación, el mapa se actualiza para mostrar los datos recién cargados.

## Reimportar y eliminar

- **Reimportar** es idempotente: para cada nivel, los límites cargados previamente para este país se reemplazan.
- **Clear boundaries** elimina todos los límites del país configurado (todos los niveles). Esta acción no se puede deshacer.

## Fuente de datos

La fuente es **OCHA COD-AB** (Common Operational Datasets – Administrative Boundaries), los límites administrativos de referencia utilizados por las agencias humanitarias, publicados en HDX.
