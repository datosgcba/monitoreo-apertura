# coding=utf-8
import os
import yaml
import time
import json
import os.path
import datetime
import schedule
import requests
import indicadores
from datetime import date
from pymongo import MongoClient, ASCENDING
from ga import updateDatajson, getBusquedas, getGaData

config = yaml.full_load(open("./config.yml", 'r'))

def job ():
  open("cron.pid", 'w').write(str(os.getpid()));
  
  connection = MongoClient(config['mongo_url'])
  db = connection['monitoreo-apertura']

  hoy_desde = datetime.datetime.combine(date.today(), datetime.datetime.min.time())
  hoy_hasta = datetime.datetime.combine(date.today() + datetime.timedelta(days=1), datetime.datetime.min.time())
  query = db['data-json'].find_one({ "fecha": { "$gte": hoy_desde, "$lt": hoy_hasta } })
  if query and os.path.isfile('indicadores.json'): return

  fecha = datetime.datetime.utcnow()
  dia = fecha.strftime("%d/%m/%Y")
  ga_data = getGaData()
  
  busquedas = getBusquedas(ga_data, fecha, dia)

  data_json = requests.get(config['data_json']).json()
  
  data_json['fecha'] = fecha
  data_json['dia'] = dia
  for dataset in data_json['dataset']:
    dataset['modified'] = datetime.datetime.strptime(dataset['modified'], '%Y-%m-%dT%H:%M:%S.%f')
    for distribution in dataset['distribution']:
      if 'modified' in distribution.keys():
        distribution['modified'] = datetime.datetime.strptime(distribution['modified'], '%Y-%m-%dT%H:%M:%S.%f')
      
  data_json = updateDatajson(ga_data, data_json)
  
  try:
    db['busquedas'].insert_many(busquedas)
    db['data-json'].insert_one(data_json)
  except:
    pass

  with open('indicadores.json', 'w') as outfile:
    outfile.truncate(0)
    json.dump(indicadores.crearIndicadores(db), outfile)

def initDB():
  connection = MongoClient(config['mongo_url'])
  db = connection['monitoreo-apertura']

  if 'data_json' not in db.list_collection_names():
    db['data-json'].create_index('dia', unique=True)
  
  if 'busquedas' not in db.list_collection_names():
    db['busquedas'].create_index([('dia', ASCENDING), ('query', ASCENDING)], unique=True)

def run ():
  initDB()
  schedule.every().day.at("00:00").do(job)

  while True:
    schedule.run_pending()
    time.sleep(1)
