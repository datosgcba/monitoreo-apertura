# coding=utf-8
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

indicadores = pd.read_csv("{}indicadores.csv".format(os.environ["SOURCE_PATH"]))
indicadores['fecha'] = pd.to_datetime(indicadores['fecha'], format='%d/%m/%Y:%H:%M:%S', utc=True)

cantidad_datasets_org = [column for column in indicadores.columns if column.startswith('datasets_organizacion_')]
cantidad_datasets_cat = [column for column in indicadores.columns if column.startswith('datasets_categoria_')]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
  dbc.Container([
    dbc.Row([
      dbc.Col([
        html.H2("{} datasets".format(indicadores.tail(1).iloc[0].at['cantidad_datasets']))
      ])
    ]),
    dbc.Row([
      dbc.Col(
        dcc.Graph(
          id='cantidad_datasets_org',
          figure={
            'data': [
              go.Scatter(
                x=indicadores['fecha'],
                y=indicadores[column],
                name=column.replace('datasets_organizacion_', '').replace('_', ' '),
                mode='lines'
              ) for column in [column for column in indicadores.columns if column.startswith('datasets_organizacion_')]
            ],
            'layout': {
              'title': 'Cantidad de datasets por organización',
              'showlegend': False
            }
          }
        )
      ),
      dbc.Col(
        dcc.Graph(
          id='cantidad_datasets_cat',
          figure={
            'data': [
              go.Scatter(
                x=indicadores['fecha'],
                y=indicadores[column],
                name=column.replace('datasets_categoria_', '').replace('_', ' '),
                mode='lines'
              ) for column in [column for column in indicadores.columns if column.startswith('datasets_categoria_')]
            ],
            'layout': {
              'title': 'Cantidad de datasets por categoría'
            }
          }
        )
      )
    ]),
    dbc.Row([
      dbc.Col([
        html.H2("{} recursos".format(indicadores.tail(1).iloc[0].at['cantidad_recursos']))
      ])
    ]),
    dbc.Row([
      dbc.Col(
        dcc.Graph(
          id='cantidad_recursos_org',
          figure={
            'data': [
              go.Scatter(
                x=indicadores['fecha'],
                y=indicadores[column],
                name=column.replace('recursos_organizacion_', '').replace('_', ' '),
                mode='lines'
              ) for column in [column for column in indicadores.columns if column.startswith('recursos_organizacion_')]
            ],
            'layout': {
              'title': 'Cantidad de recursos por organización',
              'showlegend': False
            }
          }
        )
      ),
      dbc.Col(
        dcc.Graph(
          id='cantidad_recursos_cat',
          figure={
            'data': [
              go.Scatter(
                x=indicadores['fecha'],
                y=indicadores[column],
                name=column.replace('recursos_categoria_', '').replace('_', ' '),
                mode='lines'
              ) for column in [column for column in indicadores.columns if column.startswith('recursos_categoria_')]
            ],
            'layout': {
              'title': 'Cantidad de recursos por categoría'
            }
          }
        )
      )
    ])
  ])
])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)