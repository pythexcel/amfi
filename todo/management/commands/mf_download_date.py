from django.core.management.base import BaseCommand, CommandError

from todo.jobs import download_mf_input_date

import datetime


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--date', nargs='+', type=str,
                            help="start date in format YYYY-MM-DD")

    def handle(self, *args, **options):
        print("starting mf downloading")

        date = datetime.datetime.strptime(
            options["date"][0], '%Y-%m-%d')

        print("start date ", date)
        download_mf_input_date(date)
