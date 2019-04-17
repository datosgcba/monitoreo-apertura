# coding=utf-8
import os
import math
import dash
import cron
import yaml
import datetime
import requests
import pandas as pd
from plotly import tools
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from multiprocessing import Process
from dash.dependencies import Input, Output, State
from werkzeug.contrib.cache import FileSystemCache

def diasDesdeHoy(num):
  fechas = []
  dt = datetime.datetime.utcnow()
  step = datetime.timedelta(days=1)

  for i in range(num):
    fechas.append(dt.strftime('%Y-%m-%d'))
    dt -= step
  return fechas.reverse()

cache = FileSystemCache(cache_dir="./.cache")

def layout():
  return html.Div([
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

def callbacks (app):
  @app.callback(Output('bubble', 'clickData'), [Input('tabs', 'value')])
  def render_content(tab):
    return {'points': [{'customdata': 'totales'}]}
  # ==============================
  #           Burbujas
  # ==============================
  @app.callback(Output('bubble', 'figure'), [Input('tabs', 'value')])
  def render_content(tab):
    indicadores = cache.get('indicadores')
    if not indicadores:
      return
    por_tab = indicadores["por_organizacion" if tab == 'org' else "por_categoria"]
    sizeref = 2.*(max([x['vistas_unicas'] for x in por_tab]))/(70**2)

    return dict(
      data=[go.Scatter(
        y=[x['recursos'] for x in por_tab],
        x=[x['datasets'] for x in por_tab],
        text=[x['_id']['organizacion' if tab == 'org' else 'categoria'] for x in por_tab],
        mode='markers',
        hoverlabel = dict(namelength = -1),
        marker=dict(
          size=[x['vistas_unicas'] for x in por_tab],
          sizemode='area',
          sizeref=sizeref,
          sizemin=4,
          opacity=.5
        )
      )],
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

  # ==============================
  #       Linea datasets
  # ==============================
  @app.callback(Output('linea-de-tiempo', 'figure'), [Input('bubble', 'clickData')], [State('tabs', 'value')])
  def render_content(clickData, tab):
    indicadores = cache.get('indicadores')
    por_tab = indicadores["por_organizacion" if tab == 'org' else "por_categoria"]
    annotations = []

    if 'text' in clickData['points'][0]:
      data = [x for x in por_tab if x['_id']['organizacion' if tab == 'org' else 'categoria'] == clickData['points'][0]['text']]
    else:
      data = indicadores["por_totales"]

    fechas = diasDesdeHoy(len(data))

    fig = tools.make_subplots(
      rows=3,
      cols=1,
      specs=[[{}], [{}], [{}]],
      shared_xaxes=True,
      shared_yaxes=True,
      vertical_spacing=0.1
    )

    fig.append_trace(go.Scatter(
      y=[x['datasets'] for x in data],
      x=fechas,
      mode='lines',
      line=dict(color='#1f77b4'),
      showlegend=False,
      name='Datasets'
    ), 1, 1)

    annotations.append(dict(
      yref='y1',
      xanchor='left',
      yanchor='middle',
      x=fechas[-1],
      y=data[-1]['datasets'],
      text='{} Datasets'.format(data[-1]['datasets']),
      font=dict(color='white'),
      bgcolor='#1f77b4',
      borderpad=2,
      showarrow=False
    ))

    fig.append_trace(go.Scatter(
      y=[x['recursos'] for x in data],
      x=fechas,
      mode='lines',
      line=dict(color='#1f77b4'),
      showlegend=False,
      name='Recursos'
    ), 2, 1)

    annotations.append(dict(
      yref='y2',
      xanchor='left',
      yanchor='middle',
      x=fechas[-1],
      y=data[-1]['recursos'],
      text='{} Recursos'.format(data[-1]['recursos']),
      font=dict(color='white'),
      bgcolor='#1f77b4',
      borderpad=2,
      showarrow=False
    ))

    fig.append_trace(go.Scatter(
      y=[x['vistas_unicas'] for x in data],
      x=fechas,
      mode='lines',
      line=dict(color='#1f77b4'),
      showlegend=False,
      name='Vistas únicas'
    ), 3, 1)

    annotations.append(dict(
      yref='y3',
      xanchor='left',
      yanchor='middle',
      x=fechas[-1],
      y=data[-1]['vistas_unicas'],
      text='{} Vistas Únicas'.format(data[-1]['vistas_unicas']),
      font=dict(color='white'),
      bgcolor='#1f77b4',
      borderpad=2,
      showarrow=False
    ))

    fig['layout']['annotations'] = annotations

    fig['layout']['height'] = 600

    # fig['layout']['xaxis'] = dict(
    #   showgrid=False,
    #   showticklabels=False
    # )

    return fig

  # ==============================
  #           Titulo
  # ==============================
  @app.callback(Output('linea-titulo', 'children'), [Input('bubble', 'clickData')])
  def render_content(clickData):
    if not clickData:
      return 'Totales'

    if 'text' in clickData['points'][0]:
      return clickData['points'][0]['text']
    else:
      return 'Totales'