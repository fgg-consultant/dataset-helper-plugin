# Primeros pasos

Esta página describe el recorrido mínimo para hacer aparecer un primer conjunto de capas WMS en el mapviewer de Climweb usando el plugin Dataset Helper.

## Instalar el plugin en Climweb

Antes de usar el plugin desde la administración de Wagtail, debe estar instalado del lado de Climweb. Edite el archivo `.env` de su instancia de Climweb:

1. Actualice Climweb a la versión compatible:
   ```ini
   CLIMWEB_VERSION=1.1.3
   ```
2. Declare el repositorio del plugin:
   ```ini
   CLIMWEB_PLUGIN_GIT_REPOS=https://github.com/fgg-consultant/dataset-helper-plugin
   ```

Luego reinicie Climweb para que el plugin declarado sea descargado e instalado:

```bash
docker compose down
docker compose up -d
```

Para el procedimiento completo y las opciones avanzadas (varios plugins, rama/etiqueta específica, plugins privados…), consulte la [documentación oficial de Climweb](https://climweb.readthedocs.io/en/v1.1.1/_docs/technical/extending-climweb/plugin-installation.html).

## 1. Abrir la página Dataset helper

En la administración de Wagtail, abra **GeoManager → Dataset helper**.

En el primer lanzamiento, el árbol central está vacío: el plugin sabe que existe un catálogo por defecto en disco pero aún no lo ha cargado en la base de datos. Una franja en la parte superior de la página lo recuerda.

## 2. Completar la configuración obligatoria

Antes de cargar el catálogo incluido, vaya a la pestaña **Settings** — la primera, que se abre automáticamente en una instancia nueva (las demás pestañas están bloqueadas hasta que termine aquí). Como mínimo:

- **Country** *(obligatorio)* — elija el país objetivo. Esto sirve para sustituir los marcadores `{country_alpha3}` / `{country_alpha2}` en las URL de las capas y para definir el encuadre inicial del mapa (bbox de Nominatim).
- **Language** — idioma en el que se importan los títulos y descripciones (`en`, `fr`, `es`, `pt`, `ar`).

Opcionales, según los proveedores que quiera activar:

- **ECMWF Token** — necesario para las capas privadas `eccharts.ecmwf.int` (aquellas cuya URL contiene `token={ECMWF_TOKEN}`). Sin token, esas capas simplemente se ignoran al cargar.
- **Local eStation URL** — si está rellena, solo se importan los productos eStation realmente disponibles en su instancia local. Déjela vacía para importar todo.

Haga clic en **Save Settings**. Mientras `Country` falte, las demás pestañas permanecen bloqueadas; una vez guardado, la pestaña Settings las desbloquea y ofrece accesos directos al catálogo y a los límites.

Vea [Configuración](./settings) para los detalles.

## 3. Cargar el catálogo incluido

Mientras el catálogo está vacío, la pestaña muestra un único bloque de advertencia — *No catalog loaded yet* — con un botón **Load catalog**. Haga clic en él: como el catálogo local está vacío, el catálogo incluido se **aplica directamente** (sin necesidad de previsualización — no hay nada con lo que entrar en conflicto).

El árbol se llena y todas las entradas pasan por defecto a `pending_add` (punto naranja).

En esta etapa, **aún no se ha creado ningún objeto Climweb**: el catálogo solo se ha rellenado del lado del plugin.

::: tip
El paso de previsualización/diff solo se utiliza **más adelante**, para las *actualizaciones*: cuando llega una versión más reciente del catálogo, una franja le permite revisar el conjunto de cambios antes de aplicarlo. Vea [Actualizaciones del catálogo](./updates).
:::

## 4. Afinar la selección

En el árbol:

- Desmarque las categorías, subcategorías o capas que no quiera en Climweb.
- Todas las casillas están marcadas por defecto.
- Puede plegar / desplegar todo el árbol desde los chevrones de la parte superior.

Vea [El catálogo de capas](./catalog).

## 5. Sincronizar con Climweb

En cuanto su selección difiere de Climweb, aparece una **franja de desincronización** debajo del resumen, que resume lo que está pendiente. Haga clic en su botón **Synchronize with Climweb**. El plugin:

- crea los objetos `Category`, `SubCategory`, `Dataset`, `Metadata` y `WmsLayer` correspondientes a las entradas marcadas,
- elimina los que corresponden a entradas que ha desmarcado pero que aún estaban en la base de datos.

Cuando la sincronización termina, las entradas pasan a `synced` (punto verde). Las capas son ahora visibles en el mapviewer de Climweb.

Vea [Sincronizar con Climweb](./sync).

## ¿Y después?

- Más adelante, cuando una nueva versión del plugin traiga un catálogo actualizado, vea [Actualizaciones del catálogo](./updates).
