from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the contractRegistry index.")

def contractList(request):
    return HttpResponse("List of contracts will be displayed here.")

def contractDetail(request, contract_id):
    return HttpResponse(f"Details of contract {contract_id} will be displayed here.")

def versionDetail(request, contract_id, version_id):
    return HttpResponse(f"Details of version {version_id} for contract {contract_id} will be displayed here.")

def deployedContractDetail(request, deployed_id):
    return HttpResponse(f"Details of deployed contract {deployed_id} will be displayed here.")

def registerContract(request):
    return HttpResponse("Contract registration form will be displayed here.")

def registerVersion(request, contract_id):
    return HttpResponse(f"Version registration form for contract {contract_id} will be displayed here.")

def deployContract(request, contract_id, version_id):
    return HttpResponse(f"Deployment form for version {version_id} of contract {contract_id} will be displayed here.")