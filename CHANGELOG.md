# Changelog
Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en[Keep a Changelog] (https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere a[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0 - 12-02-2018
#### Agregado
- Calcular indicadores en un proceso en segundo plano diariamente a partir del data.json del Portal de Datos Abiertos.
- Mostrar los indicadores en un tablero usando Dash.
- Usar FTP para almacenar archivos y CDN para leer.
- Leer métricas de uso del portal de datos de Google Analytics.

## 1.2.0 - 29-04-2019
#### Agregado
- Tableros de organización y de BA Data.
- Almacenar data.json en base de datos MongoDB.
- Calcula indicadores con agregaciones de MongoDB y guarda en archivo json local, diariamente.
#### Eliminado
- Uso de FTP y CDN.