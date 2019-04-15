# coding=utf-8
import os
import math
import dash
import cron
import yaml
import requests
import unidecode
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from multiprocessing import Process
from dash.dependencies import Input, Output
from tableros import general, datosabiertos, organizacion
from werkzeug.contrib.cache import FileSystemCache

cache = FileSystemCache(cache_dir="./.cache")

Process(target=cron.run).start()
cron.job()

app = dash.Dash()
template = open("template.html", "r")
app.index_string = template.read()
app.config['suppress_callback_exceptions']=True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

def normalizarNombreColumna (string):
  return "_".join([
    "".join(
      list(
        filter(str.isalnum, s)
      )
    ) for s in unidecode.unidecode(
      string
        .lower()
        .replace(' ', '_')
        .replace('-', '_')
    ).split('_')
  ])

@app.callback(dash.dependencies.Output('page-content', 'children'), [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
  indicadores = cache.get('indicadores')

  organizaciones = [normalizarNombreColumna(x['_id']['organizacion']) for x in indicadores['actualizacion_por_organizacion']]

  if(pathname == "/" or not pathname):
    return general.layout()

  if(pathname == "/datos-abiertos"):
    return datosabiertos.layout()

  if(pathname.replace("/", "") in organizaciones):
    return organizacion.layout(pathname)

  return general.layout()


common_figure = dict(
  data=[],
  layout= dict(
    xaxis=dict(
      type='log',
      title='Cantidad de datasets',
    ),
    yaxis=dict(
      type='log',
      title='Cantidad de recursos',
    ),
    showlegend=False,
    height=600,
    hovermode='closest'
  )
)

@app.callback(Output('bubble', 'figure'), [Input('tabs', 'value')])
def render_content(tab):
  indicadores = cache.get('indicadores')
  por_tab = indicadores["por_organizacion"] if tab == 'org' else indicadores["por_categoria"]
  sizeref_org = 2.*(max([x['vistas_unicas'] for x in por_tab]))/(70**2)
  common_figure['data'] = [go.Scatter(
    y=[x['recursos'] for x in por_tab],
    x=[x['datasets'] for x in por_tab],
    text=[x['_id']['organizacion' if tab == 'org' else 'categoria'] for x in por_tab],
    customdata=[tab],
    mode='markers',
    hoverlabel = dict(namelength = -1),
    marker=dict(
      size=[x['vistas_unicas'] for x in por_tab],
      sizemode='area',
      sizeref=sizeref_org,
      sizemin=4,
      opacity=.5
    )
  )]
  return common_figure

@app.callback(Output('linea-de-tiempo', 'figure'), [Input('bubble', 'clickData')])
def render_content(clickData):
  indicadores = cache.get('indicadores')
  print(clickData)
  tab = clickData['points'][0]['customdata'] if 'customdata' in clickData['points'][0] else 'org'
  por_tab = indicadores["por_organizacion"] if tab == 'org' else indicadores["por_categoria"]
  print(por_tab)
  columna = ''
  if 'text' in clickData['points'][0]:
    columna = clickData['points'][0]['text']
  
  if columna == 'totales':
    return
    # columna = 'cantidad_datasets'
  
  return dict(
    data=[
      go.Scatter(
        y=[x['datasets'] for x in por_tab if x['_id']['organizacion' if tab == 'org' else 'categoria'] == columna],
        x=[x['_id']['fecha'] for x in por_tab if x['_id']['organizacion' if tab == 'org' else 'categoria'] == columna],
        mode='lines',
      )
    ],
    layout= dict(
      yaxis=dict(
        title='Cantidad de datasets',
      ),
      showlegend=False,
      height=600
    )
  )

# @app.callback(Output('linea-titulo', 'children'), [Input('bubble', 'clickData')])
# def render_content(clickData):
#   columna = clickData['points'][-1]['customdata']

#   if columna == 'totales':
#     return 'totales'

#   return " ".join(columna.split('_')[2:])

# @app.callback(Output('linea-datasets', 'children'), [Input('bubble', 'clickData')])
# def render_content(clickData):
#   columna = clickData['points'][-1]['customdata']
  
#   if columna == 'totales':
#     columna = 'cantidad_datasets'
#   valor = indicadores_hist[columna].tail(1).iloc[0]

#   return "{} Datasets".format(valor)

# @app.callback(Output('linea-recursos', 'children'), [Input('bubble', 'clickData')])
# def render_content(clickData):
#   columna = clickData['points'][-1]['customdata']
  
#   if columna == 'totales':
#     columna = 'cantidad_recursos'
#   else:
#     columna = columna.replace('datasets_organizacion_', 'recursos_organizacion_')
#   valor = indicadores_hist[columna].tail(1).iloc[0]

#   return "{} Recursos".format(valor)

# @app.callback(Output('linea-vistas', 'children'), [Input('bubble', 'clickData')])
# def render_content(clickData):
#   columna = clickData['points'][-1]['customdata']
  
#   if columna == 'totales':
#     columna = 'vistas_totales'
#   else:
#     columna = columna.replace('datasets_organizacion_', 'vistas_organizacion_')

#   valor = indicadores_hist[columna].tail(1).iloc[0]

#   return "{} Vistas".format(valor)

app.run_server(port=8080, host='0.0.0.0', debug=True)