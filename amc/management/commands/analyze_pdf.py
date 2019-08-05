from django.core.management.base import BaseCommand, CommandError

from amc.jobs.analyze_pdf import analyze_pdf


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("checking pdf folder")
        analyze_pdf()
