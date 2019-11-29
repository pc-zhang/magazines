from bitcoinrpc.authproxy import AuthServiceProxy
from django.core.management.base import BaseCommand, CommandError
from polls.models import Order
import datetime
import calendar


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('prepath')
        parser.add_argument('path')

    def handle(self, *args, **options):
        rpc_user = 'whoami'
        rpc_password = 'uf94kgj3FWT9jovL3gAM967mies3E'
        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (rpc_user, rpc_password))
        unspents = rpc_connection.batch_([['listunspent']])
        for unspent in unspents:
            address = unspent["address"]
            amount = unspent["amount"]
            print('{}, {}'.format(unspent["address"], unspent["amount"]))
            order = Order.objects.get(address=address)
            if amount > order.amount or (order.amount - amount) / order.amount < 0.1:
                order.user.expire_date = add_months(order.user.expire_date, order.month)
                order.user.save(update_fields=["expire_date"])
                order.delete()

