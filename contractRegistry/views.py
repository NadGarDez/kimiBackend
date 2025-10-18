from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .forms import DeployForm, NetworkForm, BaseContractForm, ContractVersionForm
from .models import BaseContract, ContractVersion, DeployedContract, Network, DeploymentStatus
from django.db import IntegrityError, transaction
import random
import json
from .utils import extract_constructor_inputs_from_abi
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


@require_POST
def editBaseContract(request, pk):
    """
    View para editar el nombre de un Contrato Base existente.
    Solo se permite editar el campo 'name'. Responde con JSON para la petición AJAX.
    """
    contract = get_object_or_404(BaseContract, pk=pk) 
    
    new_name = request.POST.get('name', '').strip()
    
    if not new_name:
        return JsonResponse({'status': 'error', 'message': 'El nombre del contrato no puede estar vacío.'}, status=400)
    
    if new_name == contract.name:
        return JsonResponse({'status': 'success', 'message': f'Contrato {new_name} guardado (no se detectaron cambios).'})

    try:
        contract.name = new_name
        contract.save()
        return JsonResponse({'status': 'success', 'message': f'Contrato {new_name} actualizado con éxito.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error al guardar en BD: {e}'}, status=400)


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
    
    if request.method != "POST":
        deploy_form = DeployForm()
        add_network_form = NetworkForm()
        context = {
            'deploy_form': deploy_form,
            'add_network_form': add_network_form,
        }
        return render(request, 'contractRegistry/deploy_version.html', context)
        
    deploy_form = DeployForm(request.POST)
    add_network_form = NetworkForm() 
    
    params_string = request.POST.get('params', '{}').strip() 
    
    if deploy_form.is_valid():
        
        try:
            params_data = json.loads(params_string)
            print(f"Parsed params_data: {params_data}")
        except json.JSONDecodeError:
            deploy_form.add_error(None, 'El contenido de los parámetros JSON ("params") no es un formato JSON válido. Por favor, corrígelo.')
            
            context = {
                'deploy_form': deploy_form,
                'add_network_form': add_network_form,
            }
            return render(request, 'contractRegistry/deploy_version.html', context)
        
        deployed_contract = DeployedContract()
        
        try:
            with transaction.atomic():
                deployed_contract.contract_version = deploy_form.cleaned_data['version']
                deployed_contract.network = deploy_form.cleaned_data['network']
                deployed_contract.base_contract = deployed_contract.contract_version.base_contract
                deployed_contract.deployerAddress = deploy_form.cleaned_data['deployer']
                deployed_contract.params = params_data
                
                # address = "0x" + ''.join(random.choices('0123456789abcdef', k=40))
                # gas_used = random.randint(100000, 500000)

                # deployed_contract.address = address
                # deployed_contract.gas_used = gas_used
                deployed_contract.is_current = False
                
                deployed_contract.save()
            
            return redirect('contractRegistry:sign_and_confirm_deployment', deployed_contract_id=deployed_contract.pk)
            
        except IntegrityError as e:
            print(f"Database Integrity Error during save: {e}")
            deploy_form.add_error(None, f"Error al guardar el contrato en la base de datos (Integrity Error): {e}")
            
        except Exception as e:
            print(f"Unexpected Error during save: {e}")
            deploy_form.add_error(None, f"Ocurrió un error inesperado al intentar guardar: {e}")

    
    context = {
        'deploy_form': deploy_form,
        'add_network_form': add_network_form,
    }
    return render(request, 'contractRegistry/deploy_version.html', context)
    
    
def deployContractFromVersion(request, version_id):
    """
    Gestiona el despliegue de un contrato a partir de una versión específica.
    Asegura que la información del Contrato Base y la Versión estén disponibles para el template.
    Prepara la entrada del contrato en la BD y redirige al paso de firma.
    """
    contract_version = get_object_or_404(ContractVersion, id=version_id)
    
    base_contract = contract_version.base_contract
    
    if request.method == "POST":
        deploy_form = DeployForm(request.POST) 
        add_network_form = NetworkForm() 
        
        params_string = request.POST.get('params', '{}').strip() 
        params_data = {}
        
        if deploy_form.is_valid():
            
            try:
                params_data = json.loads(params_string)
            except json.JSONDecodeError:
                deploy_form.add_error(None, 'El contenido de los parámetros JSON ("params") no es un formato JSON válido. Por favor, corrígelo.')
                
                context = {
                    'deploy_form': deploy_form,
                    'add_network_form': add_network_form,
                }
                return render(request, 'contractRegistry/deploy_version.html', context)
            
            
            try:
                with transaction.atomic(): 
                    deployed_contract = DeployedContract()
                    deployed_contract.contract_version = contract_version
                    deployed_contract.network = deploy_form.cleaned_data['network']
                    deployed_contract.base_contract = base_contract
                    
                    if 'deployer' in deploy_form.cleaned_data:
                        deployed_contract.deployerAddress = deploy_form.cleaned_data['deployer']
                    
                    deployed_contract.params = params_data
                    
                    deployed_contract.is_current = False 
                    
                    deployed_contract.save()
                
                return redirect('contractRegistry:sign_and_confirm_deployment', deployed_contract_id=deployed_contract.pk)
                
            except IntegrityError as e:
                print(f"Database Integrity Error during save: {e}")
                deploy_form.add_error(None, f"Error de integridad en la base de datos: {e}")
            except Exception as e:
                print(f"Unexpected Error during save: {e}")
                deploy_form.add_error(None, f"Ocurrió un error inesperado al intentar guardar: {e}")
        

    else:
        deploy_form = DeployForm(initial={'version': contract_version.pk, 'base_contract': base_contract.pk})
        add_network_form = NetworkForm() 
        
    
    context = {
        'deploy_form': deploy_form,
        'add_network_form': add_network_form,
        'contract_version': contract_version, 
        'base_contract': base_contract, 
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

@require_POST
def editNetwork(request, pk):
    """View para editar una Network existente.
    La PK se pasa a través de la URL.
    Esta vista está optimizada para ser llamada por la acción 'Guardar Cambios' del modal.
    """
    network = get_object_or_404(Network, pk=pk) 

    form = NetworkForm(request.POST, instance=network)
    
    if form.is_valid():
        form.save()
        return redirect('contractRegistry:network_list') 
    else:
        return JsonResponse({'status': 'error', 'message': 'Datos de formulario no válidos.'}, status=400)
    

@require_POST
def deleteNetwork(request, pk):
    """View para eliminar una Network. Solo acepta peticiones POST (ideal para AJAX)."""
    
    network = get_object_or_404(Network, pk=pk)
    network_name = network.name 
    
    try:
        network.delete()
        return JsonResponse({'status': 'success', 'message': f'Red {network_name} eliminada.'})
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'No se pudo eliminar la red.'}, status=400)


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
    """
    Muestra la lista de contratos desplegados con estatus CONFIRMED,
    ordenados de forma descendente por la fecha de actualización.
    """
    deployed_contracts = DeployedContract.objects.filter(
        status=DeploymentStatus.CONFIRMED 
    ).order_by(
        '-updated_at' 
    )
    
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


