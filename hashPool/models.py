from django.db import models
from contractRegistry.models import DeployedContract # Asegúrate de que esta importación sea correcta

class HashPoolEventLog(models.Model):
    """
    Modelo para registrar eventos emitidos por el contrato TicketManager
    """
    deployed_contract = models.ForeignKey(
        DeployedContract, 
        on_delete=models.CASCADE,
        related_name='event_logs_hashpool', 
        verbose_name="Contrato Desplegado"
    )
    event_name = models.CharField(max_length=100, verbose_name="Nombre del Evento")
    event_data = models.JSONField(verbose_name="Datos del Evento (JSON)")
    transaction_hash = models.CharField(max_length=66, unique=True, verbose_name="Hash de Transacción")
    block_number = models.IntegerField(verbose_name="Número de Bloque")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Log de Evento de Ticket"
        verbose_name_plural = "Logs de Eventos de Tickets"
        ordering = ['-block_number', '-timestamp']

    def __str__(self):
        return f"[{self.event_name}] Block: {self.block_number}"

