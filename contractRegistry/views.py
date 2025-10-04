from django.shortcuts import render
from django.http import HttpResponse
from .staticData import STATIC_CONTRACT_DATA
from django.shortcuts import redirect

# Create your views here.

def index(request):
    return contractList(request)

def contractList(request):
    return render(request, 'contractRegistry/contractList.html')

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
        contract_id = 1 
        
        return redirect('contractRegistry:contract_detail', contract_id=contract_id)
    
    return render(request, 'contractRegistry/register_contract.html')

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

def deployContract(request, contract_id, version_id):
    return HttpResponse(f"Deployment form for version {version_id} of contract {contract_id} will be displayed here.")