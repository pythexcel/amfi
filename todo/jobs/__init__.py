
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from todo.jobs.nse import process_nse_historial, process_nse_daily
from todo.jobs.bse import process_bse_historial, process_bse_daily
from todo.jobs.mf import download_mf_historical_data, schedule_daily_nav_download

from amc.jobs.portfolio_process import process_zip_file as process_amc_portfolio_data
from stats.jobs.returns.abs import abs_return

from amc.jobs.ter_process import start_process

from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()


# trigger2 = OrTrigger([CronTrigger(hour=4, minute=0),CronTrigger(hour=16, minute=0)])

# job_mf_historical = scheduler.add_job(download_mf_historical_data, trigger2)

job_mf_historical = scheduler.add_job(
    download_mf_historical_data, 'interval', days=1)

process_nse_historial = scheduler.add_job(process_nse_historial, OrTrigger(
    [CronTrigger(hour=3, minute=0), CronTrigger(hour=15, minute=0)]))
process_bse_historial = scheduler.add_job(process_bse_historial, OrTrigger(
    [CronTrigger(hour=3, minute=15), CronTrigger(hour=15, minute=15)]))

schedule_daily_nav_download = scheduler.add_job(
    schedule_daily_nav_download, 'interval', hours=12)
job = scheduler.add_job(process_nse_daily, 'interval', hours=12)
job = scheduler.add_job(process_bse_daily, 'interval', hours=12)


job = scheduler.add_job(process_amc_portfolio_data, "interval", days=1)

trigger = OrTrigger([CronTrigger(hour=4, minute=0),
                     CronTrigger(hour=23, minute=0)])

job = scheduler.add_job(abs_return, trigger)

trigger2 = OrTrigger([CronTrigger(day=7, hour=4, minute=0),
                      CronTrigger(day=15, hour=4, minute=0),
                      CronTrigger(day=21, hour=4, minute=0)])

job = scheduler.add_job(start_process, trigger2)

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


# print(job_mf_historical.name)
# print(job_mf_historical.next_run_time)

# job_mf_historical.pause()
# i don't think we should have this job running always this always
# this was a one time affair to get all information of amc at a go

# https://apscheduler.readthedocs.io/en/latest/modules/jobstores/base.html#module-apscheduler.jobstores.base
# https://apscheduler.readthedocs.io/en/latest/modules/job.html#module-apscheduler.job
