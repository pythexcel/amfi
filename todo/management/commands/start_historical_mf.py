from django.core.management.base import BaseCommand, CommandError

from todo.jobs.mf import download_mf_historical_data

import datetime


class Command(BaseCommand):


    def handle(self, *args, **options):
        print("starting historical mf downloading")

        download_mf_historical_data()
