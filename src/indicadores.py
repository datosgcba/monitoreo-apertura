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

# Fecha actual
fecha = datetime.datetime.now().strftime('%d/%m/%Y:%H:%M:%S')

# Cantidad de Datasets
cantidad_datasets = len(data_json["dataset"])

# Cantidad de Datasets por organización
cantidad_datasets_org = Counter([ normalizeColumnName('datasets_organizacion_' + dataset["source"].split(".")[0]) for dataset in data_json["dataset"] ])

# Cantidad de Datasets por categoría
cantidad_datasets_cat = Counter([ normalizeColumnName("datasets_categoria_" + theme) for dataset in data_json["dataset"] for theme in dataset["theme"] ])

# Cantidad de Recursos
cantidad_recursos = sum([ len(dataset["distribution"]) for dataset in data_json["dataset"] ])

# Cantidad de Recursos por organización
cantidad_recursos_org = Counter()
for x in [ ( normalizeColumnName("recursos_organizacion_" + dataset["source"].split(".")[0]), len(dataset["distribution"]) ) for dataset in data_json["dataset"] ]:
  cantidad_recursos_org.update(Counter(dict([x])))

# Cantidad de Recursos por categoría
cantidad_recursos_cat = Counter()
for x in [ ( normalizeColumnName("recursos_categoria_" + theme), len(dataset["distribution"]) ) for dataset in data_json["dataset"] for theme in dataset["theme"] ]:
  cantidad_recursos_cat.update(Counter(dict([x])))

indicadores = pd.read_csv("{}indicadores.csv".format(os.environ["SOURCE_PATH"]))

columnas_variables = cantidad_datasets_org.keys() + cantidad_recursos_org.keys() + cantidad_datasets_cat.keys() + cantidad_recursos_cat.keys()

for columna in columnas_variables:
  if columna not in indicadores.columns:
    indicadores.insert(0, columna, "")

nuevos_valores = {
  'cantidad_recursos': cantidad_recursos,
  'cantidad_datasets': cantidad_datasets,
  'fecha': fecha
}
nuevos_valores.update(cantidad_datasets_org)
nuevos_valores.update(cantidad_recursos_org)
nuevos_valores.update(cantidad_datasets_cat)
nuevos_valores.update(cantidad_recursos_cat)

indicadores = indicadores.append(nuevos_valores, ignore_index=True)

indicadores.to_csv("{}indicadores.csv".format(os.environ["SOURCE_PATH"]), index=False)
