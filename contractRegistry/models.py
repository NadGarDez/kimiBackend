from django.db import models
from django.db.models import UniqueConstraint, Q
from system_address_manager.models import AuthorizedAddress as DeployerAddress

#======================================================================
# 1. BaseContract
# ----------------------------------------------------------------------
class BaseContract(models.Model):
    """
    Representa el nombre lógico y auditable de un Smart Contract (ej. 'HashPoolAdmin'). 
    Sirve como carpeta para agrupar todas sus versiones.
    """
    name = models.CharField(max_length=100, unique=True) 
    descripcion = models.TextField(blank=True, help_text="Descripción opcional del contrato base.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# ----------------------------------------------------------------------
# 2. ContractVersion
# ----------------------------------------------------------------------
class ContractVersion(models.Model):
    """
    Almacena los artefactos de código inmutable (Bytecode y ABI) para una versión 
    específica de un contrato base.
    """
    base_contract = models.ForeignKey(BaseContract, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=50) 
    bytecode = models.TextField()                 
    abi = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['base_contract', 'version'], 
                name='unique_version_per_base_contract'
            )
        ]

    def __str__(self):
        return f"{self.base_contract.name} v{self.version}"

# ----------------------------------------------------------------------
# 3. Network
# ----------------------------------------------------------------------
class Network(models.Model):
    """
    Almacena los detalles de conexión de una red blockchain (ej. Sepolia, Mainnet). 
    Proporciona la URL de RPC y el Chain ID para Web3.py.
    """
    name = models.CharField(max_length=100, unique=True)
    rpc_url = models.URLField()
    chain_id = models.PositiveIntegerField(unique=True)
    
    def __str__(self):
        return f"{self.name} (Chain ID: {self.chain_id})"
    

# ----------------------------------------------------------------------
# 4. DeployedContract
# ----------------------------------------------------------------------

class DeploymentStatus(models.TextChoices):
    PENDING_PREPARATION = 'PENDING_PREP', 'Pendiente de Preparación' # (Opcional, se puede omitir si se crea en la vista)
    PENDING_SIGNATURE = 'PENDING_SIGN', 'Esperando Firma del Usuario'
    SENT_TO_NETWORK = 'SENT', 'Transacción Enviada a la Red'
    CONFIRMED = 'CONFIRMED', 'Confirmado y Dirección Final'
    FAILED = 'FAILED', 'Fallo en Despliegue'

class DeployedContract(models.Model):
    """
    Registra una instancia de un contrato desplegado en una dirección y red específica. 
    Actúa como fuente de verdad para el contrato activo (Hotfix tracking).
    """
    contract_version = models.ForeignKey(ContractVersion, on_delete=models.PROTECT, related_name='deployments')
    network = models.ForeignKey(Network, on_delete=models.PROTECT, related_name='deployed_contracts')
    is_current = models.BooleanField(default=False) 
    deployerAddress = models.ForeignKey(DeployerAddress, on_delete=models.PROTECT)
    base_contract = models.ForeignKey(BaseContract, on_delete=models.CASCADE, related_name='deployed_instances', editable=False, db_index=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    params = models.JSONField(blank=True, null=True, help_text="Parámetros del constructor usados en el despliegue.")
    
    
    status = models.CharField(
        max_length=15, 
        choices=DeploymentStatus.choices, 
        default=DeploymentStatus.PENDING_SIGNATURE
    )
    transaction_hash = models.CharField(
        max_length=66,
        null=True, 
        blank=True,
        unique=True 
    )
    raw_tx_data = models.JSONField(
        null=True, 
        blank=True,
        help_text="Datos de la transacción sin firmar, generados por web3.py."
    )
    
    
    
    address = models.CharField(max_length=42, null=True, blank=True)  
    gas_used = models.BigIntegerField(null=True, blank=True)
    
    

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['address', 'network'], 
                name='unique_address_per_network'
            ),
            UniqueConstraint(
                fields=['network', 'base_contract'],
                condition=Q(is_current=True),
                name='unique_deployment_per_base_contract_per_network'
            )
        ]

    def __str__(self):
        return f"{self.contract_version} at {self.address} on {self.network.name}"