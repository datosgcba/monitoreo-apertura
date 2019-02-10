# coding=utf-8 
import datetime
import unidecode
from collections import Counter

def normalizarNombreColumna (string):
  return "_".join([ "".join(list(filter(str.isalnum, s))) for s in unidecode.unidecode(string.lower().replace(' ', '_').replace('-', '_')).split('_') ])

def calcular (data_json):
  indicadores = {}

  # Fecha actual
  indicadores['fecha'] = datetime.datetime.now().strftime('%d/%m/%Y:%H:%M:%S')

  # Cantidad de Datasets
  indicadores['cantidad_datasets'] = len(data_json["dataset"])

  # Cantidad de Datasets por organización
  indicadores.update(Counter([ normalizarNombreColumna('datasets_organizacion_' + dataset["source"].split(".")[0]) for dataset in data_json["dataset"] ]))

  # Cantidad de Datasets por categoría
  indicadores.update(Counter([ normalizarNombreColumna("datasets_categoria_" + theme) for dataset in data_json["dataset"] for theme in dataset["theme"] ]))

  # Cantidad de Recursos
  indicadores['cantidad_recursos'] = sum([ len(dataset["distribution"]) for dataset in data_json["dataset"] ])

  # Cantidad de Recursos por organización
  cantidad_recursos_org = Counter()
  for x in [ ( normalizarNombreColumna("recursos_organizacion_" + dataset["source"].split(".")[0]), len(dataset["distribution"]) ) for dataset in data_json["dataset"] ]:
    cantidad_recursos_org.update(Counter(dict([x])))
  indicadores.update(cantidad_recursos_org)

  # Cantidad de Recursos por categoría
  cantidad_recursos_cat = Counter()
  for x in [ ( normalizarNombreColumna("recursos_categoria_" + theme), len(dataset["distribution"]) ) for dataset in data_json["dataset"] for theme in dataset["theme"] ]:
    cantidad_recursos_cat.update(Counter(dict([x])))
  indicadores.update(cantidad_recursos_cat)

  return indicadores
