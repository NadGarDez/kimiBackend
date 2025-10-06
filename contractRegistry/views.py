from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import DeployForm, NetworkForm, BaseContractForm, ContractVersionForm
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