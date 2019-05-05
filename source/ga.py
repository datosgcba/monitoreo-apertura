# coding=utf-8 
import yaml
import urllib
import requests
import datetime
import pandas as pd
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

config = yaml.full_load(open("./config.yml", 'r'))

def getGaData():
  profile_id = None
  credentials = ServiceAccountCredentials.from_json_keyfile_dict(
      config['ga'],
      scopes=['https://www.googleapis.com/auth/analytics.readonly']
    )
  service = build('analytics', 'v3', credentials=credentials)
  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    account = accounts.get('items')[0].get('id')
    properties = service.management().webproperties().list(
      accountId=account
    ).execute()

    if properties.get('items'):
      property = properties.get('items')[0].get('id')
      profiles = service.management().profiles().list(
        accountId=account, 
        webPropertyId=property
      ).execute()

      if profiles.get('items'):
        profile_id = profiles.get('items')[0].get('id')

  if not profile_id:
    print('No se pudo recuperar el Profile ID para Google Analytics')
    exit()

  resultado = service.data().ga().get(
      ids='ga:' + profile_id, 
      start_date='yesterday', 
      end_date='today', 
      metrics='ga:pageviews,ga:uniquePageviews',
      dimensions='ga:pagePath',
      filters='ga:hostname==data.buenosaires.gob.ar'
    ).execute()

  return resultado['rows']

def getBusquedas (ga_data, fecha, dia):
  busquedas = []
  for ga_row in ga_data:
    url = urllib.parse.urlparse('https://data.buenosaires.gob.ar{}'.format(ga_row[0]))
    url_params = urllib.parse.parse_qs(url.query)
    if ('q' in url_params.keys()):
      busquedas.append({ 'query': url_params['q'][0], 'vistas_totales': int(ga_row[1]), 'vistas_unicas': int(ga_row[2]) })
  
  df = pd.DataFrame(busquedas).groupby(['query']).sum()
  df['fecha'] = fecha
  df['dia'] = dia
  df['query'] = df.index
  result = df.to_dict('records')
  
  return result

def updateDatajson(ga_data, data_json):
  ga_data_datasets = pd.DataFrame([ [urllib.parse.urlparse('https://data.buenosaires.gob.ar{}'.format(row[0])).path.split('/')[2], row[1], row[2]] for row in ga_data if 'dataset/' in row[0] ], columns=['dataset', 'vistas_totales', 'vistas_unicas'], dtype=int)
  ga_data_datasets = ga_data_datasets.groupby(['dataset']).sum()
  ga_data_datasets_usados = []

  for i, dataset in enumerate(data_json['dataset']):
    vistas = { 'totales': 0, 'unicas': 0 }
    urls = [ distribution['accessURL'] for distribution in dataset['distribution'] ]
    urls += [ dataset['landingPage'] ]
    urls = [ urllib.parse.urlparse(url) for url in urls ]
    urls = [ url.path.split('/')[2] for url in urls if url.hostname == 'data.buenosaires.gob.ar']

    for ga_data_dataset in ga_data_datasets.iterrows():
      for url in urls:
        if url == ga_data_dataset[0] and ga_data_dataset[0] not in ga_data_datasets_usados:
          vistas['totales'] += int(ga_data_dataset[1][0])
          vistas['unicas'] += int(ga_data_dataset[1][1])
          ga_data_datasets_usados.append(ga_data_dataset[0])

    data_json['dataset'][i]['vistas'] = vistas

  return data_json
