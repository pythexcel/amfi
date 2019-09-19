from django.core.management.base import BaseCommand, CommandError

from amc.jobs.health_check import update_scheme_clean_name

import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("cleaning names")

        update_scheme_clean_name()
