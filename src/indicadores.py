# '/usr/src/append.txt'
# '/home/franciclo/git/indicadores-portal-datos-abiertos/src/append.txt'

import requests
import os
from collections import Counter
import pandas as pd

url = ""

try:
  url = os.environ['DATA_JSON_URL']
except:
  print "Falta DATA_JSON_URL"
  exit()

data_json = requests.get(url).json()


# Calculo de indicadores

cantidad_datasets = len(data_json['dataset'])

cantidad_recursos = len(data_json['dataset']) # sumar distribuciones

cantidad_datasets_org = Counter([ dataset['source'].split('.')[0] for dataset in data_json['dataset'] ]) #esta mal lo del counter con objetos, no suma las keys iguales

cantidad_recursos_org = Counter({ dataset['source'].split('.')[0]: len(dataset['distribution']) for dataset in data_json['dataset'] })

cantidad_datasets_cat = Counter([ theme for theme in dataset['theme'] for dataset in data_json['dataset'] ])

cantidad_recursos_cat = Counter({ theme: len(dataset['distribution']) for theme in dataset['theme'] for dataset in data_json['dataset'] })

# Fin calculo de indicadores

# indicadores = pd.read_csv('/home/franciclo/git/indicadores-portal-datos-abiertos/src/indicadores.csv')

# indicadores[]
 