def signAndConfirmDeployment(request, deployed_contract_id):
    """
    Prepara la página de confirmación. Obtiene todos los datos necesarios (ABI, Bytecode,
    Args, Red, Deployer) para que el frontend (JavaScript/MetaMask) inicie la transacción.
    """
    try:
        deployed_contract = get_object_or_404(DeployedContract, pk=deployed_contract_id)
        version = deployed_contract.contract_version
        
        constructor_args_info = extract_constructor_inputs_from_abi(version.abi)
        print(f"Constructor Args Info: {constructor_args_info}")
        final_params_values = deployed_contract.params if deployed_contract.params else {}
        
       
        context = {
            'deployed_contract': deployed_contract,
            'contract_name': deployed_contract.base_contract.name,
            'version_number': version.version,
            
            'network_rpc_url': deployed_contract.network.rpc_url,
            'chain_id': deployed_contract.network.chain_id,
            'contract_abi': version.abi, 
            'contract_bytecode': version.bytecode,
            'deployer_address': deployed_contract.deployerAddress.address,
            
            'constructor_params_values': final_params_values,
            
            'constructor_inputs': constructor_args_info,
        }
        
        return render(request, 'contractRegistry/sign_and_confirm.html', context)
    
    except Http404:
        raise Http404("El registro de despliegue no existe.")
    except Exception as e:
        # Manejo genérico de errores
        print(f"Error al preparar la página de firma: {e}")
        # Redirigir al inicio o mostrar un error
        return redirect('contractRegistry:index') 


def get_version_args(request, version_id):
    """
    Vista API para obtener los argumentos del constructor de una ContractVersion 
    leyendo directamente su campo ABI.
    """
    try:
        version = ContractVersion.objects.get(pk=version_id)
        
        # 💥 CAMBIO CLAVE: Llamar a la función que parsea el ABI 💥
        args = extract_constructor_inputs_from_abi(version.abi)
        
        return JsonResponse({'args': args})
        
    except ContractVersion.DoesNotExist:
        return JsonResponse({'args': []}, status=404)
        
    except Exception as e:
        # Esto atrapará errores del ORM o errores no manejados en la función auxiliar
        return JsonResponse({'error': f"Error interno del servidor: {e}"}, status=500)
    
    
@require_POST
def final_deployment_step(request, deployed_contract_id):
    """
    Vista API para que el frontend llame una vez que la transacción de despliegue 
    ha sido confirmada en la red. Actualiza el registro con la dirección, estado, 
    y asegura que SÓLO esta instancia quede marcada como 'is_current=True'.
    """
    
    try:
        # 1. Obtener el objeto DeployedContract
        deployed_contract = DeployedContract.objects.get(pk=deployed_contract_id)
        
        data = json.loads(request.body)
        contract_address = data.get('contract_address')
        gas_used = data.get('gas_used')
        
        if not contract_address or not gas_used:
            return JsonResponse({'error': 'Faltan datos obligatorios (contract_address o gas_used).'}, status=400)
        
        
        with transaction.atomic():
            
            base_contract_id = deployed_contract.base_contract_id
            network_id = deployed_contract.network_id

            DeployedContract.objects.filter(
                base_contract_id=base_contract_id,
                network_id=network_id,
                is_current=True
            ).exclude(pk=deployed_contract.pk).update(is_current=False)

            deployed_contract.address = contract_address
            deployed_contract.gas_used = gas_used
            deployed_contract.status = DeploymentStatus.CONFIRMED
            deployed_contract.is_current = True 
            
            deployed_contract.save()
            
        
        return JsonResponse({'status': 'actualizado', 'message': 'Despliegue confirmado y marcado como actual.'})
    
    except DeployedContract.DoesNotExist:
        return JsonResponse({'error': 'Registro de despliegue no encontrado'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Cuerpo de petición no es JSON válido'}, status=400)
        
    except IntegrityError as e:
        # Esto atraparía errores si, por alguna razón, fallara la desactivación.
        return JsonResponse({'error': f'Error de integridad de base de datos durante la activación: {e}'}, status=409)

    except Exception as e:
        print(f"Error al actualizar el despliegue: {e}")
        return JsonResponse({'error': f'Error interno del servidor: {e}'}, status=500)
