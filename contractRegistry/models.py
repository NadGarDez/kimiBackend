from django.db import models
from django.db.models import UniqueConstraint, Q

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
    constructor_args_info = models.JSONField(
        default=list, 
        help_text="Lista de nombres y tipos de argumentos del constructor para validación."
    )
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
class DeployedContract(models.Model):
    """
    Registra una instancia de un contrato desplegado en una dirección y red específica. 
    Actúa como fuente de verdad para el contrato activo (Hotfix tracking).
    """
    contract_version = models.ForeignKey(ContractVersion, on_delete=models.PROTECT, related_name='deployments')
    address = models.CharField(max_length=42)  
    deployed_at = models.DateTimeField(auto_now_add=True)
    network = models.ForeignKey(Network, on_delete=models.PROTECT, related_name='deployed_contracts')
    gas_used = models.BigIntegerField(null=True, blank=True)
    is_current = models.BooleanField(default=False) 
    base_contract = models.ForeignKey(BaseContract, on_delete=models.CASCADE, related_name='deployed_instances', editable=False, db_index=False)

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