from django.core.management.base import BaseCommand, CommandError

from todo.jobs.health_check import health_check
from amc.jobs.health_check import health_check as amc_health_check


class Command(BaseCommand):


    def handle(self, *args, **options):
        print("health_check for data related to nav, indexes ")
        amc_health_check()
        # health_check()
