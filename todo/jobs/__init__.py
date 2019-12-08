
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from todo.jobs.nse import process_nse_historial, process_nse_daily
from todo.jobs.bse import process_bse_historial, process_bse_daily
from todo.jobs.mf import download_mf_historical_data, schedule_daily_nav_download

from amc.jobs.portfolio_process import process_zip_file as process_amc_portfolio_data
from stats.jobs.returns.abs import abs_return,index_abs_return

from amc.jobs.ter_process import start_process

from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger


from amc.jobs.aum_process import start_process as aum_daily_process

scheduler = BackgroundScheduler()


# trigger2 = OrTrigger([CronTrigger(hour=4, minute=0),CronTrigger(hour=16, minute=0)])

# job_mf_historical = scheduler.add_job(download_mf_historical_data, trigger2)

job_mf_historical = scheduler.add_job(
    download_mf_historical_data, 'interval', days=1)

process_nse_historial = scheduler.add_job(process_nse_historial, OrTrigger(
    [CronTrigger(hour=14, minute=22), CronTrigger(hour=14, minute=22)]))
process_bse_historial = scheduler.add_job(process_bse_historial, OrTrigger(
    [CronTrigger(hour=3, minute=15), CronTrigger(hour=15, minute=15)]))
#job = scheduler.add_job(process_nse_historial, "interval", hours=10)
#job = scheduler.add_job(process_bse_historial, "interval", hours=15)


schedule_daily_nav_download = scheduler.add_job(
    schedule_daily_nav_download, 'interval', hours=12)
job = scheduler.add_job(process_nse_daily, 'interval', hours=12)
job = scheduler.add_job(process_bse_daily, 'interval', hours=12)


job = scheduler.add_job(process_amc_portfolio_data, "interval", days=1)


job = scheduler.add_job(aum_daily_process, "interval", days=1)

triggerrr = OrTrigger([CronTrigger(hour=12, minute=36),
                     CronTrigger(hour=20, minute=30)])

job = scheduler.add_job(index_abs_return, triggerrr)

trigger = OrTrigger([CronTrigger(hour=18, minute=14),
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
