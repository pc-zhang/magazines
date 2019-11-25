from email.headerregistry import Address
from email.message import EmailMessage
from django.core.management.base import BaseCommand, CommandError
from django.template import loader
import smtplib
import mimetypes
import os

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        template = loader.get_template('mail.html')
        context = {}
        content = template.render(context)

        msg = EmailMessage()
        msg["Subject"] = '您的WSJ更新了'
        msg["From"] = Address("外刊訂閱", "magazines", "helloworld555.site")
        msg.set_content('')
        msg.add_alternative(content, subtype='html')
        msg["To"] = '13520697042@163.com'

        filename = 'w14.pdf'
        path = os.path.join('.', filename)
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
                               filename=filename)

        with smtplib.SMTP('localhost') as s:
            s.send_message(msg)

        self.stdout.write(self.style.SUCCESS('Successfully send email'))
