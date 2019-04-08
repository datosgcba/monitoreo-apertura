# coding=utf-8 
import yaml
import pprint
from bson.son import SON
from pymongo import MongoClient
from werkzeug.contrib.cache import FileSystemCache

config = yaml.full_load(open("../config.yml", 'r'))
cache = FileSystemCache(cache_dir="./.cache")
connection = MongoClient(config['mongo_url'])
db = connection['monitoreo-apertura']
indicadores = {}

indicadores['por_organizacion'] = list(db['data-json'].aggregate([
  {"$unwind": "$dataset"},
  {"$project": {
    "fecha": "$fecha",
    "organizacion": { "$arrayElemAt": [{ "$split": ["$dataset.source", "."] }, 0] },
    "dataset": "$dataset.title",
    "recursos": { "$size": "$dataset.distribution" },
    "vistas": "$dataset.vistas"
  }},
  {"$group": {
    "_id": {
      "fecha": "$fecha",
      "organizacion": "$organizacion"
    },
    "datasets": {"$sum": 1},
    "recursos": {"$sum": "$recursos"},
    "vistas_totales": {"$sum": "$vistas.totales"},
    "vistas_unicas": {"$sum": "$vistas.unicas"},
  }}
]))

indicadores['por_categoria'] = list(db['data-json'].aggregate([
  {"$unwind": "$dataset"},
  {"$unwind": "$dataset.theme"},
  {"$project": {
    "fecha": "$fecha",
    "categoria": "$dataset.theme",
    "dataset": "$dataset.title",
    "recursos": { "$size": "$dataset.distribution" },
    "vistas": "$dataset.vistas"
  }},
  {"$group": {
    "_id": {
      "fecha": "$fecha",
      "categoria": "$categoria"
    },
    "datasets": {"$sum": 1},
    "recursos": {"$sum": "$recursos"},
    "vistas_totales": {"$sum": "$vistas.totales"},
    "vistas_unicas": {"$sum": "$vistas.unicas"},
  }}
]))

cache.set('indicadores', indicadores)


#########################
#########################
indicadores = cache.get('indicadores')
pprint.pprint(indicadores['por_categoria'])
































































# import datetime
# import unidecode
# import pandas as pd
# from collections import Counter

# def normalizarNombreColumna (string):
#   return "_".join([ "".join(list(filter(str.isalnum, s))) for s in unidecode.unidecode(string.lower().replace(' ', '_').replace('-', '_')).split('_') ])

# def normalizarNombrePathDataset (path):
#   if '?' in path:
#     path = path.split('?')[0]
#   if path.endswith('/'):
#     path = path[:-1]
#   path = path.split('/')[-1]
#   return path

# def armarIndicadoresGa (ga_datasets, org_cat_dataset):
#   views_by_categoria = {}
#   views_by_org = {}
#   ga_datasets_dict = { normalizarNombrePathDataset(x[0]): x[1] for x in ga_datasets['rows'] }
  
#   for (dataset, org, categorias) in org_cat_dataset:
#     org = normalizarNombreColumna('vistas_organizacion_{}'.format(org))
#     categorias = [ normalizarNombreColumna('vistas_categoria_{}'.format(cat)) for cat in categorias ]
#     if dataset in ga_datasets_dict.keys():
#       views = int(ga_datasets_dict[dataset])
#       if org in views_by_org.keys():
#         views_by_org[org] += views
#       else:
#         views_by_org[org] = views
      
#       for categoria in categorias:
#         if categoria in views_by_categoria.keys():
#           views_by_categoria[categoria] += views
#         else:
#           views_by_categoria[categoria] = views

#   full_dict = {}
#   full_dict.update(views_by_categoria)
#   full_dict.update(views_by_org)
  
#   return full_dict

# def calcular (data_json, ga_metricas):
#   indicadores = {}

#   # Fecha actual
#   indicadores['fecha'] = datetime.datetime.now().strftime('%d/%m/%Y:%H:%M:%S')

