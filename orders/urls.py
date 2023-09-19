from django.urls import path, include
from . import views

urlpatterns = [
    path('<int:order_id>/', views.OrderListView.as_view(), name='order-detail'),
    path('<int:order_id>/transactions/', views.order_transaction_list, name='order-transaction-list'),
]