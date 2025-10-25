from django.db import models
from contractRegistry.models import DeployedContract, DeployedContractVersion 
# Create your models here.

class GlobalEventLog(models.Model):
    """
    Modelo CENTRALIZADO para registrar eventos emitidos por CUALQUIER contrato.
    
    Este modelo permite a las tareas de fondo guardar logs de TicketManager, 
    HashPoolAdmin, o cualquier otro contrato, simplificando la lógica de 
    selección de modelos.
    """
    deployed_contract = models.ForeignKey(
        DeployedContract, 
        on_delete=models.CASCADE,
        related_name='event_logs', 
        verbose_name="Instancia de Contrato Desplegado"
    )
    event_name = models.CharField(max_length=100, verbose_name="Nombre del Evento")
    event_data = models.JSONField(verbose_name="Datos del Evento (JSON)")
    transaction_hash = models.CharField(max_length=66, unique=True, verbose_name="Hash de Transacción")
    block_number = models.IntegerField(verbose_name="Número de Bloque")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Log de Evento Global"
        verbose_name_plural = "Logs de Eventos Globales"
        ordering = ['-block_number', '-timestamp']

    def __str__(self):
        return f"[{self.event_name}] Contrato: {self.deployed_contract.base_contract.name} | Bloque: {self.block_number}"
    
    
class EventSubscription(models.Model):
    """
    Modelo para gestionar suscripciones a eventos específicos de contratos.
    """
    deployed_contract = models.ForeignKey(
        DeployedContract, 
        on_delete=models.CASCADE,
        related_name='event_subscriptions',
        verbose_name="Instancia de Contrato Desplegado"
    )
    event_name = models.CharField(max_length=100, verbose_name="Nombre del Evento")
    # callback_url = models.URLField(verbose_name="URL de Callback")
    is_active = models.BooleanField(default=True, verbose_name="¿Activa?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Suscripción de Evento"
        verbose_name_plural = "Suscripciones de Eventos"
        unique_together = ('contract_version', 'event_name')

    def __str__(self):
        return f"Suscripción a {self.event_name} para {self.contract_version}" 
