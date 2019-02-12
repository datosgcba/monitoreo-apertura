# coding=utf-8
import os
import sys
import json
import time
import schedule
import requests
import datetime
import indicadores
import pandas as pd
from ftplib import FTP
from io import StringIO, BytesIO

variables_faltantes = ""

if "DATA_JSON_URL" not in os.environ:
  variables_faltantes += "DATA_JSON_URL\n"
if "FTP_HOST" not in os.environ:
  variables_faltantes += "FTP_HOST\n"
if "FTP_USER" not in os.environ:
  variables_faltantes += "FTP_USER\n"
if "FTP_PASS" not in os.environ:
  variables_faltantes += "FTP_PASS\n"

if variables_faltantes != "":
  print("ERROR Faltan las siguientes variables de entorno:")
  print(variables_faltantes)
  exit()

def actualizaDataframe (dataframe, nuevos_indicadores):
  for columna in nuevos_indicadores.keys():
    if columna not in dataframe.columns:
      dataframe.insert(0, columna, "")

  dataframe = dataframe.append(nuevos_indicadores, ignore_index=True)

  return dataframe

class str_to_bytes:
  def __init__(self, stringio):
    self.stringio = stringio

  def read(self, blocksize):
    return self.stringio.read(blocksize).encode()

def job():
  ftp = FTP(os.environ["FTP_HOST"], os.environ["FTP_USER"], os.environ["FTP_PASS"])
  csv_old = StringIO()
  ftp.retrlines('RETR /datasets/tablero-apertura/indicadores.csv', lambda line: csv_old.write("%s\n" % line))
  csv_old.seek(0)

  data_json = requests.get(os.environ["DATA_JSON_URL"]).json()
  nuevos_indicadores = indicadores.calcular(data_json)

  dataframe = pd.read_csv(csv_old)
  dataframe = actualizaDataframe(dataframe, nuevos_indicadores)

  csv_new = StringIO()
  dataframe.to_csv(csv_new, index=False)
  csv_new.seek(0)
  data_json_stream = StringIO(json.dumps(data_json))

  ftp.storbinary('STOR /datasets/tablero-apertura/indicadores.csv', str_to_bytes(csv_new))
  ftp.storbinary('STOR /datasets/tablero-apertura/data-{}.json'.format(datetime.datetime.now().strftime('%d-%m-%Y')), str_to_bytes(data_json_stream))

  ftp.close()

def run ():
  schedule.every().day.at("00:00").do(job)

  while True:
    schedule.run_pending()
    time.sleep(1)