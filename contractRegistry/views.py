from django.shortcuts import render
from django.http import HttpResponse
from .staticData import STATIC_CONTRACT_DATA
from django.shortcuts import redirect
from .forms import DeployForm, NetworkForm, BaseContractForm

from .models import BaseContract, ContractVersion, DeployedContract

# Create your views here.

def index(request):
    return contractList(request)

def contractList(request):
    contracts = BaseContract.objects.all()
    
    context = {
        'contracts': contracts
    }
    return render(request, 'contractRegistry/contractList.html', context)

def contractDetail(request, contract_id):
    contract_data = STATIC_CONTRACT_DATA 

    context = {
        'contract': contract_data
    }
    return render(request, 'contractRegistry/contractDetail.html', context)

def versionDetail(request, contract_id, version_id):
    return HttpResponse(f"Details of version {version_id} for contract {contract_id} will be displayed here.")

def deployedContractDetail(request, deployed_id):
    return HttpResponse(f"Details of deployed contract {deployed_id} will be displayed here.")

def registerContract(request):
    if request.method == "POST":
        contract_name = request.POST.get("name")
        print( "Contract Name:", contract_name )  # Debugging line
        contract_description = request.POST.get("descripcion")
        
        new_contract = BaseContract(name=contract_name, descripcion=contract_description)
        new_contract.save()
        contract_id = new_contract.id
        
        return redirect('contractRegistry:contract_detail', contract_id=contract_id)
    
    
    form = BaseContractForm()
    context = {
        'form': form   
    }
    return render(request, 'contractRegistry/register_contract.html', context=context)

def registerVersion(request, contract_id):
    if request.method == "POST":
        version_name = request.POST.get("version_name")
        version_id = 1

        return redirect('contractRegistry:contract_detail', contract_id=contract_id)
    contract_data = STATIC_CONTRACT_DATA
    context = {
        'contract_id': contract_id,
        'contract': contract_data
    }
    return render(request, 'contractRegistry/register_version.html', context)

def deployContract(request):
    deploy_form = DeployForm()
    add_network_form = NetworkForm()

    context = {
        'deploy_form': deploy_form,
        'add_network_form': add_network_form,
        # Necesitarás pasar cualquier otra variable necesaria, como el ContractVersion
    }
    
    return render(request, 'contractRegistry/deploy_version.html', context)