from email.headerregistry import Address
from email.message import EmailMessage
from django.core.management.base import BaseCommand, CommandError
import smtplib
import mimetypes
import os
from os import listdir
from polls.models import Magazine, User, Subscribe, Task
from django.utils.timezone import localdate
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Send mails'

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        path = options['path']
        site = 'http://helloworld555.site/'

        for f in listdir(path):
            if not f.endswith('.pdf'):
                continue

            title = f[0:f.find('-')]
            print(title)
            magazine = Magazine.objects.get(title=title)
            subscribes = Subscribe.objects.filter(magazine=magazine)
            for subscribe in subscribes:
                if localdate() > subscribe.user.expire_date:
                    continue
                tasks = Task.objects.filter(pdf=f, email=subscribe.user.email)
                if len(tasks) > 0:
                    continue
                task = Task(pdf=f, email=subscribe.user.email, sended=False)
                task.save()

        for f in listdir(path):
            if not f.endswith('.pdf'):
                continue

            tasks = Task.objects.filter(pdf=f, sended=False)
            for task in tasks:
                user = User.objects.get(email=task.email)
                content = render_to_string('mail.html', {'user': user, 'magazines': Magazine.objects.all(), 'date': localdate(), 'site': site})
                ok = self.send(path, f, task.email, content)
                if ok:
                    task.sended = True
                    task.save()

    def send(self, pdfPath, pdf, email, content):
        title = pdf[0:pdf.find('-')]

        msg = EmailMessage()
        msg["Subject"] = '您的{}更新了'.format(title)
        msg["From"] = Address("小報童", "newsboy", "newsboy.site")
        msg.set_content('')
        msg.add_alternative(content, subtype='html')
        msg["To"] = email

        path = os.path.join(pdfPath, pdf)
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(path, 'rb') as fp:
            msg.add_attachment(fp.read(),
                               maintype=maintype,
                               subtype=subtype,
                               filename=pdf)

        with smtplib.SMTP('localhost') as s:
            s.send_message(msg)

        self.stdout.write(self.style.SUCCESS('send {} to {}'.format(pdf, email)))
        return 'ok'
