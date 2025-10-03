from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contract/list/', views.contract_list, name='contract_list'),
    path('contract/<int:contract_id>/', views.contract_detail, name='contract_detail'),
    path('contract/register/', views.register_contract, name='register_contract'),
    path('version/<int:version_id>/', views.version_detail, name='version_detail'),
    path('version/register/<int:contract_id>/', views.register_version, name='register_version'),
    path('deployed/<int:deployed_id>/', views.deployed_contract_detail, name='deployed_contract_detail'),
    path('deploy/<int:contract_id>/<int:version_id>/', views.deploy_contract, name='deploy_contract'),
]
