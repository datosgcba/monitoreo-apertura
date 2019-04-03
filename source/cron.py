# coding=utf-8
import yaml
import time
import datetime
import schedule
import requests
from pymongo import MongoClient
from ga import updateDatajson, getBusquedas, getGaData

with open("../config.yml", 'r') as ymlfile:
  config = yaml.full_load(ymlfile)

connection = MongoClient(config['mongo_url'])
db = connection['monitoreo-apertura']
data_json_coll = db['data-json']
busquedas_coll = db['busquedas']

def job ():
  ga_data = getGaData()
  
  busquedas = getBusquedas(ga_data)
  busquedas_coll.insert_many(busquedas)

  data_json = requests.get(config['archivos']['data_json']).json()
  data_json = updateDatajson(ga_data, data_json)
  data_json_coll.insert_one(data_json)
  
def run ():
  schedule.every().day.at("00:00").do(job)

  while True:
    schedule.run_pending()
    time.sleep(1)