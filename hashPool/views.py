from django.shortcuts import render
# Asegúrate de que las importaciones de la blockchain (w3) y los modelos sean correctas
from kimi_backend.blockchainClient import w3 
from contractRegistry.models import DeployedContract
from django.db.models import Sum 
from events.models import GlobalEventLog

# ==============================================================================
# IMPORTANTE: Reemplaza 'HashPoolEventLog' con tu modelo de log de eventos real.
# Si estás usando un modelo genérico, ajusta el nombre de la importación.
# ==============================================================================

def hashPoolAdminDashboard(request):
    """
    Panel de administración para el contrato Hash Pool.
    Obtiene la configuración del contrato, los eventos recientes y calcula las métricas clave.
    """
    
    try:
        current_contract = DeployedContract.objects.filter(
            base_contract__name='HashPool', 
            is_current = True
        ).latest('updated_at')
        
    except DeployedContract.DoesNotExist:
        context = {
            'error_message': 'No se encontró un contrato "HashPoolAdmin" activo y vigente. Por favor, despliega uno.'
        }
        return render(request, 'hashpool/hashpool_admin_panel.html', context)
    
    
    recent_events = GlobalEventLog.objects.filter(
        deployed_contract=current_contract
    ).order_by('-timestamp')[:10]


    contract_abi = current_contract.contract_version.abi
    
    
    # 4. Calcular Estadísticas de la Pool (Temporalmente con datos quemados)
    
    # ==========================================================================
    # DATOS QUEMADOS TEMPORALES: Reemplazar con lógica real de DB cuando esté lista
    # ==========================================================================
    
    # // LÓGICA COMENTADA Y REEMPLAZADA POR DATOS FIJOS
    # total_deposits = HashPoolEventLog.objects.filter(
    #     deployed_contract=current_contract, 
    #     event_name='Deposit'
    # ).aggregate(
    #     total_amount=Sum('event_data__amount') 
    # )['total_amount'] or 0
    
    # total_pool_transactions = HashPoolEventLog.objects.filter(
    #     deployed_contract=current_contract,
    # ).count()
    
    # Datos de ejemplo para desarrollo
    total_deposits_burned = 150000000000000000000 # Ejemplo: 150 ETH en WEI
    total_pool_transactions_burned = 4500 # Número de transacciones
    
    # ==========================================================================
    
    stats = {
        'total_pool_deposits': total_deposits_burned, 
        'total_pool_transactions': total_pool_transactions_burned,
    }
    
    # 5. Contexto y Renderizado
    context = {
        'contract': current_contract,
        'recent_events': recent_events,
        'abi': contract_abi,
        'stats': stats,
    }
    
    # Renderiza la nueva plantilla de administrador de Hash Pool
    return render(request, 'hashpool/hashpool_admin_panel.html', context)
