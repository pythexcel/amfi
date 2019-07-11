from django.core.management.base import BaseCommand, CommandError

from amc.jobs.portfolio_process import process_data


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("processing porftolio data for amc")
        process_data()
