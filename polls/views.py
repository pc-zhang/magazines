from django.shortcuts import get_object_or_404, render
from .models import Subscribe, User, Magazine, Order
import uuid
from django.utils.timezone import localdate
from django.http import Http404
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import qrcode
import qrcode.image.svg
import time
import os
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import datetime
import calendar
from mysite.settings import STATIC_ROOT

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)


def invite_page(request, invitor_id):
    user = get_object_or_404(User, uuid=invitor_id)
    magazines = Magazine.objects.all()
    return render(request, 'invite.html',
                  {'user': user, 'magazines': magazines, 'hidden_email': hide_email(user.email)})


def hide_email(email):
    i = email.find('@')
    return email[:3] + 'xxx' + email[i:]


def new_subscribe(request, invitor_id):
    invitor = get_object_or_404(User, uuid=invitor_id)
    magazines = Magazine.objects.all()
    checked_magazines = [magazine for magazine in magazines if request.POST.get(magazine.title, 'off') == 'on']

    email = request.POST.get('email', 'wrong')

    try:
        validate_email(email)
    except ValidationError as e:
        error_info = "郵件格式錯誤"
        return render(request, 'invite.html',
                      {'hidden_email': hide_email(invitor.email), 'user': invitor, 'magazines': magazines,
                       'error_info': error_info})

    if len(User.objects.filter(email=email)) > 0:
        error_info = "您已註冊"
        return render(request, 'invite.html',
                      {'hidden_email': hide_email(invitor.email), 'user': invitor, 'magazines': magazines,
                       'error_info': error_info})

    if len(checked_magazines) > 3:
        error_info = "最多選擇3種"
        return render(request, 'invite.html',
                      {'hidden_email': hide_email(invitor.email), 'user': invitor, 'magazines': magazines,
                       'error_info': error_info})
    elif len(checked_magazines) < 1:
        error_info = "至少選擇一種"
        return render(request, 'invite.html',
                      {'hidden_email': hide_email(invitor.email), 'user': invitor, 'magazines': magazines,
                       'error_info': error_info})

    user = User(email=email, uuid=uuid.uuid4().hex, key=uuid.uuid4().hex, invitor=invitor_id,
                expire_date=localdate())
    user.save()

    for magazine in checked_magazines:
        subscribe = Subscribe(user=user, magazine=magazine)
        subscribe.save()

    subscribes = Subscribe.objects.filter(user=user)

    return render(request, 'subscribe_ok.html', {'user': user, 'magazines': magazines, 'subscribes': subscribes})


def update_page(request, user_id, key):
    user = get_object_or_404(User, uuid=user_id, key=key)
    magazines = Magazine.objects.all()
    return render(request, 'update_subscribe.html', {'user': user, 'magazines': magazines})


def update_subscribe(request, user_id, key):
    user = get_object_or_404(User, uuid=user_id, key=key)

    magazines = Magazine.objects.all()
    checked_magazines = [magazine for magazine in magazines if request.POST.get(magazine.title, 'off') == 'on']

    if len(checked_magazines) > 3:
        error_info = "最多選擇3種"
        return render(request, 'update_subscribe.html',
                      {'user': user, 'magazines': magazines, 'error_info': error_info})
    elif len(checked_magazines) < 1:
        error_info = "至少選擇一種"
        return render(request, 'update_subscribe.html',
                      {'user': user, 'magazines': magazines, 'error_info': error_info})

    for subscribe in Subscribe.objects.filter(user=user):
        subscribe.delete()

    for magazine in checked_magazines:
        subscribe = Subscribe(user=user, magazine=magazine)
        subscribe.save()

    subscribes = Subscribe.objects.filter(user=user)

    return render(request, 'subscribe_ok.html', {'user': user, 'magazines': magazines, 'subscribes': subscribes})


def pay(request, user_id, month):
    user = get_object_or_404(User, uuid=user_id)
    if month not in [1, 3, 6, 12]:
        raise Http404("Question does not exist")

    try:
        order = Order.objects.get(user=user, month=month)
    except Order.DoesNotExist:
        rpc_user = 'whoami'
        rpc_password = 'uf94kgj3FWT9jovL3gAM967mies3E'
        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (rpc_user, rpc_password))
        addresses = rpc_connection.batch_([['getnewaddress']])
        address = addresses[0]

        order = Order(user=user, month=month, address=address, amount=1)
        order.save()
    except:
        raise Http404('支付系統維護中，請耐心等待')

    factory = qrcode.image.svg.SvgFillImage
    btc_address = order.address
    amount = 0.1
    label = '小報童'
    message = '您的郵箱{}，續訂{}個月'.format(user.email, month)
    qr_message = "bitcoin:{}?amount={}&label={}&message={}".format(btc_address, amount, label, message)
    img = qrcode.make(qr_message, image_factory=factory)

    path = STATIC_ROOT + 'payments/{}.svg'.format(btc_address)

    if os.path.isfile(path):
        os.remove(path)
        for i in range(0, 10):
            time.sleep(.1)
            if not os.path.isfile(path):
                break

        if os.path.isfile(path):
            raise Http404("Question does not exist")

    img.save(path)

    for i in range(0, 10):
        time.sleep(.1)
        if os.path.isfile(path):
            new_expire_date = add_months(user.expire_date, month)
            return render(request, 'pay.html', {'user': user, 'btc_address': btc_address, 'qr_message': qr_message, 'new_expire_date': new_expire_date})

    raise Http404("Question does not exist")


def mail(request, user_id, key):
    user = get_object_or_404(User, uuid=user_id, key=key)
    magazines = Magazine.objects.all()
    return render(request, 'mail.html', {'user': user, 'magazines': magazines, 'date': localdate()})
