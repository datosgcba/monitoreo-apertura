import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html

def layout (indicadores):
  vistas_dataset_cols = [column for column in indicadores.columns if column.startswith('vistas_dataset_')]
  datasets_organizacion_cols = [column for column in indicadores.columns if column.startswith('datasets_organizacion_')]
  datasets_categoria_cols = [column for column in indicadores.columns if column.startswith('datasets_categoria_')]

  return html.Div(children=[
    html.H2("Datasets: {}".format(indicadores.tail(1).iloc[0].at['cantidad_datasets']), className='text-center'),
    html.P("Visitas totales del portal: {}".format(int(indicadores.tail(1).iloc[0].at['vistas_totales'])), className='text-center'),
    html.P("Visitas únicas totales del portal: {}".format(int(indicadores.tail(1).iloc[0].at['vistas_totales_unicas'])), className='text-center'),
    dcc.Graph(
      id='cantidad_datasets_org',
      figure={
        'data': [
          go.Scatter(
            x=indicadores['fecha'],
            y=indicadores[column],
            name=column.replace('datasets_organizacion_', '').replace('_', ' '),
            mode='lines'
          ) for column in datasets_organizacion_cols
        ],
        'layout': {
          'title': 'Cantidad de datasets por organización'
        }
      }
    ),
    dcc.Graph(
      id='cantidad_datasets_org_bar',
      figure={
        'data': [
          go.Bar(
            x=[x.replace('datasets_organizacion_', '').replace('_', ' ') for x in datasets_organizacion_cols],
            y=indicadores[datasets_organizacion_cols].tail(1).iloc[0],
          )
        ],
      }
    ),
    dcc.Graph(
      id='cantidad_datasets_cat',
      figure={
        'data': [
          go.Scatter(
            x=indicadores['fecha'],
            y=indicadores[column],
            name=column.replace('datasets_categoria_', '').replace('_', ' '),
            mode='lines'
          ) for column in datasets_categoria_cols
        ],
        'layout': {
          'title': 'Cantidad de datasets por categoría'
        }
      }
    ),
    dcc.Graph(
      id='cantidad_datasets_cat_bar',
      figure={
        'data': [
          go.Bar(
            x=[x.replace('datasets_categoria_', '').replace('_', ' ') for x in datasets_categoria_cols],
            y=indicadores[datasets_categoria_cols].tail(1).iloc[0],
          )
        ],
      }
    ),
    dcc.Graph(
      id='cantidad_vistas_datasets',
      figure={
        'data': [
          go.Scatter(
            x=indicadores['fecha'],
            y=indicadores[column],
            name=column.replace('vistas_dataset_', '').replace('_', ' '),
            mode='lines'
          ) for column in vistas_dataset_cols
        ],
        'layout': {
          'title': 'Cantidad de vistas por dataset'
        }
      }
    ),
    html.H2("Recuros: {}".format(indicadores.tail(1).iloc[0].at['cantidad_recursos']), className='text-center'),
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
          'title': 'Cantidad de recursos por organización'
        }
      }
    ),
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
  ])