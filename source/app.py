# coding=utf-8
import os
import dash
import cron
import yaml
import tablero
import pandas as pd
from multiprocessing import Process

with open("../config.yml", 'r') as ymlfile:
  config = yaml.load(ymlfile)

app = dash.Dash()

template = open("template.html", "r") 
app.index_string = template.read()

indicadores = pd.read_csv(config['archivos']['indicadores_csv'])
indicadores['fecha'] = pd.to_datetime(indicadores['fecha'], format='%d/%m/%Y:%H:%M:%S', utc=True)

app.layout = tablero.layout(indicadores)

Process(target=cron.run).start()

app.run_server(port=8080, host='0.0.0.0')