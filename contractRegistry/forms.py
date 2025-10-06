# contractRegistry/forms.py

from django import forms
from .models import BaseContract, ContractVersion, Network

# Estilo Base para los campos (para usar las clases de Bootstrap)
WIDGET_CLASSES = {
    'class': 'form-control bg-dark text-light border border-info'
}

class ContractVersionForm(forms.ModelForm):
    """Formulario para registrar una nueva versión de un contrato base."""
    class Meta:
        model = ContractVersion
        fields = ['base_contract', 'version', 'bytecode', 'abi', 'constructor_args_info']
        
        widgets = {
            'version': forms.TextInput(attrs=WIDGET_CLASSES),
            
            'bytecode': forms.Textarea(attrs={**WIDGET_CLASSES, 'rows': 6}),
            
            'abi': forms.Textarea(attrs={**WIDGET_CLASSES, 'rows': 8}),
            
            'constructor_args_info': forms.Textarea(attrs={**WIDGET_CLASSES, 'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            current_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = current_classes.replace('border-info', 'border-success')
        
        if 'initial' in kwargs and 'base_contract' in kwargs['initial']:
            self.fields['base_contract'].widget = forms.HiddenInput()
        elif 'data' in kwargs and kwargs['data'].get('base_contract'):
            self.fields['base_contract'].widget = forms.HiddenInput()
        
        self.fields['abi'].widget.attrs['placeholder'] = '[{"type": "constructor", "inputs": []}, ...]'
        self.fields['constructor_args_info'].widget.attrs['placeholder'] = '[{"name": "tokenAddress", "type": "address"}, ...]'


class BaseContractForm(forms.ModelForm):
    """Formulario para registrar un nuevo contrato base (lógico)."""
    class Meta:
        model = BaseContract
        fields = ['name', 'descripcion']
        
        widgets = {
            'name': forms.TextInput(attrs=WIDGET_CLASSES),
            'descripcion': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe el propósito general y el estándar del contrato (ej. ERC-20, Contrato de Administración).',
                **WIDGET_CLASSES 
            }),
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
            field.widget.attrs['class'] = current_classes