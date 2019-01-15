# '/usr/src/append.txt'
# '/home/franciclo/git/indicadores-portal-datos-abiertos/src/append.txt'

import csv
import requests
import os
from collections import Counter

url = ""

try:
  url = os.environ['DATA_JSON_URL']
except:
  print "Falta DATA_JSON_URL"
  exit()

r = requests.get(url)
data_json = r.json()

cantidad_datasets = len(data_json.datasets)

cantidad_datasets_org = Counter([ dataset.source.split('.')[0] for dataset in data_json.datasets ])

cantidad_recursos_org = [ len(dataset.distribution) for dataset in data_json.datasets ] # hacerlo por org

cantidad_datasets_cat = Counter([ theme for theme in dataset.theme for dataset in data_json.datasets ])

with open('/home/franciclo/git/indicadores-portal-datos-abiertos/src/indicadores.csv', mode='a') as indicadores:
  indicadores = csv.writer(indicadores, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  indicadores.writerow(['John Smith', 'Accounting', 'November'])
 