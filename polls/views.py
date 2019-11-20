from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login

def mail(request):
    return render(request, 'mail.html', {})


def invite(request):
    return render(request, 'invite.html', {})


def subscribe(request):
    username = request.GET['email']
    password = request.GET['key']
    return render(request, 'subscribe.html', {})
    # user = authenticate(request, username=username, password=password)
    # if user is not None:
    #     login(request, user)
    #     return render(request, 'subscribe.html', {})
    # else:
    #     return render(request, 'subscribe.html', {})


def subscribe_ok(request):
    return render(request, 'subscribe_ok.html', {})


def pay(request):
    return render(request, 'pay.html', {})
