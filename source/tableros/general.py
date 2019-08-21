# coding=utf-8
import dash
import json
import urllib
import datetime
from plotly import tools
import plotly
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

def diasDesdeHoy(num):
  fechas = []
  dt = datetime.datetime.utcnow()
  step = datetime.timedelta(days=1)

  for i in range(num):
    fechas.append(dt.strftime('%Y-%m-%d'))
    dt -= step

  return fechas[::-1]

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
        html.H5(id='linea-titulo'),
        dcc.Graph(id='lineas-de-tiempo'),
        html.Div(id='org-link', className='text-center')
      ])
    ])
  ])

def callbacks (app):
  # ==============================
  #          Reset lineas
  # ==============================
  @app.callback(Output('bubble', 'clickData'), [Input('tabs', 'value')])
  def render_content(tab):
    return {'points': [{'customdata': 'totales'}]}

  # ==============================
  #            Burbujas
  # ==============================
  @app.callback(Output('bubble', 'figure'), [Input('tabs', 'value')])
  def render_content(tab):
    indicadores = json.load(open('indicadores.json'))
    por_tab = indicadores["por_organizacion_ultimo" if tab == 'org' else "por_categoria_ultimo"]
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
  # Link a tablero de organización
  # ==============================
  @app.callback(Output('org-link', 'children'), [Input('bubble', 'clickData')], [State('tabs', 'value')])
  def render_content(clickData, tab):
    if 'text' in clickData['points'][0] and tab == 'org':
      return dcc.Link('Ver tablero', href=urllib.parse.quote(clickData['points'][0]['text']), className='btn btn-link')

  # ==============================
  #       Lineas de tiempo
  # ==============================
  @app.callback(Output('lineas-de-tiempo', 'figure'), [Input('bubble', 'clickData')], [State('tabs', 'value')])
  def render_content(clickData, tab):
    indicadores = json.load(open('indicadores.json'))
    por_tab = indicadores["por_organizacion" if tab == 'org' else "por_categoria"]
    annotations = []

    if 'text' in clickData['points'][0]:
      data = [x for x in por_tab if x['_id']['organizacion' if tab == 'org' else 'categoria'] == clickData['points'][0]['text']]
    else:
      data = indicadores["por_totales"]
    
    fechas = diasDesdeHoy(len(data))

    fig = plotly.subplots.make_subplots(
      rows=3,
      cols=1,
      specs=[[{}], [{}], [{}]],
      shared_xaxes=False,
      vertical_spacing=0.1,
      print_grid=False
    )

    # Datasets
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

    # Recursos
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

    # Vistas únicas
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
      text='{} Vistas'.format(data[-1]['vistas_unicas']),
      font=dict(color='white'),
      bgcolor='#1f77b4',
      borderpad=2,
      showarrow=False
    ))

    fig['layout']['annotations'] = annotations

    fig['layout']['height'] = 600

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
