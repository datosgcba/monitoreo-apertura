# Tablero de monitoreo de apertura del portal de datos abiertos.

Tablero implementado en [Dash](https://dash.plot.ly) que muestra una serie de indicadores que se calculan semanalmente a partir del data.json que expone el portal de datos abiertos.

## Requerimientos

Para usar el tablero es necesario tener:
- Fuente del archivo data.json
- Base de datos MongoDB
- Google Analytics

## Instalación

El sistema hace uso de Docker para su despliegue.

Para cargar la configuración hay que:
- Copiar el archivo `config.yml.dist`.
- Renombrarlo a `config.yml`.
- Reemplazar los datos de ejemplo.

Luego se procede a crear la imagen Docker usando el Dockerfile que se encuentra en la raiz del proyecto, ejecutando el comando:

`docker build -t organizacion/imagen:version .`

Y finalmente se ejecuta la imagen con el comando:

`docker run -p 8080:8080 organizacion/imagen:version`