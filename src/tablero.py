# coding=utf-8
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

import os
indicadores = pd.read_csv("{}indicadores.csv".format(os.environ["SOURCE_PATH"]))
indicadores['fecha'] = pd.to_datetime(indicadores['fecha'], format='%d/%m/%Y:%H:%M:%S', utc=True)

app = dash.Dash(__name__, app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]))

app.index_string = '''
<!DOCTYPE html>
<html>
  <head>
    {%metas%}
    <title>Monitoreo de apertura de datos</title>
    <link rel="icon" type="image/png" href="/assets/images/favicon.png">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    {%css%}
  </head>
  <body>
    <header id="header">
      <div class="border-gradient">
        <div class="container">
          <div id="logo-sitio">
            <a href="#" style="text-decoration: none;">
              <div id="ba-logo" class="navbar-brand img-responsive" data-original-title="" title=""></div>
            </a>
          </div>
          <div id="nombre-sitio">
            <a href="http://disfrutemosba.buenosaires.gob.ar">
              <h1>Monitoreo de apertura de datos</h1>
            </a>
          </div>
        </div>
      </div>
    </header>
    {%app_entry%}
    <footer id="ba-footer">
      <div class="container">
        <div class="col-md-12 col-sm-12" style="margin-top: -55px;">
          <div class="container-ciudad">
            <a href="http://www.buenosaires.gob.ar/"><img src="/assets/images/logo-bac.svg" class="img-responsive logo_footer_ciudad"></a>
          </div>
        </div>
      </div>
    </footer>
    {%config%}
    {%scripts%}
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js" integrity="sha384-b/U6ypiBEHpOf/4+1nzFpr53nxSS+GLCkfwBdFNTxtclqqenISfwAzpKaMNFNmj4" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
  </body>
</html>
'''

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