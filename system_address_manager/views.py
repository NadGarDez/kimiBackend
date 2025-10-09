# contractRegistry/views.py

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import AuthorizedAddress
from .forms import AuthorizedAddressForm


def index(request):
    return render(request, 'authorizedAddress/index.html')

# ====================================================================
# 1. READ (Listar todas las direcciones) - AuthorizedAddressListView
# ====================================================================
class AuthorizedAddressListView(ListView):
    """Muestra una lista de todas las direcciones autorizadas."""
    model = AuthorizedAddress
    template_name = 'authorizedAddress/address_list.html'
    context_object_name = 'addresses'
    paginate_by = 10
    queryset = AuthorizedAddress.objects.all().order_by('-created_at')


# ====================================================================
# 2. READ (Ver detalles de una dirección) - AuthorizedAddressDetailView
# ====================================================================
class AuthorizedAddressDetailView(DetailView):
    """Muestra los detalles de una dirección específica."""
    model = AuthorizedAddress
    template_name = 'authorizedAddress/address_detail.html'
    context_object_name = 'address'


# ====================================================================
# 3. CREATE (Crear una nueva dirección) - AuthorizedAddressCreateView
# ====================================================================
class AuthorizedAddressCreateView(CreateView):
    """Permite crear una nueva dirección autorizada."""
    model = AuthorizedAddress
    form_class = AuthorizedAddressForm
    template_name = 'authorizedAddress/address_form.html'
    # Redirigir a la lista después de crear
    success_url = reverse_lazy('contractRegistry:address_list') 
    
    def form_valid(self, form):
        # Opcional: Convertir la dirección a minúsculas antes de guardar
        form.instance.address = form.instance.address.lower()
        return super().form_valid(form)


# ====================================================================
# 4. UPDATE (Actualizar una dirección existente) - AuthorizedAddressUpdateView
# ====================================================================
class AuthorizedAddressUpdateView(UpdateView):
    """Permite actualizar los detalles de una dirección existente."""
    model = AuthorizedAddress
    form_class = AuthorizedAddressForm
    template_name = 'authorizedAddress/address_form.html'
    context_object_name = 'address'
    # Redirigir a los detalles de la dirección después de actualizar
    # Usamos f-string y lazy para resolver la URL con el pk de la instancia
    def get_success_url(self):
        return reverse_lazy('contractRegistry:address_detail', kwargs={'pk': self.object.pk})
        

# ====================================================================
# 5. DELETE (Eliminar una dirección) - AuthorizedAddressDeleteView
# ====================================================================
class AuthorizedAddressDeleteView(DeleteView):
    """Permite eliminar una dirección autorizada."""
    model = AuthorizedAddress
    template_name = 'authorizedAddress/address_confirm_delete.html'
    context_object_name = 'address'
    # Redirigir a la lista después de eliminar
    success_url = reverse_lazy('contractRegistry:address_list')