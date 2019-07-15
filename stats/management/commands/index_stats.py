from django.core.management.base import BaseCommand, CommandError

from stats.jobs.returns.index import abs_return


import datetime


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--index', nargs='+', type=str, help="Index Name")

    def handle(self, *args, **options):
        print("calculating abs for index")

        index = " ".join(options["index"])
        abs_return(index)
