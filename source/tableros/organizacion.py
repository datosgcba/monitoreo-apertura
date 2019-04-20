import urllib
import dash_table
from plotly import tools
from itertools import groupby
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from tableros.general import diasDesdeHoy
from werkzeug.contrib.cache import FileSystemCache

cache = FileSystemCache(cache_dir="./.cache")

frecuencias = {
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
    shared_xaxes=True,
    shared_yaxes=True,
    vertical_spacing=0.1
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

  # ==============================
  #      Barras de publicador
  # ==============================
  datasets = [x for x in indicadores['datasets'] if x['organizacion'] == organizacion]
  publicadores = [(k, len(list(v))) for k,v in groupby(datasets, key=lambda x:x['publicador'])]
  desactualizados = [len([x for x in list(v) if x['dias'] > frecuencias[x['frecuencia']]]) for k,v in groupby(datasets, key=lambda x:x['publicador'])]

  datasets_total = go.Bar(
    y=[x[0] for x in publicadores],
    x=[x[1] for x in publicadores],
    name='Datasets',
    orientation = 'h',
    marker = dict(color='#1f77b4')
  )

  datasets_desactualizados = go.Bar(
    y=[x[0] for x in publicadores],
    x=[x for x in desactualizados],
    name='Datasets desactualizados',
    orientation = 'h',
    marker = dict(color='#d62728')
  )

  data = [datasets_desactualizados, datasets_total]

  layout = go.Layout(
    barmode='stack',
    yaxis=dict(automargin=True)
  )

  fig_barras = go.Figure(data=data, layout=layout)
  datasets = [{
        'Titulo': d['titulo'],
        'Frecuencia de actualización': d['frecuencia'],
        'Días desactualizado': int(d['dias']),
        'Fuente': d['fuente'],
        'Publicador': d['publicador'],
        'URL de descarga': d['url']
      } for d in datasets]

  return html.Div([
    html.H2(organizacion, className='text-center'),
    dcc.Graph(figure=fig_lineas),
    html.H3('Publicadores', className='text-center'),
    dcc.Graph(figure=fig_barras),
    html.H3('Datasets', className='text-center'),
    dash_table.DataTable(
      id='table',
      columns=[{"name": i, "id": i} for i in datasets[0].keys()],
      data=datasets,
      style_table={'overflowX': 'scroll'}
    )
  ])