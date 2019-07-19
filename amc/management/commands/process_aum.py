from django.core.management.base import BaseCommand, CommandError

from amc.jobs.aum_process import start_process


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("processing aum for amc")
        start_process()
