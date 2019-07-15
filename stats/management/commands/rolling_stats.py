from django.core.management.base import BaseCommand, CommandError

from stats.jobs.returns.rolling import rolling_return


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("calculating rolling for schemes")
        rolling_return()
