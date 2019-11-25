from django.shortcuts import get_object_or_404, render
from .models import Subscribe, User, Magazine
import uuid
from django.utils import timezone
from django.http import Http404


def invite_page(request, invitor_id):
    user = get_object_or_404(User, uuid=invitor_id)
    return render(request, 'invite.html', {'user': user})


def new_subscribe(request, invitor_id):
    email = request.POST.get('email', 'wrong')
    user = User(email=email, uuid=uuid.uuid4().hex, key=uuid.uuid4().hex, invitor=invitor_id,
                expire_date=timezone.now())
    user.save()
    return render(request, 'subscribe_ok.html', {'user': user})


def update_page(request, user_id, key):
    user = get_object_or_404(User, uuid=user_id, key=key)
    return render(request, 'update_subscribe.html', {'user': user})


def update_subscribe(request, user_id, key):
    user = get_object_or_404(User, uuid=user_id, key=key)
    return render(request, 'subscribe_ok.html', {'user': user})


def pay(request, user_id, month):
    user = get_object_or_404(User, uuid=user_id)
    if month not in [1, 3, 6, 12]:
        raise Http404("Question does not exist")
    return render(request, 'pay.html', {'user': user})
