import dash_table
from itertools import groupby
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from tableros.organizacion import dias_frecuencias
from werkzeug.contrib.cache import FileSystemCache

import sys

cache = FileSystemCache(cache_dir="./.cache")

def layout():
  indicadores = cache.get('indicadores')
  datasets = indicadores['datasets']

  # ==============================
  #     Barras por publicador
  # ==============================
  publicadores = indicadores['datasets_por_publicador']

  barras_publicador = dcc.Graph(
    figure=go.Figure(
      data=[go.Bar(
        y=[x['_id']['publicador'] for x in publicadores],
        x=[x['datasets'] for x in publicadores],
        orientation = 'h',
      )]
    ),
  )

  # ==============================
  #       Barras por fuente
  # ==============================
  fuentes = indicadores['datasets_por_fuente']

  barras_fuentes = dcc.Graph(
    figure=go.Figure(
      data=[go.Bar(
        y=[x['_id']['fuente'] for x in fuentes],
        x=[x['datasets'] for x in fuentes],
        orientation = 'h'
      )]
    )
  )

  # ==============================
  #     Barras por frecuencia
  # ==============================
  frecuencias = indicadores['datasets_por_frecuencia']

  barras_frecuencias = dcc.Graph(
    figure=go.Figure(
      data=[go.Bar(
        y=[x['_id']['frecuencia'] for x in frecuencias],
        x=[x['datasets'] for x in frecuencias],
        orientation = 'h'
      )]
    )
  )

  # ==============================
  #     Barras por formato
  # ==============================
  formatos = indicadores['recursos_por_formato']

  barras_formatos = dcc.Graph(
    figure=go.Figure(
      data=[go.Bar(
        y=[x['_id']['formato'] for x in formatos],
        x=[x['recursos'] for x in formatos],
        orientation = 'h'
      )]
    )
  )

  # ==============================
  #    Torta por actualización
  # ==============================
  actualizados = len([x for x in datasets if x['dias'] <= dias_frecuencias[x['frecuencia']]])
  desactualizados = len([x for x in datasets if x['dias'] > dias_frecuencias[x['frecuencia']]])

  torta_actualizacion = dcc.Graph(
    id='graph',
    figure=go.Figure(
      data=[go.Pie(
        values= [actualizados, desactualizados],
        labels= ['Actualizados', 'Desactualizados'],
      )]
    )
  )

  # ==============================
  #      Tabla desactualizados
  # ==============================
  datasets = [x for x in datasets if x['dias'] > dias_frecuencias[x['frecuencia']]]
  datasets = sorted(datasets, key=lambda x: x['dias'])[::-1][:10]

  datasets = [{
    'Titulo': d['titulo'],
    'Frecuencia de actualización': d['frecuencia'],
    'Días desactualizado': int(d['dias']),
    'Fuente': d['fuente'],
    'Publicador': d['publicador'],
    'URL de descarga': d['url']
  } for d in datasets]

  tabla_datasets = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in datasets[0].keys()],
    data=datasets,
    style_table={'overflowX': 'scroll'}
  )

  return html.Div([
    html.H3('Publicadores', className='text-center'),
    barras_publicador,
    html.H3('Fuentes', className='text-center'),
    barras_fuentes,
    html.H3('Frecuencias', className='text-center'),
    barras_frecuencias,
    html.H3('Formatos', className='text-center'),
    barras_formatos,
    html.H3('Actualización', className='text-center'),
    torta_actualizacion,
    tabla_datasets
  ])
