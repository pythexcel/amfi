from django.core.management.base import BaseCommand, CommandError

from todo.jobs.nse import process_nse_daily
from todo.jobs.bse import process_bse_daily

import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("starting daily index download")

        process_nse_daily()
        process_bse_daily()
