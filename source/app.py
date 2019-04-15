# coding=utf-8
import os
import math
import dash
import cron
import yaml
import requests
import itertools
import unidecode
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from multiprocessing import Process
from dash.dependencies import Input, Output, State
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

# def normalizarNombreColumna (string):
#   return "_".join([
#     "".join(
#       list(
#         filter(str.isalnum, s)
#       )
#     ) for s in unidecode.unidecode(
#       string
#         .lower()
#         .replace(' ', '_')
#         .replace('-', '_')
#     ).split('_')
#   ])

# ==============================
#           Router
# ==============================
@app.callback(dash.dependencies.Output('page-content', 'children'), [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
  indicadores = cache.get('indicadores')

  organizaciones = []
  #  [normalizarNombreColumna(x['_id']['organizacion']) for x in indicadores['actualizacion_por_organizacion']]

  if(pathname == "/" or not pathname):
    return general.layout()

  if(pathname == "/datos-abiertos"):
    return datosabiertos.layout()

  if(pathname.replace("/", "") in organizaciones):
    return organizacion.layout(pathname)

  return general.layout()

general.callbacks(app)

app.run_server(port=8080, host='0.0.0.0', debug=True)