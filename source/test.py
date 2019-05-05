# coding=utf-8
import yaml
import datetime
from datetime import date
import requests
from pymongo import MongoClient
from ga import updateDatajson, getBusquedas, getGaData

config = yaml.full_load(open("../config.yml", 'r'))
connection = MongoClient(config['mongo_url'])
db = connection['monitoreo-apertura']

def loadTestData():
  fecha = datetime.datetime.utcnow()
  ga_data = getGaData()

  data_json = requests.get(config['data_json']).json()

  for dataset in data_json['dataset']:
    dataset['modified'] = datetime.datetime.strptime(dataset['modified'], '%Y-%m-%dT%H:%M:%S.%f')
    for distribution in dataset['distribution']:
      if 'modified' in distribution.keys():
        distribution['modified'] = datetime.datetime.strptime(distribution['modified'], '%Y-%m-%dT%H:%M:%S.%f')
      
  data_json = updateDatajson(ga_data, data_json)

  end = datetime.datetime.utcnow()
  dt = end - datetime.timedelta(days=5)
  step = datetime.timedelta(days=1)

  while dt < end:
    data_json['fecha'] = dt
    db['data-json'].insert_one(data_json.copy())
    dt += step

def getBusq():
  fecha = datetime.datetime.utcnow()
  ga_data = getGaData()
  getBusquedas(ga_data, "")

