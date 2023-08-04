from django.urls import path, include
from . import views


urlpatterns = [
    # POST Method only, to create a new token
    path('', views.token_create_view, name='token-create'),
    path('<int:token_id>/', views.token_update_get_view, name='token-update-get'),
    path('asset/<int:asset_id>/', views.asset_update_view, name='asset-update'),
    path('asset/delete/<int:asset_id>/', views.asset_delete_view, name='asset-delete'),
    path('user/<int:user_id>/', views.token_list_view_by_user, name='token-list'),
]

