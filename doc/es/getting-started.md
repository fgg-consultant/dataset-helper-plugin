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

Para el procedimiento completo y las opciones avanzadas (varios plugins, rama/etiqueta específica, plugins privados…), consulte la [documentación oficial de Climweb](https://climweb.readthedocs.io/es/v1.1.1/_docs/technical/extending-climweb/plugin-installation.html).

## 1. Abrir la página Dataset helper

En la administración de Wagtail, abra el menú **GeoManager → Dataset helper**.

En el primer lanzamiento, el árbol central está vacío: el plugin sabe que existe un catálogo por defecto en disco pero aún no lo ha cargado en la base de datos. Una franja informativa lo recuerda en la parte superior de la página.

## 2. Completar la configuración obligatoria

Antes de poder cargar el catálogo incluido, abra el panel **Settings** (plegado justo debajo de los contadores). Como mínimo:

- **Country** *(obligatorio)* — elija el país objetivo. Esta información sirve para sustituir los marcadores `{country_alpha3}` / `{country_alpha2}` en las URL de las capas, y para definir el encuadre inicial del mapa (bbox de Nominatim).
- **Language** — idioma en el que se importarán los títulos y descripciones (`en`, `fr`, `es`, `pt`, `ar`).

Opcionales según los proveedores que quiera activar:

- **ECMWF Token** — necesario para las capas `eccharts.ecmwf.int` privadas (aquellas cuya URL contiene `token={ECMWF_TOKEN}`). Sin token, esas capas simplemente se ignoran al cargar.
- **Local eStation URL** — si está rellena, solo se importarán los productos eStation realmente disponibles en su instancia local. Déjela vacía para importar todo.

Haga clic en **Save Settings**. Mientras `Country` no esté definido, el panel muestra una advertencia.

Vea [Configuración](./settings) para los detalles.

## 3. Cargar el catálogo incluido

Haga clic en **Load embedded catalog**. El plugin calcula un *changeset* sin escribir nada y le muestra:

- lo que se **añadirá** al catálogo,
- lo que se **actualizará**,
- lo que se **eliminará** (si había cargado una versión anterior).

Haga clic en **Apply changes** para validar. El árbol se llena y todas las entradas pasan por defecto a `pending_add` (punto naranja).

En esta etapa, **aún no se ha creado ningún objeto Climweb**: el catálogo solo se rellena del lado del plugin.

## 4. Afinar la selección

En el árbol:

- Desmarque las categorías, subcategorías o capas que no quiera en Climweb.
- Todas las casillas están marcadas por defecto.
- Puede desplegar / plegar todo desde los chevrones de la parte superior del árbol.

Vea [El catálogo de capas](./catalog).

## 5. Sincronizar con Climweb

Haga clic en **Synchronize with Climweb**. El plugin:

- crea los `Category`, `SubCategory`, `Dataset`, `Metadata` y `WmsLayer` correspondientes a las entradas marcadas,
- elimina los que corresponden a entradas desmarcadas pero aún presentes en la base.

Cuando la sincronización termina, las entradas pasan a `synced` (punto verde). Las capas son entonces visibles en el mapviewer de Climweb.

Vea [Sincronizar con Climweb](./sync).

## ¿Y después?

- Más adelante, cuando una nueva versión del plugin traiga un catálogo actualizado, vea [Actualizaciones del catálogo](./updates).
