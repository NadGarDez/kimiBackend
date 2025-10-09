# contractRegistry/urls.py

from django.urls import path
from . import views

app_name = 'system_address_manager'

urlpatterns = [
    path('', views.index, name='index'),
    path('addresses/', views.AuthorizedAddressListView.as_view(), name='address_list'), 
    path('addresses/add/', views.AuthorizedAddressCreateView.as_view(), name='address_create'),
    path('addresses/<int:pk>/', views.AuthorizedAddressDetailView.as_view(), name='address_detail'),
    path('addresses/<int:pk>/edit/', views.AuthorizedAddressUpdateView.as_view(), name='address_update'),
    path('addresses/<int:pk>/delete/', views.AuthorizedAddressDeleteView.as_view(), name='address_delete'),
]