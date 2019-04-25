import urllib
import textwrap
import dash_table
from plotly import tools
from itertools import groupby
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from tableros.general import diasDesdeHoy
from werkzeug.contrib.cache import FileSystemCache

cache = FileSystemCache(cache_dir="./.cache")

dias_frecuencias = {
  "R/P10Y": 360 * 10,
  "R/P4Y": 360 * 4,
  "R/P3Y": 360 * 3,
  "R/P2Y": 360 * 2,
  "R/P1Y": 360,
  "R/P6M": 30 * 6,
  "R/P4M": 30 * 4,
  "R/P3M": 30 * 3,
  "R/P2M": 30 * 2,
  "R/P1M": 30,
  "R/P0.5M": 30 * 0.5,
  "R/P0.33M": 30 * 0.33,
  "R/P1W": 7,
  "R/P0.5W": 7 * 0.5,
  "R/P0.33W": 7 * 0.33,
  "R/P1D": 1,
  "R/PT1H": 1,
  "R/PT1S": 1,
  "eventual": 0
}

def layout(pathname):
  indicadores = cache.get('indicadores')
  organizacion = urllib.parse.unquote(pathname.replace("/", ""))

  # ==============================
  #        Lineas de tiempo
  # ==============================
  indicadores_org = [x for x in indicadores["por_organizacion"] if x['_id']['organizacion'] == organizacion]
  annotations = []

  fechas = diasDesdeHoy(len(indicadores_org))

  fig_lineas = tools.make_subplots(
    rows=3,
    cols=1,
    specs=[[{}], [{}], [{}]],
    shared_yaxes=True,
    vertical_spacing=0.1,
    print_grid=False
  )

  # Datasets
  fig_lineas.append_trace(go.Scatter(
    y=[x['datasets'] for x in indicadores_org],
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
    y=indicadores_org[-1]['datasets'],
    text='{} Datasets'.format(indicadores_org[-1]['datasets']),
    font=dict(color='white'),
    bgcolor='#1f77b4',
    borderpad=2,
    showarrow=False
  ))

  # Recursos
  fig_lineas.append_trace(go.Scatter(
    y=[x['recursos'] for x in indicadores_org],
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
    y=indicadores_org[-1]['recursos'],
    text='{} Recursos'.format(indicadores_org[-1]['recursos']),
    font=dict(color='white'),
    bgcolor='#1f77b4',
    borderpad=2,
    showarrow=False
  ))

  # Vistas únicas
  fig_lineas.append_trace(go.Scatter(
    y=[x['vistas_unicas'] for x in indicadores_org],
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
    y=indicadores_org[-1]['vistas_unicas'],
    text='{} Vistas'.format(indicadores_org[-1]['vistas_unicas']),
    font=dict(color='white'),
    bgcolor='#1f77b4',
    borderpad=2,
    showarrow=False
  ))

  fig_lineas['layout']['annotations'] = annotations

  fig_lineas['layout']['height'] = 600

  lineas_organizacion = dcc.Graph(figure=fig_lineas)

  # ==============================
  #      Barras de publicador
  # ==============================
  datasets = [x for x in indicadores['datasets'] if x['organizacion'] == organizacion]


  # ==============================
  #     Barras por publicador
  # ==============================
  publicadores = [x for x in indicadores['datasets_por_publicador_organizacion'] if x['_id']['organizacion'] == organizacion]
  publicadores_yaxis = []
  for x in publicadores:
    publicadores_yaxis.append('<br>'.join(textwrap.wrap(x['_id']['publicador'], width=100)))

  barras_publicador = dcc.Graph(
    figure=go.Figure(
      data=[go.Bar(
        y=publicadores_yaxis,
        x=[x['datasets'] for x in publicadores],
        orientation = 'h',
      )],
      layout=go.Layout(
        height=3000,
        margin=go.layout.Margin(
          l=600
        ),
        yaxis={
          'categoryorder': 'array',
          'categoryarray': publicadores_yaxis
        }
      )
    ),
  )

  # ==============================
  #    Torta por actualización
  # ==============================
  actualizados = len([x for x in datasets if x['dias'] <= dias_frecuencias[x['frecuencia']]])
  desactualizados = len([x for x in datasets if x['dias'] > dias_frecuencias[x['frecuencia']]])

  torta_actualizacion = dcc.Graph(
    id='graph',
    figure={
      'data': [{
        'values': [actualizados, desactualizados],
        'labels': ['Actualizados', 'Desactualizados'],
        'type': 'pie',
      }]
    }
  )

  # ==============================
  #        Tabla Datasets
  # ==============================
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
    html.H2(organizacion, className='text-center'),
    html.Div([
      html.Div([
        lineas_organizacion,
      ], className='col-xs-8 text-center'),
      html.Div([
        html.H3('Actualización', className='text-center'),
        torta_actualizacion,
      ], className='col-xs-4 text-center')
    ], className='row'),
    html.H3('Datasets', className='text-center'),
    tabla_datasets,
    html.H3('Publicadores', className='text-center'),
    barras_publicador
  ])