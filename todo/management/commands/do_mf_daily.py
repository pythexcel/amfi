from django.core.management.base import BaseCommand, CommandError

from todo.jobs.mf import schedule_daily_download_mf

import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("starting daily mf download")

        schedule_daily_download_mf()
