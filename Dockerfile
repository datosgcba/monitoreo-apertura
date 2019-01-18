FROM python:2.7

COPY ["./src", "/usr/src/"]

WORKDIR /usr/src

RUN apt-get update

RUN apt-get -y install cron

RUN pip install -r requirements.txt

RUN python cron.py

EXPOSE 8050

ENTRYPOINT ["python", "tablero.py"]
