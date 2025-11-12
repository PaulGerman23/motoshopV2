from django import forms
from .models import Producto, Categoria, Proveedor

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'estado': forms.Select(attrs={'class': 'form-select'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['razon_social', 'codigo_proveedor', 'cuit', 'nombre_contacto', 
                  'telefono', 'direccion', 'email', 'condicion_iva', 'estado']
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razón Social'}),
            'codigo_proveedor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Código'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XX-XXXXXXXX-X'}),
            'nombre_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de contacto'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'condicion_iva': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'descripcion', 'precio_costo', 'precio_venta', 
                  'stock', 'categoria', 'proveedor', 'estado']
        widgets = {
            'codigo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Código del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }