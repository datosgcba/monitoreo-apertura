# coding=utf-8
import yaml
import time
import json
import datetime
from datetime import date
import schedule
import requests
import indicadores
from pymongo import MongoClient
from ga import updateDatajson, getBusquedas, getGaData

config = yaml.full_load(open("./config.yml", 'r'))
connection = MongoClient(config['mongo_url'])
db = connection['monitoreo-apertura']

def job ():
  hoy_desde = datetime.datetime.combine(date.today(), datetime.datetime.min.time())
  hoy_hasta = datetime.datetime.combine(date.today() + datetime.timedelta(days=1), datetime.datetime.min.time())
  query = db['data-json'].find_one({ "fecha": { "$gte": hoy_desde, "$lt": hoy_hasta } })
  if(query):
    return

  fecha = datetime.datetime.utcnow()
  ga_data = getGaData()
  
  busquedas = getBusquedas(ga_data, fecha)
  db['busquedas'].insert_many(busquedas)

  data_json = requests.get(config['data_json']).json()
  
  data_json['fecha'] = fecha
  
  for dataset in data_json['dataset']:
    dataset['modified'] = datetime.datetime.strptime(dataset['modified'], '%Y-%m-%dT%H:%M:%S.%f')
    for distribution in dataset['distribution']:
      if 'modified' in distribution.keys():
        distribution['modified'] = datetime.datetime.strptime(distribution['modified'], '%Y-%m-%dT%H:%M:%S.%f')
      
  data_json = updateDatajson(ga_data, data_json)
  
  db['data-json'].insert_one(data_json)

  with open('indicadores.json', 'w') as outfile:
    outfile.truncate(0)
    json.dump(indicadores.crearIndicadores(db), outfile)

def run ():
  schedule.every().day.at("00:00").do(job)

  while True:
    schedule.run_pending()
    time.sleep(1)