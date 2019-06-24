from django.core.management.base import BaseCommand, CommandError

from todo.jobs import scheduler


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("scheduling mf downloading")
        scheduler.start()
