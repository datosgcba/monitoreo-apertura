# coding=utf-8
import yaml
import time
import datetime
import schedule
import requests
from pymongo import MongoClient
from ga import updateDatajson, getBusquedas, getGaData

config = yaml.full_load(open("../config.yml", 'r'))
connection = MongoClient(config['mongo_url'])
db = connection['monitoreo-apertura']

def job ():
  ga_data = getGaData()
  
  busquedas = getBusquedas(ga_data)
  db['busquedas'].insert_many(busquedas)

  data_json = requests.get(config['archivos']['data_json']).json()
  data_json['fecha'] = datetime.datetime.now().strftime('%d/%m/%Y:%H:%M:%S')
  data_json = updateDatajson(ga_data, data_json)
  db['data-json'].insert_one(data_json)

def run ():
  schedule.every().day.at("00:00").do(job)

  while True:
    schedule.run_pending()
    time.sleep(1)