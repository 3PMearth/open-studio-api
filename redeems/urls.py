from django.urls import path, include
from . import views

urlpatterns = [
    path('balance_validate_check/', views.balance_validate_check, name='balance-validate-check'),
    path('redeem_ticket/', views.redeem_ticket, name='ticket-redeem'),
]
