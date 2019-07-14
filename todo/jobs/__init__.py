
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from todo.jobs.nse import process_nse_historial, process_nse_daily
from todo.jobs.bse import process_bse_historial, process_bse_daily
from todo.jobs.mf import download_mf_historical_data, schedule_daily_download_mf

from amc.jobs.portfolio_identify import process_zip_file, identify_amc
from amc.jobs.portfolio_process import process_data as process_amc_portfolio_data
from stats.jobs.returns.abs import abs_return

from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

job = scheduler.add_job(download_mf_historical_data, 'interval', minutes=1)
job = scheduler.add_job(process_nse_historial, 'interval', minutes=1)
job = scheduler.add_job(process_bse_historial, 'interval', minutes=1)

job = scheduler.add_job(schedule_daily_download_mf, 'interval', hours=12)
job = scheduler.add_job(process_nse_daily, 'interval', hours=12)
job = scheduler.add_job(process_bse_daily, 'interval', hours=12)


job = scheduler.add_job(process_zip_file, 'interval', days=1)
job = scheduler.add_job(identify_amc, 'interval', days=1)

job = scheduler.add_job(process_amc_portfolio_data, "interval", minutes=1)

trigger = OrTrigger([CronTrigger(hour=4, minute=0),
                     CronTrigger(hour=23, minute=0)])

job = scheduler.add_job(abs_return, trigger)

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
