# coding=utf-8
import yaml
import json
import time
import schedule
import requests
import datetime
import indicadores
import pandas as pd
from ftplib import FTP
from io import StringIO
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

with open("config.yml", 'r') as ymlfile:
  config = yaml.load(ymlfile)

def actualiza_dataframe (dataframe, nuevos_indicadores):
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

def get_ga_metrics ():
  profile_id = None

  credentials = ServiceAccountCredentials.from_json_keyfile_dict(config['ga'], scopes=['https://www.googleapis.com/auth/analytics.readonly'])

  service = build('analytics', 'v3', credentials=credentials)

  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    account = accounts.get('items')[0].get('id')
    properties = service.management().webproperties().list(accountId=account).execute()

    if properties.get('items'):
      property = properties.get('items')[0].get('id')
      profiles = service.management().profiles().list(accountId=account, webPropertyId=property).execute()

      if profiles.get('items'):
        profile_id = profiles.get('items')[0].get('id')

  if not profile_id:
    print('No se pudo recuperar el Profile ID para Google Analytics')
    exit()

  resultado = {}
  resultado['ga_totales'] = service.data().ga().get(ids='ga:' + profile_id, start_date='2017-01-01', end_date='today', metrics='ga:pageviews,ga:uniquePageviews').execute()
  resultado['ga_datasets'] = service.data().ga().get(ids='ga:' + profile_id, start_date='2017-01-01', end_date='today', metrics='ga:pageviews', dimensions='ga:pagePathLevel2').execute()

  return resultado

def job ():
  ftp_config = config['ftp']
  ftp = FTP(ftp_config['host'], ftp_config["user"], ftp_config["pass"])
  csv_old = StringIO()
  ftp.retrlines('RETR /{}/indicadores.csv'.format(ftp_config['dir']), lambda line: csv_old.write("%s\n" % line))
  csv_old.seek(0)

  metricas = get_ga_metrics()
  data_json = requests.get(config['archivos']['data_json']).json()
  nuevos_indicadores = indicadores.calcular(data_json, metricas)

  dataframe = pd.read_csv(csv_old)
  dataframe = actualiza_dataframe(dataframe, nuevos_indicadores)

  csv_new = StringIO()
  dataframe.to_csv(csv_new, index=False)
  csv_new.seek(0)
  data_json_stream = StringIO(json.dumps(data_json))

  ftp.storbinary('STOR /{}/indicadores.csv'.format(ftp_config['dir']), str_to_bytes(csv_new))
  ftp.storbinary('STOR /{}/data-{}.json'.format(ftp_config['dir'], datetime.datetime.now().strftime('%d-%m-%Y')), str_to_bytes(data_json_stream))

  ftp.close()

def run ():
  schedule.every().day.at("00:00").do(job)

  while True:
    schedule.run_pending()
    time.sleep(1)