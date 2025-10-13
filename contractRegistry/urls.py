from django.urls import path
from . import views

app_name = 'contractRegistry'

urlpatterns = [
    # Principal
    path('', views.index, name='index'),
    
    # Contratos
    path('contract/list/', views.contractList, name='contract_list'),
    path('contract/<int:contract_id>/', views.contractDetail, name='contract_detail'),
    path('contract/register/', views.registerContract, name='register_contract'),
    
    # Versiones
    path('version/list/', views.versionList, name='version_list'),
    path('version/<int:version_id>/', views.versionDetail, name='version_detail'),
    path('version/register/<int:contract_id>/', views.registerVersion, name='register_version'),
     path('version/version_args/<int:version_id>/', views.get_version_args, name='get_version_args'),
    
    # Despliegues
    path('deployed/list/', views.deployedContractList, name='deployed_contract_list'),
    path('deployed/<int:deployed_id>/', views.deployedContractDetail, name='deployed_contract_detail'),
    path('deploy/', views.deployContract, name='deploy_contract'),
    path('deploy/from/version/<int:version_id>/', views.deployContractFromVersion, name='deploy_contract_from_version'),
    path('deploy/sing_and_confirm/<int:deployed_contract_id>/', views.signAndConfirmDeployment, name='sign_and_confirm_deployment'),
    path('deploy/step/final/<int:deployed_contract_id>/', views.final_deployment_step, name='finalize_deployment_step'),
    
    # Redes Blockchain
    path('network/list/', views.networkList, name='network_list'),
    path('network/register/', views.registerNetwork, name='register_network'),
    path('network/edit/<int:pk>/', views.editNetwork, name='edit_network'),
    path('network/delete/<int:pk>/', views.deleteNetwork, name='delete_network'),
]
