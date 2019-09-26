Pasos para el despliegue de nuevas versiones:
1- Abrir la terminal en el proyecto.
2- Actualizar el código con `git push`
3- Detener el container con `docker stop`
4- Recrear el container con `docker build`
5- Volver a ejecutar el container con `docker run`