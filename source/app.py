# coding=utf-8
import dash
import cron
import urllib
import dash_core_components as dcc
import dash_html_components as html
from multiprocessing import Process
from dash.dependencies import Input, Output
from werkzeug.contrib.cache import FileSystemCache
from tableros import general, badata, organizacion

cache = FileSystemCache(cache_dir="./.cache")

Process(target=cron.run).start()
cron.job()

app = dash.Dash()
template = open("template.html", "r")

app.index_string = template.read()
app.config['suppress_callback_exceptions'] = True
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

# ==============================
#           Router
# ==============================
@app.callback(dash.dependencies.Output('page-content', 'children'), [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
  indicadores = cache.get('indicadores')

  if(pathname == "/" or not pathname):
    return general.layout()

  if(pathname == "/badata"):
    return badata.layout()

  if(pathname.replace("/", "") in [urllib.parse.quote(org) for org in set([x['_id']['organizacion'] for x in indicadores['por_organizacion']])]):
    return organizacion.layout(pathname)

  return general.layout()

general.callbacks(app)

app.run_server(port=8080, host='0.0.0.0', debug=True)