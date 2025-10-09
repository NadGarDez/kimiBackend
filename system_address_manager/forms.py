# contractRegistry/forms.py

from django import forms
from .models import AuthorizedAddress

class AuthorizedAddressForm(forms.ModelForm):
    class Meta:
        model = AuthorizedAddress
        fields = ['address', 'description', 'is_active']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Ej: 0x... (42 caracteres)'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }