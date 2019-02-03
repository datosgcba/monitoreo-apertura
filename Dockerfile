FROM centos:7

RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm

RUN yum -y update

RUN yum install -y crontabs python36u python36u-libs python36u-devel python36u-pip initscripts && yum clean all

COPY ["./src/requirements.txt", "/opt/tablero/requirements.txt"]

WORKDIR /opt/tablero

RUN pip3.6 install -r requirements.txt

COPY ["./src", "/opt/tablero"]

EXPOSE 8050

CMD su -c "python3.6 cron.py" && python3.6 tablero.py
