from django.core.management.base import BaseCommand, CommandError
from polls.models import Magazine
from os import listdir
from os.path import isfile, join


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('prepath')
        parser.add_argument('path')

    def handle(self, *args, **options):
        prepath = options['prepath']
        path = options['path']

        for magazine in Magazine.objects.all():
            magazine.todayUpdated = False
            magazine.save()

        for f in listdir(prepath + path):
            if f.endswith('.jpg'):
                title = f[0:f.find('-')]
                print(title)
                magazine = Magazine.objects.get(title=title)
                magazine.titleAndDate = f.replace(".jpg", "")
                magazine.thumbnailPath = join(path, f)
                magazine.todayUpdated = True
                magazine.save()

