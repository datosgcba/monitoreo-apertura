import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import math

def layout (indicadores, data_json):
  datasets_organizacion_cols = [ column for column in indicadores.columns if column.startswith('datasets_organizacion_') ]
  
  for col in datasets_organizacion_cols:
      col_vistas = col.replace('datasets_organizacion_', 'vistas_organizacion_')
      if col_vistas not in indicadores.columns:
          indicadores.insert(1, col_vistas, 0)

  # datasets_categoria_cols = [ column for column in indicadores.columns if column.startswith('datasets_categoria_') ]
  # vistas_categoria_cols = [ indicadores[column.replace('datasets_categoria_', 'vistas_categoria_')] if column.replace('datasets_categoria_', 'vistas_categoria_') in indicadores.columns else 0 for column in datasets_categoria_cols ]
  sizeref = 2.*(indicadores[[ column for column in indicadores.columns if column.startswith('vistas_organizacion_') ]].max().max())/(70**2)
  
  return html.Div(children=[
    dcc.Graph(
      id='dataset_org',
      figure=dict(
        data= [
          go.Scatter(
            y=indicadores[column.replace('datasets_organizacion_', 'recursos_organizacion_')],
            x=indicadores[column],
            name=column.replace('datasets_organizacion_', '').replace('_', ' '),
            mode='markers',
            hoverlabel = dict(namelength = -1),
            marker=dict(
              size=indicadores[column.replace('datasets_organizacion_', 'vistas_organizacion_')],
              sizemode='area',
              sizeref=sizeref,
              sizemin=2,
              opacity=.5
            )
          ) for column in datasets_organizacion_cols
        ],
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
        )
      )
    )
  ])