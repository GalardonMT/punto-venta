from django import forms
from .models import Producto, Categoria

class ProductoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar opción vacía para categoría
        self.fields['categoria'].empty_label = "Sin categoría"
        self.fields['categoria'].required = False
        # Configurar el widget de imagen
        self.fields['imagen'].widget.attrs.update({
            'accept': 'image/*',
            'style': 'display: none;'
        })
    
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'precio', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'categoria': forms.Select(attrs={'class': 'select-categoria'}),
            'precio': forms.NumberInput(attrs={'step': 10}),
        }