from django.core.management.base import BaseCommand, CommandError

from stats.jobs.returns.best_fund import find_best_fund


import datetime


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--fund', nargs='+', type=str, help="Fund Sub Category Name")

    def handle(self, *args, **options):
        print("calculating best fund")

        index = " ".join(options["fund"])
        find_best_fund(index)
