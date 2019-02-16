# coding=utf-8 
import ga
import datetime
import unidecode
import pandas as pd
from collections import Counter

def normalizarNombreColumna (string):
  return "_".join([ "".join(list(filter(str.isalnum, s))) for s in unidecode.unidecode(string.lower().replace(' ', '_').replace('-', '_')).split('_') ])

def normalize_dataset_from_path (path):
  if '?' in path:
    path = path.split('?')[0]
  if path.endswith('/'):
    path = path[:-1]
  return path.split('/')[-1]

def armar_indicadores_ga (ga_totales, ga_datasets, datasets):
  df = pd.DataFrame.from_records(data=ga_metricas_dataset['rows'], columns=[ x['name'] for x in ga_metricas_dataset['columnHeaders'] ])
  df['ga:pageviews'] = df['ga:pageviews'].astype('int')
  df['ga:pagePathLevel2'] = df['ga:pagePathLevel2'].apply(lambda x: normalize_dataset_from_path(x))
  df = df.groupby(['ga:pagePathLevel2']).sum().reset_index()
  df = df[df['ga:pagePathLevel2'].isin(datasets)]
  df.index = df['ga:pagePathLevel2'].apply(lambda x: 'vistas_dataset_{}'.format(x.replace('-', '_')))
  df = df[['ga:pageviews']].transpose()

  df['vistas_totales'] = ga_metricas_total['totalsForAllResults']['ga:pageviews']
  df['vistas_totales_unicas'] = ga_metricas_total['totalsForAllResults']['ga:uniquePageviews']

  df.to_csv('datasets-ga.csv', index=False)

  return df.to_dict()

def calcular (data_json, metricas):
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

  ga_indicadores = armar_indicadores_ga(metricas['ga_totales'], metricas['ga_datasets'], [ normalize_dataset_from_path(dataset['landingPage']) for dataset in data_json["dataset"] ])
  indicadores.update(ga_indicadores)

  return indicadores
