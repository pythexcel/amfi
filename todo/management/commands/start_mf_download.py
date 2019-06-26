from django.core.management.base import BaseCommand, CommandError

from todo.jobs import download_mf_input

import datetime


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--amc', nargs='+', type=str, help="amc id")
        parser.add_argument('--start', nargs='+', type=str,
                            help="start date in format YYYY-MM-DD")
        parser.add_argument('--end', nargs='+', type=str,
                            help="end date in format YYYY-MM-DD")

    def handle(self, *args, **options):
        print("starting mf downloading")

        print("maximum date diff should be 90days only")
        print("amc id ", options["amc"][0])

        start = datetime.datetime.strptime(
            options["start"][0], '%Y-%m-%d')

        end = datetime.datetime.strptime(
            options["end"][0], '%Y-%m-%d')
        print("start date ", start)
        print("end date ", end)
        download_mf_input(options["amc"][0], start, end)
