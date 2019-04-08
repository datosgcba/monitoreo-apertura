# coding=utf-8
import os
import math
import dash
import cron
import yaml
import requests
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from multiprocessing import Process
from dash.dependencies import Input, Output

Process(target=cron.run).start()

config = yaml.full_load(open("../config.yml", 'r'))
app = dash.Dash()

template = open("template.html", "r")
app.index_string = template.read()

data_json = requests.get(config['archivos']['data_json']).json()
indicadores = pd.read_csv(config['archivos']['indicadores_csv'])
indicadores = indicadores.loc[:, ~indicadores.columns.str.contains('^Unnamed')]
indicadores['fecha'] = pd.to_datetime(indicadores['fecha'], format='%d/%m/%Y:%H:%M:%S', utc=True)

datasets_organizacion_cols = [ column for column in indicadores.columns if column.startswith('datasets_organizacion_') ]
sizeref_org = 2.*(indicadores[datasets_organizacion_cols].max().max())/(70**2)
for col in datasets_organizacion_cols:
    col_vistas = col.replace('datasets_organizacion_', 'vistas_organizacion_')
    if col_vistas not in indicadores.columns:
      indicadores.insert(1, col_vistas, 1)

datasets_categoria_cols = [ column for column in indicadores.columns if column.startswith('datasets_categoria_') ]  
sizeref_cat = 2.*(indicadores[datasets_categoria_cols].max().max())/(70**2)
for col in datasets_categoria_cols:
    col_vistas = col.replace('datasets_categoria_', 'vistas_categoria_')
    col_recursos = col.replace('datasets_categoria_', 'recursos_categoria_')
    if col_vistas not in indicadores.columns:
      indicadores.insert(1, col_vistas, 1)

indicadores_hist = indicadores
indicadores_actual = indicadores[-1:]
indicadores = indicadores_actual

indicadores = indicadores.drop(['vistas_totales_unicas', 'vistas_totales', 'fecha', 'cantidad_datasets', 'cantidad_recursos'], axis=1)

indicadores = indicadores.transpose()

indicadores['index'] = indicadores.index
indicadores['nombre'] = indicadores['index'].str\
                                        .replace('recursos_categoria_', '').str \
                                        .replace('vistas_categoria_', '').str \
                                        .replace('datasets_categoria_', '').str \
                                        .replace('recursos_organizacion_', '').str \
                                        .replace('vistas_organizacion_', '').str \
                                        .replace('datasets_organizacion_', '').str \
                                        .replace('_', ' ')

df = pd.DataFrame([], columns=['vistas', 'recursos', 'datasets', 'nombre', 'tipo'])
for i,d in indicadores.groupby(['nombre']):
    d['columnas'] = d['index'].apply(lambda x: x.split('_')[0])
    d['tipo'] = d['index'].apply(lambda x: 'organizacion' if '_organizacion_' in x else ('categoria' if '_categoria_' in x else ''))
    
    d = d.append(pd.DataFrame([[d['nombre'].iloc[0], '', '', 'nombre', '']], columns=d.columns), ignore_index=True)
    d = d.append(pd.DataFrame([[d['tipo'].iloc[0], '', '', 'tipo', '']], columns=d.columns), ignore_index=True)
    d = d.transpose()
    d.columns = d.loc['columnas']
    d = d.reset_index()
    d = d[['vistas', 'recursos', 'datasets', 'nombre', 'tipo']]
    d = d.iloc[0]
    df = df.append(d)

df = df.append(pd.DataFrame([[indicadores_actual['vistas_totales'].iloc[0], indicadores_actual['cantidad_recursos'].iloc[0], indicadores_actual['cantidad_datasets'].iloc[0], 'totales', 'totales']], columns=df.columns), ignore_index=True)

