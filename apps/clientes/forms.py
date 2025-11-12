from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'codigo_cliente', 'telefono', 'email', 
                  'direccion', 'dni', 'cuit', 'condicion_iva', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'codigo_cliente': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Código'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XX-XXXXXXXX-X'}),
            'condicion_iva': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }