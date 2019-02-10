# coding=utf-8
import os
import sys
import dash
import cron
import tablero
import pandas as pd
from ftplib import FTP
from io import StringIO
from multiprocessing import Process

app = dash.Dash()

template = open("template.html", "r") 

app.index_string = template.read()

ftp = FTP(os.environ["FTP_HOST"], os.environ["FTP_USER"], os.environ["FTP_PASS"])
csv_old = StringIO(newline='\n')
ftp.retrlines('RETR /tablero-apertura/indicadores.csv', lambda line: csv_old.write("%s\n" % line))
csv_old.seek(0)

indicadores = pd.read_csv(csv_old)
indicadores['fecha'] = pd.to_datetime(indicadores['fecha'], format='%d/%m/%Y:%H:%M:%S', utc=True)

app.layout = tablero.layout(indicadores)

p = Process(target=cron.run)
p.start()

app.run_server(host='0.0.0.0')