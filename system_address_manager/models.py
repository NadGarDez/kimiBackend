from django.db import models

# Create your models here.
class AuthorizedAddress(models.Model):
    """
    Dirección autorizada para desplegar contratos.
    """
    address = models.CharField(max_length=42, unique=True)  
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.address
