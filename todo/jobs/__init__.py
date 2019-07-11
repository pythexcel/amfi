
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from todo.jobs.nse import process_nse_historial, process_nse_daily
from todo.jobs.bse import process_bse_historial, process_bse_daily
from todo.jobs.mf import download_mf_historical_data, schedule_daily_download_mf

from amc.jobs.portfolio_identify import process_zip_file, identify_amc

scheduler = BackgroundScheduler()

job = scheduler.add_job(download_mf_historical_data, 'interval', minutes=1)
job = scheduler.add_job(process_nse_historial, 'interval', minutes=1)
job = scheduler.add_job(process_bse_historial, 'interval', minutes=1)

job = scheduler.add_job(schedule_daily_download_mf, 'interval', hours=12)
job = scheduler.add_job(process_nse_daily, 'interval', hours=12)
job = scheduler.add_job(process_bse_daily, 'interval', hours=12)


job = scheduler.add_job(process_zip_file, 'interval', days=1)
job = scheduler.add_job(identify_amc, 'interval', days=1)

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
