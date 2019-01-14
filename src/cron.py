import os
from crontab import CronTab

cron = CronTab(True)

job = cron.new(command='python /home/franciclo/git/indicadores-portal-datos-abiertos/src/calcula-indicadores.py')
# job = cron.new(command='python /usr/src/calcula-indicadores.py')
job.minute.every(1)

cron.write()
