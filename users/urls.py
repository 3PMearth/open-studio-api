from django.urls import path
from . import views


urlpatterns = [
    path('wallet/<str:wallet_address>/', views.user_detail_view, name='user-detail'),
    path('s/<str:user_slug>/', views.user_detail_view_by_slug, name='user-detail-slug'),
    path('', views.user_create_view, name='user-create'),
    path('<int:user_id>/', views.user_modify_view, name='user-modify')
]