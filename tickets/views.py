from django.shortcuts import render
from kimi_backend.blockchainClient import w3
from contractRegistry.models import DeployedContract, BaseContract
from .models import TicketEventLog
from django.db.models import Sum 


# Create your views here.
def index(request):
    return render(request, 'tickets/index.html')



def ticketDashboard(request):
    # Ejemplo: Obtener el número de bloque actual desde el cliente web3
    
    try:
        current_contract = DeployedContract.objects.filter(base_contract__name='TicketManager', is_current = True).latest('updated_at')
    except DeployedContract.DoesNotExist:
        context = {
            'error_message': 'No se encontró un contrato "TicketManager" activo y vigente. Por favor, despliega uno.'
        }
        return render(request, 'tickets/dashboard.html', context)
    
    
    recent_events = TicketEventLog.objects.filter(
        deployed_contract=current_contract
    ).order_by('-timestamp')[:10]
    
    contract_abi = current_contract.contract_version.abi
    
    
    total_ingresos = TicketEventLog.objects.filter(
        deployed_contract=current_contract, 
        event_name='PurchasedTicket' # Usamos el evento específico de compra
    ).aggregate(
        # Sumamos el campo 'value' dentro del JSONField 'event_data'
        total_amount=Sum('event_data__value') 
    )['total_amount'] or 0
    
    # Contar la cantidad de eventos de tickets comprados (cada evento es un ticket o una compra)
    total_tickets_comprados = TicketEventLog.objects.filter(
        deployed_contract=current_contract,
        event_name='PurchasedTicket'
    ).count()
    
    stats = {
        'total_tickets_vendidos': total_tickets_comprados,
        'ingresos_brutos': total_ingresos, 
    }
    # ----------------------------------------------------
    
    context = {
        'contract': current_contract,
        'recent_events': recent_events,
        'abi': contract_abi,
        'stats': stats,
    }
    return render(request, 'tickets/dashboard.html', context)