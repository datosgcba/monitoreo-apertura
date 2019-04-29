import json
import base64
import textwrap
import dash_table
from io import BytesIO
from itertools import groupby
import plotly.graph_objs as go
from wordcloud import WordCloud
import dash_core_components as dcc
import dash_html_components as html
from tableros.organizacion import dias_frecuencias

def layout():
  indicadores = json.load(open('indicadores.json'))
  datasets = indicadores['datasets']

  # ==============================
  #     Barras por publicador
  # ==============================
  publicadores = indicadores['datasets_por_publicador']
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
        height=6000,
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
  #       Barras por fuente
  # ==============================
  fuentes = indicadores['datasets_por_fuente']

  fuentes_yaxis = []
  for x in fuentes:
    fuentes_yaxis.append('<br>'.join(textwrap.wrap(x['_id']['fuente'], width=100)))

  barras_fuentes = dcc.Graph(
    figure=go.Figure(
      data=[go.Bar(
        y=fuentes_yaxis,
        x=[x['datasets'] for x in fuentes],
        orientation = 'h',
      )],
      layout=go.Layout(
        height=6000,
        margin=go.layout.Margin(
          l=600
        ),
        yaxis={
          'categoryorder': 'array',
          'categoryarray': fuentes_yaxis
        }
      )
    ),
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

  # ==============================
  #       Nube de keywords
  # ==============================
  keywords = {x['_id']['keyword']: x['datasets'] for x in indicadores['datasets_por_keyword']}

  buffered_keywords = BytesIO()
  WordCloud(width=500, height=700, background_color='white').generate_from_frequencies(keywords).to_image().save(buffered_keywords, format="JPEG")
  img_str_keywords = base64.b64encode(buffered_keywords.getvalue())
  nube_keywords = html.Img(src="data:image/jpeg;base64,{}".format(img_str_keywords.decode()))

  # ==============================
  #       Nube de búsquedas
  # ==============================
  busquedas = {x['_id']['keyword']: x['datasets'] for x in indicadores['datasets_por_keyword']}

  buffered_busquedas = BytesIO()
  WordCloud(width=500, height=700, background_color='white').generate_from_frequencies(busquedas).to_image().save(buffered_busquedas, format="JPEG")
  img_str_busquedas = base64.b64encode(buffered_busquedas.getvalue())
  nube_busquedas = html.Img(src="data:image/jpeg;base64,{}".format(img_str_busquedas.decode()))

  return html.Div([
    html.Div([
      html.Div([
        html.H3('Actualización', className='text-center'),
        torta_actualizacion,
      ], className='col-xs-4 text-center'),
      html.Div([
        html.H3('Frecuencias', className='text-center'),
        barras_frecuencias,
      ], className='col-xs-4 text-center'),
      html.Div([
        html.H3('Formatos', className='text-center'),
        barras_formatos,
      ], className='col-xs-4 text-center'),
    ], className='row'),
    html.H3('Top 10 datasets desactualizados', className='text-center'),
    tabla_datasets,
    html.Div([
      html.Div([
        html.H3('Keywords', className='text-center'),
        nube_keywords
      ], className='col-xs-6 text-center'),
      html.Div([
        html.H3('Búsquedas', className='text-center'),
        nube_busquedas
      ], className='col-xs-6 text-center'),
    ], className='row margin-bottom-xl'),
    html.Div([
      html.Div([
        html.H3('Publicadores', className='text-center'),
        barras_publicador,
      ], className='col-xs-6 text-center'),
      html.Div([
        html.H3('Fuentes', className='text-center'),
        barras_fuentes,
      ], className='col-xs-6 text-center'),
    ], className='row')
  ], className='container')
