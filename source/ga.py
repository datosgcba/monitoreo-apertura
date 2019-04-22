# coding=utf-8 
import yaml
import urllib
import requests
import datetime
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

def getBusquedas (ga_data, fecha):
  busquedas = []
  for ga_row in ga_data:
    url = urllib.parse.urlparse('https://data.buenosaires.gob.ar{}'.format(ga_row[0]))
    url_params = urllib.parse.parse_qs(url.query)
    if ('q' in url_params.keys()):
      try:
        ind = [ x['query'] for x in busquedas ].index(url_params['q'])
        busquedas[ind][1] += int(ga_row[1])
        busquedas[ind][2] += int(ga_row[2])
      except ValueError:
        busquedas.append({ 'query': url_params['q'][0], 'vistas_totales': int(ga_row[1]), 'vistas_unicas': int(ga_row[2]), 'fecha': fecha })

  return busquedas

def updateDatajson(ga_data, data_json):
  ga_data_datasets = [ [urllib.parse.urlparse('https://data.buenosaires.gob.ar{}'.format(row[0])).path.split('/')[2], row[1], row[2]] for row in ga_data if 'dataset/' in row[0] ]

  for i, dataset in enumerate(data_json['dataset']):
    vistas = { 'totales': 0, 'unicas': 0 }
    urls = [ distribution['accessURL'] for distribution in dataset['distribution'] ]
    urls += [ dataset['landingPage'] ]
    urls = [ urllib.parse.urlparse(url) for url in urls ]
    urls = [ url.path.split('/')[2] for url in urls if url.hostname == 'data.buenosaires.gob.ar']

    for i_ga_row, ga_row in enumerate(ga_data_datasets):
      for url in urls:
        if url == ga_row[0]:
          vistas['totales'] += int(ga_row[1])
          vistas['unicas'] += int(ga_row[2])
          ga_data_datasets[i_ga_row][0] = ''

    data_json['dataset'][i]['vistas'] = vistas

  return data_json
