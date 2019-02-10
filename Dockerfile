FROM centos:7

RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm

RUN yum -y update

RUN yum install -y python36u python36u-libs python36u-devel python36u-pip initscripts && yum clean all

COPY ["./source/requirements.txt", "/opt/tablero/requirements.txt"]

WORKDIR /opt/tablero

RUN pip3.6 install -r requirements.txt

COPY ["./source", "/opt/tablero"]

EXPOSE 8050

CMD python3.6 app.py
