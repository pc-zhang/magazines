from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('invite_page/<invitor_id>/', views.invite_page, name='invite_page'),
    path('update_page/<user_id>/<key>/', views.update_page, name='update_page'),
    path('new_subscribe/<invitor_id>/', views.new_subscribe, name='new_subscribe'),
    path('update_subscribe/<user_id>/<key>/', views.update_subscribe, name='update_subscribe'),
    path('pay/<user_id>/<int:month>/', views.pay, name='pay'),
]