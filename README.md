# Dataset Helper Plugin

## Climweb Plugin

The plugin provides wizzards to easily create WMS reference datasets.
EG. Climate Station Datasets

## Quick start

### Build climweb docker images, 
The plugin needs images tagged with `climweb_dev` suffix. 

EG. `climweb_dev:latest`

### Build the plugin docker image

```bash
docker compose build
```

### Run the plugin container

```bash
docker compose up -d
```

Go on http://localhost/admin

## Dev
### Update frontend
The frontend is a VueJS SPA. So you need to copy the built files to the plugin static folder.

```bash
cd plugins/frontend
npm install
npm run build
cp -r dist/* ../dataset_helper_plugin/src/dataset_helper_plugin/static/dataset_helper_plugin/
```