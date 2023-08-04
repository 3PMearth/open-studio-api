from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.request_payment, name='payment_request'),
    path('payment_webhook/', views.payment_webhook, name='payment_webhook'),
]

