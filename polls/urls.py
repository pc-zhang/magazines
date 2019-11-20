from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('mail/', views.mail, name='mail'),
    path('invite/', views.invite, name='invite'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe_ok/', views.subscribe_ok, name='subscribe_ok'),
    path('pay/', views.pay, name='pay'),
]