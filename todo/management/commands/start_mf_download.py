from django.core.management.base import BaseCommand, CommandError

from todo.jobs import download_mf


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("starting mf downloading")
        download_mf()
