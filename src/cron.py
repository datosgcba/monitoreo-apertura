import os
from crontab import CronTab

cron = CronTab(True)

job = cron.new(command="python {}".format(os.path.abspath("indicadores.py")))

job.minute.every(1) # hacerlo semanal

cron.write()
