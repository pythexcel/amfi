from django.core.management.base import BaseCommand, CommandError

from amc.jobs.organize_download import organize_download


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("organizing download folder")
        organize_download()
