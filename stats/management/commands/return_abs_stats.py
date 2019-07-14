from django.core.management.base import BaseCommand, CommandError

from stats.jobs.returns.abs import one_year_abs_return


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("calculating returns for schemes")
        one_year_abs_return()
