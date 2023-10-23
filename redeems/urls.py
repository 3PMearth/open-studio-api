from django.urls import path, include
from . import views

urlpatterns = [
    path('balance_validate_check/', views.balance_validate_check, name='balance-validate-check'),
    path('redeem_ticket/', views.redeem_ticket, name='ticket-redeem'),
    path('verifiers/', views.VerifierListView.as_view(), name='verifier'),
    path('verifiers/<int:verifier_id>/', views.VerifierDetailView.as_view(), name='verifier-detail'),
]
