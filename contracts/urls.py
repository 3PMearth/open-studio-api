from django.urls import path, include
from . import views


urlpatterns = [
    # POST Method only, to create a new token
    path('', views.contract_list_view, name='contract-list'),
]

