from django.core.management.base import BaseCommand, CommandError

from amc.jobs.portfolio_identify import identify_amc


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("processing porftolio data for amc")
        identify_amc()
