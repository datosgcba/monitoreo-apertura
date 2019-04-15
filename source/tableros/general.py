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


# print(app)


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
