from django.urls import path, include
from . import views


urlpatterns = [
    # POST Method only, to create a new token
    path('', views.contract_list_view, name='contract-list'),
    path('<int:contract_id>/meta', views.contract_metadata_view, name='contract-metadata'),
    path('<int:contract_id>/nft/<int:nft_id>', views.token_metadata_view, name='token-metadata'),
]

