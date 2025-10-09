from django.urls import path
from . import views

app_name = 'contractRegistry'

urlpatterns = [
    path('', views.index, name='index'),
    path('contract/list/', views.contractList, name='contract_list'),
    path('contract/<int:contract_id>/', views.contractDetail, name='contract_detail'),
    path('contract/register/', views.registerContract, name='register_contract'),
    path('version/<int:version_id>/', views.versionDetail, name='version_detail'),
    path('version/register/<int:contract_id>/', views.registerVersion, name='register_version'),
    path('version/list/', views.versionList, name='version_list'),
    path('deployed/<int:deployed_id>/', views.deployedContractDetail, name='deployed_contract_detail'),
    path('deploy/', views.deployContract, name='deploy_contract'),
    path('deploy/from/version/<int:version_id>/', views.deployContractFromVersion, name='deploy_contract_from_version'),
    path('deployed/list/', views.deployedContractList, name='deployed_contract_list'),
    path('network/register/', views.registerNetwork, name='register_network'),
    path('network/list/', views.networkList, name='network_list'),
    path('api/version_args/<int:version_id>/', views.get_version_args, name='get_version_args'),
]
