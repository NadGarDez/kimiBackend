from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import DeployForm, NetworkForm, BaseContractForm, ContractVersionForm
from .models import BaseContract, ContractVersion, DeployedContract, Network
import random
import string

# Create your views here.

def index(request):
    return render(request, 'contractRegistry/index.html')

def contractList(request):
    contracts = BaseContract.objects.all()
    
    context = {
        'contracts': contracts
    }
    return render(request, 'contractRegistry/contractList.html', context)

def contractDetail(request, contract_id):
    contract = BaseContract.objects.get(id=contract_id)
    print(contract.pk, 'contract_id')
    
    versions = ContractVersion.objects.filter(base_contract=contract)
    deployed_versions = DeployedContract.objects.filter(contract_version__in=versions)
    contract_data = {
        'instance': contract,
        'versions': versions,
        'deployed_versions': deployed_versions,
    }
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
    try:
        base_contract = BaseContract.objects.get(id=contract_id)
    except BaseContract.DoesNotExist:
        from django.shortcuts import get_object_or_404

        base_contract = get_object_or_404(BaseContract, pk=contract_id)

    if request.method == "POST":
        form = ContractVersionForm(request.POST)
        print('Form data:', request.POST)  # Debugging line
        if form.is_valid():
            print("Form is valid")
            new_version = form.save(commit=False)
            new_version.base_contract = base_contract
            new_version.save()
            return redirect('contractRegistry:contract_detail', contract_id=contract_id)
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = ContractVersionForm(initial={'base_contract': contract_id})
    
    context = {
        'contract': base_contract,
        'form': form
    }
    return render(request, 'contractRegistry/register_version.html', context)


def deployContract(request):
    deploy_form = DeployForm()
    add_network_form = NetworkForm()
    
    if request.method == "POST":
        deploy_form = DeployForm(request.POST)
        add_network_form = NetworkForm()  
        if deploy_form.is_valid():
            deployed_contract = DeployedContract()
            
            deployed_contract.contract_version = deploy_form.cleaned_data['version']
            deployed_contract.network = deploy_form.cleaned_data['network']
            deployed_contract.base_contract = deployed_contract.contract_version.base_contract
            address = "0x" + ''.join(random.choices('0123456789abcdef', k=40))
            gas_used = random.randint(100000, 500000)

            deployed_contract.address = address
            deployed_contract.gas_used = gas_used
            deployed_contract.is_current = True
            deployed_contract.save()
            return redirect('contractRegistry:contract_detail', contract_id=deployed_contract.contract_version.base_contract.id)
        else:
            print(deploy_form.errors)

    context = {
        'deploy_form': deploy_form,
        'add_network_form': add_network_form,
        # Necesitarás pasar cualquier otra variable necesaria, como el ContractVersion
    }
    
    return render(request, 'contractRegistry/deploy_version.html', context)


def registerNetwork(request):
    if request.method == "POST":
        form = NetworkForm(request.POST)
        if form.is_valid():
            network = form.save()
            return redirect('contractRegistry:deploy_contract')
    else:
        form = NetworkForm()
    context = {
        'form': form
    }
    return render(request, 'contractRegistry/register_network.html', context)



def deployContractFromVersion(request, version_id):
    try:
        contract_version = ContractVersion.objects.get(id=version_id)
    except ContractVersion.DoesNotExist:
        return HttpResponse("Contract Version not found.", status=404)
    
    if request.method == "POST":
        form = DeployForm(request.POST)
        if form.is_valid():
            deployed_contract = DeployedContract()
            deployed_contract.contract_version = contract_version
            deployed_contract.network = form.cleaned_data['network']
            deployed_contract.base_contract = contract_version.base_contract
            
            address = "0x" + ''.join(random.choices('0123456789abcdef', k=40))
            gas_used = random.randint(100000, 500000)

            deployed_contract.address = address
            deployed_contract.gas_used = gas_used
            deployed_contract.is_current = True
            deployed_contract.save()
            
            return redirect('contractRegistry:contract_detail', contract_id=contract_version.base_contract.id)
    else:
        form = DeployForm(initial={'version': contract_version.id, 'base_contract': contract_version.base_contract.id})
    
    context = {
        'contract_version': contract_version,
        'deploy_form': form,
    }
    return render(request, 'contractRegistry/deploy_version.html', context)

def versionList(request):
    
    versions = ContractVersion.objects.all()
    context = {
        'versions': versions
    }
    return render(request, 'contractRegistry/version_list.html', context)


def deployedContractList(request):
    deployed_contracts = DeployedContract.objects.all()
    context = {
        'deployed_contracts': deployed_contracts
    }
    return render(request, 'contractRegistry/deployed_contract_list.html', context)


def networkList(request):
    all_networks = Network.objects.all()
    context = {
        'networks': all_networks
    }
    return render(request, 'contractRegistry/network_list.html', context)


def get_version_args(request, version_id):
    try:
        version = ContractVersion.objects.get(pk=version_id)
        args = version.constructor_args_info 
        return JsonResponse({'args': args})
    except ContractVersion.DoesNotExist:
        return JsonResponse({'args': []}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)