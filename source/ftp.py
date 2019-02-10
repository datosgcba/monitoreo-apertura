# coding=utf-8
import os
import sys
import json
import schedule
import requests
import datetime
import indicadores
import pandas as pd
from ftplib import FTP
from io import StringIO, BytesIO
import cron

class str_to_bytes:
  def __init__(self, stringio):
    self.stringio = stringio

  def read(self, blocksize):
    return self.stringio.read(blocksize).encode()

ftp = FTP(os.environ["FTP_HOST"], os.environ["FTP_USER"], os.environ["FTP_PASS"])
csv_old = StringIO()
ftp.retrlines('RETR /tablero-apertura/indicadores.csv', lambda line: csv_old.write("%s\n" % line))
csv_old.seek(0)

data_json = requests.get(os.environ["DATA_JSON_URL"]).json()
nuevos_indicadores = indicadores.calcular(data_json)

dataframe = pd.read_csv(csv_old)
dataframe = cron.actualizaDataframe(dataframe, nuevos_indicadores)

csv_new = StringIO()
dataframe.to_csv(csv_new, index=False)
csv_new.seek(0)

data_json_stream = StringIO(json.dumps(data_json))

ftp.storbinary('STOR /tablero-apertura/indicadores.csv', str_to_bytes(csv_new))
ftp.storbinary('STOR /tablero-apertura/data-{}.json'.format(datetime.datetime.now().strftime('%d-%m-%Y')), str_to_bytes(data_json_stream))

ftp.close()