app.layout = html.Div([
    dcc.Tabs(id="tabs", value='org', children=[
        dcc.Tab(label='Organizaciones', value='org'),
        dcc.Tab(label='Categorías', value='cat'),
    ]),
    html.Div(id='graph-wrapper', children=[
      dcc.Graph(
        id='bubble',
        clickData={'points': [{'customdata': 'totales'}]}
      ),
      html.Div([
        html.Div(id='datos-linea', children=[
          html.H5(id='linea-titulo'),
          html.Div([
            html.P(id='linea-datasets', className='label label-primary'),
            html.P(id='linea-recursos', className='label label-primary'),
            html.P(id='linea-vistas', className='label label-primary'),
          ])
        ]),
        dcc.Graph(
          id='linea-de-tiempo'
        )
      ])
    ])
])

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
  if tab == 'org':
    common_figure['data'] = [go.Scatter(
      y=df[df['tipo'] == 'organizacion']['recursos'],
      x=df[df['tipo'] == 'organizacion']['datasets'],
      text=df[df['tipo'] == 'organizacion']['nombre'],
      customdata=df[df['tipo'] == 'organizacion']['nombre'].apply(lambda x: 'datasets_organizacion_{}'.format(x.replace(' ', '_'))),
      mode='markers',
      hoverlabel = dict(namelength = -1),
      marker=dict(
        size=df[df['tipo'] == 'organizacion']['vistas'].tolist(),
        sizemode='area',
        sizeref=sizeref_org,
        sizemin=4,
        opacity=.5
      )
    )]
    return common_figure

  elif tab == 'cat':
    common_figure['data'] = [go.Scatter(
      y=df[df['tipo'] == 'categoria']['recursos'],
      x=df[df['tipo'] == 'categoria']['datasets'],
      text=df[df['tipo'] == 'categoria']['nombre'],
      customdata=df[df['tipo'] == 'categoria']['nombre'].apply(lambda x: 'datasets_categoria_{}'.format(x.replace(' ', '_'))),
      mode='markers',
      hoverlabel = dict(namelength = -1),
      marker=dict(
        size=df[df['tipo'] == 'categoria']['vistas'].tolist(),
        sizemode='area',
        sizeref=sizeref_org,
        sizemin=4,
        opacity=.5
      )
    )]
    return common_figure

@app.callback(Output('linea-de-tiempo', 'figure'), [Input('bubble', 'clickData')])
def render_content(clickData):
  columna = clickData['points'][0]['customdata']
  
  if columna == 'totales':
    columna = 'cantidad_datasets'
  
  return dict(
    data=[
      go.Scatter(
        y=indicadores_hist[columna],
        x=indicadores_hist['fecha'],
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

@app.callback(Output('linea-titulo', 'children'), [Input('bubble', 'clickData')])
def render_content(clickData):
  columna = clickData['points'][-1]['customdata']

  if columna == 'totales':
    return 'totales'

  return " ".join(columna.split('_')[2:])

@app.callback(Output('linea-datasets', 'children'), [Input('bubble', 'clickData')])
def render_content(clickData):
  columna = clickData['points'][-1]['customdata']
  
  if columna == 'totales':
    columna = 'cantidad_datasets'
  valor = indicadores_hist[columna].tail(1).iloc[0]

  return "{} Datasets".format(valor)

@app.callback(Output('linea-recursos', 'children'), [Input('bubble', 'clickData')])
def render_content(clickData):
  columna = clickData['points'][-1]['customdata']
  
  if columna == 'totales':
    columna = 'cantidad_recursos'
  else:
    columna = columna.replace('datasets_organizacion_', 'recursos_organizacion_')
  valor = indicadores_hist[columna].tail(1).iloc[0]

  return "{} Recursos".format(valor)

@app.callback(Output('linea-vistas', 'children'), [Input('bubble', 'clickData')])
def render_content(clickData):
  columna = clickData['points'][-1]['customdata']
  
  if columna == 'totales':
    columna = 'vistas_totales'
  else:
    columna = columna.replace('datasets_organizacion_', 'vistas_organizacion_')

  valor = indicadores_hist[columna].tail(1).iloc[0]

  return "{} Vistas".format(valor)

app.run_server(port=8080, host='0.0.0.0', debug=True)