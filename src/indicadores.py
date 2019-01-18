# coding=utf-8
import os
import datetime
import requests 
import unidecode
import pandas as pd
from collections import Counter

try:
  url = os.environ["DATA_JSON_URL"]
except:
  print "Falta DATA_JSON_URL"
  exit()

data_json = requests.get(url).json()

def normalizeColumnName (string):
  return "_".join([ filter(str.isalnum, s) for s in unidecode.unidecode(string.lower().replace(' ', '_').replace('-', '_')).split('_') ])


# Cantidad de Datasets
cantidad_datasets = len(data_json["dataset"])

# Cantidad de Datasets por organización
cantidad_datasets_org = Counter([ normalizeColumnName('datasets_organizacion_' + dataset["source"].split(".")[0]) for dataset in data_json["dataset"] ])

# Cantidad de Recursos por organización
# cantidad_recursos_org = Counter({ dataset["source"].split(".")[0]: len(dataset["distribution"]) for dataset in data_json["dataset"] }) # falta sumar las keys iguales

# Cantidad de Datasets por categoría
cantidad_datasets_cat = Counter([ normalizeColumnName("datasets_categoria_" + theme) for theme in dataset["theme"] for dataset in data_json["dataset"] ])

# Cantidad de Recursos por categoría
# cantidad_recursos_cat = Counter({ theme: len(dataset["distribution"]) for theme in dataset["theme"] for dataset in data_json["dataset"] }) # falta sumar las keys iguales

# Cantidad total de recursos
# cantidad_recursos = len(data_json["dataset"]) # falta sumar distribuciones


indicadores = pd.read_csv(os.path.abspath("src/indicadores.csv"))

for org in cantidad_datasets_org:
  if org not in indicadores.columns:
    indicadores.insert(0, org, "")

for cat in cantidad_datasets_cat:
  if cat not in indicadores.columns:
    indicadores.insert(0, cat, "")

nuevos_valores = {
  'cantidad_datasets': cantidad_datasets,
  'fecha': datetime.datetime.now().strftime("%d/%m/%Y")
}
nuevos_valores.update(cantidad_datasets_org)
nuevos_valores.update(cantidad_datasets_cat)

indicadores = indicadores.append(nuevos_valores, ignore_index=True)

indicadores.to_csv(os.path.abspath("src/indicadores.csv"), index=False)
