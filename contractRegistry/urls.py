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
    path('deployed/<int:deployed_id>/', views.deployedContractDetail, name='deployed_contract_detail'),
    path('deploy/', views.deployContract, name='deploy_contract'),
    path('deploy/from/version/<int:version_id>/', views.deployContractFromVersion, name='deploy_contract_from_version'),
    path('network/register/', views.registerNetwork, name='register_network'),

]
