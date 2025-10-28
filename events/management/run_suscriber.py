import asyncio
import json
import time
from asgiref.sync import sync_to_async

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from web3 import AsyncWeb3, WebSocketProvider
from web3.utils.subscriptions import LogsSubscription, LogsSubscriptionContext
from web3.exceptions import InvalidArgument
from web3.contract.async_contract import AsyncContract
from web3.types import LogReceipt

# Importar modelos
from events.models import EventSubscription, GlobalEventLog
from contractRegistry.models import DeployedContract 

class Command(BaseCommand):
    help = 'Inicia el proceso asíncrono de suscripción a eventos de contratos vía WebSocket.'

    def handle(self, *args, **options):
        # 1. Ejecuta el bucle asíncrono principal
        self.stdout.write(self.style.SUCCESS('Iniciando el Gestor de Suscripciones de Eventos...'))
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.run_subscription_manager())
        except KeyboardInterrupt:
            self.stdout.write(self.style.NOTICE('Interrupción detectada. Cerrando el gestor de suscripciones.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Un error inesperado ocurrió: {e}'))

    # --- Función Asíncrona para Guardar en BD (Debe ser síncrona/asíncrona) ---

    @sync_to_async
    def save_log_to_db(self, deployed_contract: DeployedContract, event_name: str, decoded_event: dict, log_receipt: LogReceipt):
        """Guarda el log de evento decodificado en el modelo GlobalEventLog."""
        try:
            tx_hash = log_receipt['transactionHash'].hex()
            
            # 1. Chequeo de duplicados (necesario por posible retransmisión de logs)
            if GlobalEventLog.objects.filter(transaction_hash=tx_hash).exists():
                 self.stdout.write(f"Log de TX {tx_hash[:10]}... ya existe. Ignorando.")
                 return

            # 2. Serializar los argumentos del evento, asegurando la conversión de bytes
            event_args = decoded_event.get('args', {})
            event_data_json = {
                'address': decoded_event.get('address'),
                # Convertir cualquier tipo 'bytes' (como address o hash) a string (hex)
                'args': {k: v.hex() if isinstance(v, bytes) else v for k, v in event_args.items()}, 
            }
            
            # 3. Guardar el log
            GlobalEventLog.objects.create(
                deployed_contract=deployed_contract,
                event_name=event_name,
                event_data=event_data_json,
                transaction_hash=tx_hash,
                block_number=log_receipt['blockNumber'],
            )
            # Usando la nueva estructura para el nombre en el log
            base_name = deployed_contract.contract_version.base_contract.name
            self.stdout.write(self.style.MIGRATE_SUCCESS(
                f"✅ Log guardado: {event_name} del contrato {base_name} en bloque {log_receipt['blockNumber']}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al guardar log en BD: {e}"))

    # --- Handler Asíncrono para Eventos de Logs ---

    async def log_event_handler(self, handler_context: LogsSubscriptionContext) -> None:
        """
        Función que maneja un evento de log entrante del WebSocket.
        """
        log_receipt: LogReceipt = handler_context.result
        
        # Recuperar objetos pasados en el contexto
        contract_instance: AsyncContract = handler_context.handler_context.get('contract_instance')
        db_subscription: EventSubscription = handler_context.handler_context.get('db_subscription')

        if not contract_instance or not db_subscription:
            self.stdout.write(self.style.ERROR("Error: Instancia de Contrato o Suscripción de BD no encontrada en el contexto del handler."))
            return
        
        # El objeto DeployedContract ya contiene todos los datos relacionados (Network, Version, Base) gracias a select_related
        deployed_contract = db_subscription.deployed_contract 

        try:
            # 1. Decodificar el Log (Web3.py)
            event_abi = contract_instance.events[db_subscription.event_name]
            decoded_event = event_abi.process_log(log_receipt)
            
            self.stdout.write(f"🔔 Evento Decodificado: {db_subscription.event_name} en TX {log_receipt['transactionHash'].hex()[:10]}...")

            # 2. Guardar en la base de datos (Usando sync_to_async)
            await self.save_log_to_db(
                deployed_contract=deployed_contract,
                event_name=db_subscription.event_name,
                decoded_event=decoded_event,
                log_receipt=log_receipt
            )

        except InvalidArgument as e:
            self.stdout.write(self.style.WARNING(f"Advertencia de decodificación en contrato {deployed_contract.address}: Log no coincide con ABI de {db_subscription.event_name}. Error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error en el handler de evento: {e}"))

    # --- Bucle principal del Gestor de Suscripciones ---
    
    async def run_subscription_manager(self):
        """
        Bucle principal que inicializa la conexión WS, configura las suscripciones 
        y mantiene el proceso escuchando.
        """
        self.stdout.write("Cargando suscripciones activas y datos de contrato...")
        
        # Select related profundo para obtener todos los datos necesarios en pocas consultas a la BD:
        # DeployedContract -> Network
        # DeployedContract -> ContractVersion -> BaseContract
        active_subscriptions = await sync_to_async(list)(
            EventSubscription.objects.filter(is_active=True).select_related(
                'deployed_contract', 
                'deployed_contract__network',
                'deployed_contract__contract_version',
                'deployed_contract__contract_version__base_contract',
            ).exclude(
                deployed_contract__address__isnull=True  # Excluir si la dirección final no está confirmada
            ).exclude(
                deployed_contract__network__rpc_url__isnull=True # Excluir si no hay URL de nodo
            )
        )

        if not active_subscriptions:
            self.stdout.write(self.style.WARNING("No se encontraron suscripciones activas y válidas. Terminando el proceso."))
            return

        # Agrupar suscripciones por URL de nodo (Network.rpc_url)
        subscriptions_by_node = {}
        for sub in active_subscriptions:
            # La URL del WS ahora proviene de Network
            ws_url = sub.deployed_contract.network.rpc_url 
            if not ws_url or not ws_url.startswith(('ws://', 'wss://')):
                self.stdout.write(self.style.WARNING(f"La URL RPC '{ws_url}' no parece ser un WebSocket. Omitiendo suscripción para {sub}."))
                continue
                
            if ws_url not in subscriptions_by_node:
                subscriptions_by_node[ws_url] = []
            subscriptions_by_node[ws_url].append(sub)

        # Configurar y agrupar las tareas asíncronas por nodo
        node_tasks = []
        for ws_url, subs_list in subscriptions_by_node.items():
            self.stdout.write(f"Conectando a nodo WS: {ws_url} para {len(subs_list)} suscripciones.")
            node_tasks.append(self.setup_node_subscriptions(ws_url, subs_list))

        self.stdout.write(self.style.SUCCESS("Iniciando escucha concurrente en nodos..."))
        # Ejecutar todos los bucles de escucha concurrentemente
        await asyncio.gather(*node_tasks)

    async def setup_node_subscriptions(self, ws_url: str, subs_list: list[EventSubscription]):
        """
        Configura la conexión WebSocket y las suscripciones para un nodo específico.
        """
        while True: # Bucle infinito para reintentar la conexión si falla
            try:
                # Inicializar AsyncWeb3 para este nodo
                async with AsyncWeb3(WebSocketProvider(ws_url)) as w3:
                    
                    configured_subscriptions = []
                    
                    for sub in subs_list:
                        # --- Extracción de datos con la nueva estructura ---
                        # ABI proviene de ContractVersion
                        abi_data = sub.deployed_contract.contract_version.abi
                        # Dirección proviene de DeployedContract
                        contract_address = w3.to_checksum_address(sub.deployed_contract.address)
                        
                        contract_instance = w3.eth.contract(address=contract_address, abi=abi_data)

                        # Obtener el topic del evento. Necesario para el filtro RPC
                        try:
                            event_abi = contract_instance.events[sub.event_name]
                            event_topic = event_abi()._get_event_topic_hash()
                        except (KeyError, ValueError) as e:
                            self.stdout.write(self.style.ERROR(
                                f"El evento '{sub.event_name}' no se encuentra en el ABI de {sub.deployed_contract.contract_version}. Omitiendo."
                            ))
                            continue
                        
                        # Configurar la LogsSubscription
                        logs_subscription = LogsSubscription(
                            label=f"{sub.deployed_contract.contract_version.base_contract.name}:{sub.event_name}@{sub.deployed_contract.network.name}",
                            address=contract_address,
                            topics=[event_topic], # Filtra por el Topic del Evento
                            handler=self.log_event_handler,
                            handler_context={
                                "db_subscription": sub,
                                "contract_instance": contract_instance 
                            },
                            parallelize=True # Permite que las operaciones de DB no bloqueen la recepción de otros eventos
                        )
                        configured_subscriptions.append(logs_subscription)

                    if configured_subscriptions:
                        await w3.subscription_manager.subscribe(configured_subscriptions)
                        self.stdout.write(self.style.SUCCESS(
                            f"🎉 Suscrito exitosamente a {len(configured_subscriptions)} eventos en el nodo {sub.deployed_contract.network.name}."
                        ))
                        
                        # Iniciar el manejo de las suscripciones. Esta línea bloquea el bucle.
                        await w3.subscription_manager.handle_subscriptions()
                    else:
                        self.stdout.write(self.style.WARNING(f"No hay suscripciones válidas para el nodo {ws_url}."))

                    # Si handle_subscriptions termina (raro, pero posible si se cierran los sockets)
                    return 

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error en el bucle del nodo {ws_url}: {e}"))
                self.stdout.write(self.style.NOTICE(f"Reintentando la conexión a {ws_url} en 15 segundos..."))
                await asyncio.sleep(15)
                # El bucle while True asegura el reintento
