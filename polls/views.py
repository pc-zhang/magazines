from django.shortcuts import get_object_or_404, render
from .models import Subscribe, User, Magazine
import uuid
from django.utils import timezone
from django.http import Http404
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def invite_page(request, invitor_id):
    user = get_object_or_404(User, uuid=invitor_id)
    magazines = Magazine.objects.all()
    return render(request, 'invite.html', {'user': user, 'magazines': magazines})


def new_subscribe(request, invitor_id):
    magazines = Magazine.objects.all()
    checked_magazines = [magazine for magazine in magazines if request.POST.get(magazine.title, 'off') == 'on']

    if len(checked_magazines) > 3:
        raise Http404("最多選擇3種")
    elif len(checked_magazines) < 1:
        raise Http404("至少選擇一種")

    email = request.POST.get('email', 'wrong')
    try:
        validate_email(email)
    except ValidationError as e:
        raise Http404("郵件格式錯誤")

    if len(User.objects.filter(email=email)) > 0:
        raise Http404("您已註冊")

    user = User(email=email, uuid=uuid.uuid4().hex, key=uuid.uuid4().hex, invitor=invitor_id,
                expire_date=timezone.now())
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
        raise Http404("最多選擇3種")
    elif len(checked_magazines) < 1:
        raise Http404("至少選擇一種")

    for subscribe in Subscribe.objects.get(user=user):
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
    return render(request, 'pay.html', {'user': user})
