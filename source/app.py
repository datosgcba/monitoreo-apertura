# coding=utf-8
from _plotly_future_ import v4_subplots
import os
import dash
import cron
import json
import urllib
import dash_core_components as dcc
import dash_html_components as html
from multiprocessing import Process
from dash.dependencies import Input, Output
from tableros import general, badata, organizacion

PID = str(os.getpid())

def can_it_run():
  if os.path.isfile("cron.pid"):
    return False
  else:
    return True

app = dash.Dash()

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

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
  indicadores = json.load(open('indicadores.json'))

  if(pathname == "/" or not pathname):
    return general.layout()

  if(pathname == "/badata"):
    return badata.layout()

  if(pathname.replace("/", "") in [urllib.parse.quote(org) for org in set([x['_id']['organizacion'] for x in indicadores['por_organizacion'] if x['_id']['organizacion']])]):
    return organizacion.layout(pathname)

  return general.layout()

general.callbacks(app)

@app.server.after_request
def after_request(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Server"] = ""
    return response

if __name__ == '__main__':
  if can_it_run():
    Process(target=cron.run).start()
    cron.job()
    app.run_server(port=8080, host='0.0.0.0')
