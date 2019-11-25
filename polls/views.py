from django.shortcuts import get_object_or_404, render
from .models import Subscribe, User, Magazine
import uuid
from django.utils import timezone

def invite_page(request, invitor_id):
    user = get_object_or_404(User, uuid=invitor_id)
    return render(request, 'invite.html', {'user': user})


def update_page(request, uuid, key):
    return render(request, 'update_subscribe.html', {})


def new_subscribe(request, invitor_id):
    email = request.POST.get('email', 'wrong')
    user = User(email=email, uuid=uuid.uuid4().hex, key=uuid.uuid4().hex, invitor=invitor_id,
                expire_date=timezone.now())
    user.save()
    return render(request, 'subscribe_ok.html', {})


def update_subscribe(request, uuid, key):
    return render(request, 'subscribe_ok.html', {})


def pay(request, uuid, month):
    return render(request, 'pay.html', {})
