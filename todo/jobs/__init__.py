
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from todo.jobs.nse import process_nifty_historial, process_nifty_daily
from todo.jobs.mf import download_mf_historical_data, schedule_daily_download_mf


scheduler = BackgroundScheduler()

# job = scheduler.add_job(download_mf_historical_data, 'interval', minutes=1)
job = scheduler.add_job(process_nifty_historial, 'interval', minutes=1)

job = scheduler.add_job(schedule_daily_download_mf, 'interval', hours=12)
job = scheduler.add_job(process_nifty_daily, 'interval', hours=12)

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
