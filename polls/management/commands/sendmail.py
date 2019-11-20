import sys, traceback
from email.headerregistry import Address
from email.message import EmailMessage
from time import sleep
import smtplib
import re
from django.core.management.base import BaseCommand, CommandError
from polls.models import Question as Poll
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('poll_id', type=int)

    def handle(self, *args, **options):
        send_mail(
            'Subject here',
            'Here is the message.',
            'from@example.com',
            ['13520697042@163.com'],
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % options['poll_id']))


regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
def isValidEmail(email):
    if re.search(regex, email):
        return True
    else:
        return False

def message(subject = 'magazines', content = ''):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = Address("Magazines", "magazines", "helloworld555.site")
    msg.set_content('')
    msg.add_alternative(content, subtype = 'html')

    return msg

# def sendmail(email = ''):
#     if not isValidEmail(email):
#         continue
#     msg = message(subject, content)
#     msg["To"] = email
#
#     try:
#         server = smtplib.SMTP_SSL("mail.ustc.edu.cn", 465, context=context)
#         server.login("ustcif@ustc.edu.cn", settings.mail_server_password)
#     except Exception as ex:
#         print(ex)
#         server.quit()
#         sleep(5)
#         continue
#
#     try:
#         server.send_message(msg)
#         print("{} --- sended".format(email))
#     except Exception as ex:
#         print("{} --- failed".format(email))
#         print("Exception in send_message:")
#         print("-" * 60)
#         traceback.print_exc(file=sys.stdout)
#         print("-" * 60)
#
#     server.quit()