#   # Cantidad de Datasets
#   indicadores['cantidad_datasets'] = len(data_json["dataset"])

#   # Cantidad de Datasets por organización
#   indicadores.update(Counter([ normalizarNombreColumna('datasets_organizacion_' + dataset["source"].split(".")[0]) for dataset in data_json["dataset"] ]))

#   # Cantidad de Datasets por categoría
#   indicadores.update(Counter([ normalizarNombreColumna("datasets_categoria_" + theme) for dataset in data_json["dataset"] for theme in dataset["theme"] ]))

#   # Cantidad de Recursos
#   indicadores['cantidad_recursos'] = sum([ len(dataset["distribution"]) for dataset in data_json["dataset"] ])

#   # Cantidad de Recursos por organización
#   cantidad_recursos_org = {}
#   recursos_por_datasets_org = [ ( normalizarNombreColumna("recursos_organizacion_" + dataset["source"].split(".")[0]), len(dataset["distribution"]) ) for dataset in data_json["dataset"] ]
#   for recurso_por_dataset in recursos_por_datasets_org:
#     if recurso_por_dataset[0] in cantidad_recursos_org:
#       cantidad_recursos_org[recurso_por_dataset[0]] += recurso_por_dataset[1]
#     else: 
#       cantidad_recursos_org[recurso_por_dataset[0]] = recurso_por_dataset[1]
#   indicadores.update(cantidad_recursos_org)

#   # Cantidad de Recursos por categoría
#   cantidad_recursos_cat = {}
#   recursos_por_datasets_cat = [ ( normalizarNombreColumna("recursos_categoria_" + theme), len(dataset["distribution"]) ) for dataset in data_json["dataset"] for theme in dataset["theme"] ]
#   for recurso_por_dataset in recursos_por_datasets_cat:
#     if recurso_por_dataset[0] in cantidad_recursos_cat:
#       cantidad_recursos_cat[recurso_por_dataset[0]] += recurso_por_dataset[1]
#     else: 
#       cantidad_recursos_cat[recurso_por_dataset[0]] = recurso_por_dataset[1]
#   indicadores.update(cantidad_recursos_cat)

#   # Metricas Google Analytics
#   ga_indicadores = armarIndicadoresGa(ga_metricas['ga_datasets'], [ (normalizarNombrePathDataset(dataset['landingPage']), dataset["source"].split(".")[0], dataset["theme"]) for dataset in data_json["dataset"] ])
#   indicadores.update(ga_indicadores)

#   indicadores['vistas_totales'] = ga_metricas['ga_totales']['totalsForAllResults']['ga:pageviews']
#   indicadores['vistas_totales_unicas'] = ga_metricas['ga_totales']['totalsForAllResults']['ga:uniquePageviews']





#   # Cantidad de datasets por frecuencia de actualización
#   indicadores.update(Counter([ normalizarNombreColumna('datasets_frecuencia_' + dataset["accrualPeriodicity"]) for dataset in data_json["dataset"] ]))

#   # Cantidad de datasets formato por distribución
#   indicadores.update(Counter([ normalizarNombreColumna('recursos_formato_' + (distribution["format"] if 'format' in distribution.keys() else 'NO_FORMAT')) for dataset in data_json["dataset"] for distribution in dataset["distribution"] ]))

#   # Cantidad de datasets Keywords
#   indicadores.update(Counter([ normalizarNombreColumna('dataset_keyword_' + keyword) for dataset in data_json["dataset"] for keyword in dataset["keyword"] ]))

#   # Cantidad de datasets por publicador
#   indicadores.update(Counter([ normalizarNombreColumna('datasets_publicador_' + dataset["publisher"]['name']) for dataset in data_json["dataset"] ]))

#   # Cantidad de datasets por fuente
#   indicadores.update(Counter([ normalizarNombreColumna('datasets_fuente_' + dataset["source"]) for dataset in data_json["dataset"] ]))

#   return indicadores
