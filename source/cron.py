# coding=utf-8
import yaml
import time
import pprint
import datetime
import schedule
import requests
import indicadores
from pymongo import MongoClient
from werkzeug.contrib.cache import FileSystemCache
from ga import updateDatajson, getBusquedas, getGaData

cache = FileSystemCache(cache_dir="./.cache")
config = yaml.full_load(open("../config.yml", 'r'))
connection = MongoClient(config['mongo_url'])
db = connection['monitoreo-apertura']

def job ():
  # fecha = datetime.datetime.utcnow()

  # ga_data = getGaData()
  
  # busquedas = getBusquedas(ga_data, fecha)
  # db['busquedas'].insert_many(busquedas)

  # data_json = requests.get(config['archivos']['data_json']).json()
  # data_json['fecha'] = fecha
  # for dataset in data_json['dataset']:
  #   dataset['modified'] = datetime.datetime.strptime(dataset['modified'], '%Y-%m-%dT%H:%M:%S.%f')
  #   for distribution in dataset['distribution']:
  #     if 'modified' in distribution.keys():
  #       distribution['modified'] = datetime.datetime.strptime(distribution['modified'], '%Y-%m-%dT%H:%M:%S.%f')
      
  # data_json = updateDatajson(ga_data, data_json)
  # db['data-json'].insert_one(data_json)
  
  cache.set('indicadores', indicadores.crearIndicadores(db))

  pprint.pprint(cache.get('indicadores'))

def run ():
  schedule.every().day.at("00:00").do(job)

  while True:
    schedule.run_pending()
    time.sleep(1)