from email.headerregistry import Address
from email.message import EmailMessage
from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from django.core.mail import send_mail
import smtplib

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        template = loader.get_template('mail.html')
        context = {}
        content = template.render(context)

        msg = EmailMessage()
        msg["Subject"] = 'magazines'
        msg["From"] = Address("Magazines", "magazines", "helloworld555.site")
        msg.set_content('')
        msg.add_alternative(content, subtype='html')
        msg["To"] = '13520697042@163.com'

        with smtplib.SMTP('localhost') as s:
            s.send_message(msg)

        self.stdout.write(self.style.SUCCESS('Successfully send email'))
