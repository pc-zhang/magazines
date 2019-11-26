from django.core.management.base import BaseCommand
from polls.models import Magazine, User, Subscribe, Task
from django.utils.timezone import localdate


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Magazine.objects.all().delete()
        User.objects.all().delete()
        Subscribe.objects.all().delete()
        Task.objects.all().delete()

        titles = ["Reader's Digest USA"
            , 'Harvard Business Review'
            , 'Scientific American'
            , 'Bloomberg Businessweek'
            , 'WSJ'
            , 'Time'
            , 'TE'
            , 'FT'
            , 'TWP'
            , 'The New Yorker'
                  ]
        for title in titles:
            if len(Magazine.objects.filter(title=title)) > 0:
                continue
            magazine = Magazine(title=title)
            magazine.save()

        if len(User.objects.filter(uuid='uuid')) == 0:
            user = User(email='xxx', uuid='uuid', key='key', invitor='invitor', expire_date=localdate())
            user.save()
