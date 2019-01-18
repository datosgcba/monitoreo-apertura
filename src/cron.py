import os
from crontab import CronTab

cron = CronTab(user='root')

env_vars = { "data_json_url": os.environ["DATA_JSON_URL"], "source_path": os.environ["SOURCE_PATH"] }

job = cron.new(command="DATA_JSON_URL={data_json_url} SOURCE_PATH={source_path} python {source_path}indicadores.py".format(**env_vars))

job.dow.on('MON')

cron.write()
