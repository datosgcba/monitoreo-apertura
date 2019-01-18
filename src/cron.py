import os
from crontab import CronTab

cron = CronTab(True)

job = cron.new(command="python {}".format("{}indicadores.py".format(os.environ["SOURCE_PATH"])))

job.minute.every(1) # hacerlo semanal

cron.write()
