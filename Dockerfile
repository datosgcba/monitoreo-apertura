FROM ubuntu:latest

EXPOSE 8050

COPY ["./src", "/usr/src/"]

WORKDIR /usr/src

RUN apt-get update

RUN apt-get -y install python-pip cron

RUN pip install -r requirements.txt

CMD su -c "service cron start && python cron.py" && python tablero.py
