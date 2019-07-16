from django.core.management.base import BaseCommand, CommandError

from amc.jobs.ter_process import process_ter


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("processing TER for amc")
        process_ter()
