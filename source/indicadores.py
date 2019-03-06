# coding=utf-8 
import datetime
import unidecode
import pandas as pd
from collections import Counter

def normalizarNombreColumna (string):
  return "_".join([ "".join(list(filter(str.isalnum, s))) for s in unidecode.unidecode(string.lower().replace(' ', '_').replace('-', '_')).split('_') ])

def normalizarNombrePathDataset (path):
  if '?' in path:
    path = path.split('?')[0]
  if path.endswith('/'):
    path = path[:-1]
  path = path.split('/')[-1]
  return path

def armarIndicadoresGa (ga_datasets, org_cat_dataset):
  views_by_categoria = {}
  views_by_org = {}
  ga_datasets_dict = { normalizarNombrePathDataset(x[0]): x[1] for x in ga_datasets['rows'] }
  
  for (dataset, org, categorias) in org_cat_dataset:
    org = normalizarNombreColumna('vistas_organizacion_{}'.format(org))
    categorias = [ normalizarNombreColumna('vistas_categoria_{}'.format(cat)) for cat in categorias ]
    if dataset in ga_datasets_dict.keys():
      views = int(ga_datasets_dict[dataset])
      if org in views_by_org.keys():
        views_by_org[org] += views
      else:
        views_by_org[org] = views
      
      for categoria in categorias:
        if categoria in views_by_categoria.keys():
          views_by_categoria[categoria] += views
        else:
          views_by_categoria[categoria] = views

  full_dict = {}
  full_dict.update(views_by_categoria)
  full_dict.update(views_by_org)
  
  return full_dict

def calcular (data_json, ga_metricas):
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
  cantidad_recursos_org = {}
  recursos_por_datasets_org = [ ( normalizarNombreColumna("recursos_organizacion_" + dataset["source"].split(".")[0]), len(dataset["distribution"]) ) for dataset in data_json["dataset"] ]
  for recurso_por_dataset in recursos_por_datasets_org:
    if recurso_por_dataset[0] in cantidad_recursos_org:
      cantidad_recursos_org[recurso_por_dataset[0]] += recurso_por_dataset[1]
    else: 
      cantidad_recursos_org[recurso_por_dataset[0]] = recurso_por_dataset[1]
  indicadores.update(cantidad_recursos_org)

  # Cantidad de Recursos por categoría
  cantidad_recursos_cat = {}
  recursos_por_datasets_cat = [ ( normalizarNombreColumna("recursos_categoria_" + theme), len(dataset["distribution"]) ) for dataset in data_json["dataset"] for theme in dataset["theme"] ]
  for recurso_por_dataset in recursos_por_datasets_cat:
    if recurso_por_dataset[0] in cantidad_recursos_cat:
      cantidad_recursos_cat[recurso_por_dataset[0]] += recurso_por_dataset[1]
    else: 
      cantidad_recursos_cat[recurso_por_dataset[0]] = recurso_por_dataset[1]
  indicadores.update(cantidad_recursos_cat)

  # Metricas Google Analytics
  ga_indicadores = armarIndicadoresGa(ga_metricas['ga_datasets'], [ (normalizarNombrePathDataset(dataset['landingPage']), dataset["source"].split(".")[0], dataset["theme"]) for dataset in data_json["dataset"] ])
  indicadores.update(ga_indicadores)

  indicadores['vistas_totales'] = ga_metricas['ga_totales']['totalsForAllResults']['ga:pageviews']
  indicadores['vistas_totales_unicas'] = ga_metricas['ga_totales']['totalsForAllResults']['ga:uniquePageviews']

  return indicadores
