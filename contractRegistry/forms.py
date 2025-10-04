# contractRegistry/forms.py

from django import forms
from .models import BaseContract, ContractVersion, Network

# Estilo Base para los campos (para usar las clases de Bootstrap)
WIDGET_CLASSES = {
    'class': 'form-control bg-dark text-light border border-info'
}

class DeployForm(forms.Form):
    """Formulario para seleccionar el Contrato, Versión y Red antes del despliegue."""
    
    # 1. Contrato Base (Select)
    base_contract = forms.ModelChoiceField(
        queryset=BaseContract.objects.all(),
        label="Contrato Base",
        empty_label="Seleccione un contrato",
        widget=forms.Select(attrs=WIDGET_CLASSES)
    )
    
    # 2. Versión (Select) - Se llenará dinámicamente con JavaScript/AJAX en la práctica
    version = forms.ModelChoiceField(
        # Inicialmente, puede estar vacío o contener todas las versiones
        queryset=ContractVersion.objects.all(),
        label="Versión Registrada",
        empty_label="Seleccione una versión",
        widget=forms.Select(attrs=WIDGET_CLASSES)
    )
    
    # 3. Red (Select)
    network = forms.ModelChoiceField(
        queryset=Network.objects.all(),
        label="Red de Destino",
        empty_label="Seleccione una red existente",
        widget=forms.Select(attrs={
            'class': 'form-control bg-dark text-light border border-info'
        })
    )
    
    # NOTA: Los campos dinámicos del constructor se añadirán con JS/AJAX
    # y se enviarán directamente en la petición POST.
    
class NetworkForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = ['name', 'rpc_url', 'chain_id']
        
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_CLASSES),
            'rpc_url': forms.URLInput(attrs=WIDGET_CLASSES),
            'chain_id': forms.NumberInput(attrs=WIDGET_CLASSES),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añade la clase border-warning específica para este formulario
        for field in self.fields.values():
            current_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = current_classes + ' border-warning'