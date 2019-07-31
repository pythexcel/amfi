from django.core.management.base import BaseCommand, CommandError

from todo.jobs.mf import schedule_daily_nav_download

import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("starting daily nav download")

        schedule_daily_nav_download()
