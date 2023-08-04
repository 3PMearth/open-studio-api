from django.urls import path
from . import views


urlpatterns = [
    path('<str:wallet_address>/', views.user_detail_view, name='user-detail'),
    path('', views.user_create_view, name='user-create')
]