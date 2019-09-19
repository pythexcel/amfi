
from django.core.management.base import BaseCommand, CommandError

from amc.jobs.aum_process import process_aum_history


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("processing history aum for amc")
        process_aum_history()
