"""
Formularios de la aplicación de Inventario y Ventas
Integra django-crispy-forms y validaciones personalizadas.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Producto, Cliente, Venta
from .validators import validar_rut_chileno, formatear_rut


# ==============================================================================
# FORMULARIO 1: PRODUCTO (CREAR / EDITAR)
# ==============================================================================
class ProductoForm(forms.ModelForm):
    """
    Formulario para registrar o editar productos.
    """
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'descripcion', 'precio', 'stock']
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Ej: PROD-101', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Teclado Mecánico RGB', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción o detalles del producto...', 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'placeholder': 'Ej: 15990', 'min': '1', 'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'placeholder': 'Ej: 20', 'min': '0', 'class': 'form-control'}),
        }
        labels = {
            'codigo': 'Código Único del Producto',
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción Opcional',
            'precio': 'Precio Unitario ($ CLP)',
            'stock': 'Cantidad en Stock',
        }

    def clean_codigo(self):
        """
        Validación y estandarización del código de producto.
        """
        codigo = self.cleaned_data.get('codigo', '').strip().upper()
        if not codigo:
            raise ValidationError("El código de producto no puede quedar vacío.")
        return codigo

    def clean_precio(self):
        """
        Estructura de decisión para validar que el precio sea mayor a cero.
        """
        precio = self.cleaned_data.get('precio')
        if precio is None or precio <= 0:
            raise ValidationError("El precio del producto debe ser un valor positivo mayor a 0.")
        return precio

    def clean_stock(self):
        """
        Estructura de decisión para validar que el stock no sea negativo.
        """
        stock = self.cleaned_data.get('stock')
        if stock is None or stock < 0:
            raise ValidationError("El stock disponible no puede ser un número negativo.")
        return stock


# ==============================================================================
# FORMULARIO 2: ACTUALIZACIÓN RÁPIDA DE STOCK
# Permite aumentar o ajustar el stock de un producto específico.
# ==============================================================================
class StockUpdateForm(forms.Form):
    """
    Formulario para ajustar rápidamente las existencias de un producto.
    """
    TIPO_AJUSTE_CHOICES = [
        ('SUMAR', 'Añadir unidades al stock actual (+)'),
        ('REEMPLAZAR', 'Fijar nuevo valor de stock (=)'),
    ]

    tipo_ajuste = forms.ChoiceField(
        choices=TIPO_AJUSTE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Acción a realizar"
    )
    cantidad = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad de unidades'}),
        label="Cantidad de unidades"
    )


# ==============================================================================
# FORMULARIO 3: REGISTRO DE VENTA
# Cumple requerimientos:
# - Registrar venta con RUT de cliente.
# - Validar stock disponible.
# - Guardar datos de cliente si desea ser habitual, o solo pedir RUT para boleta si no.
# ==============================================================================
class VentaForm(forms.Form):
    """
    Formulario dinámico de venta que procesa la compra, la validación de inventario
    y la captura condicional de datos de clientes habituales.
    """
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(stock__gt=0),
        empty_label="-- Seleccione un producto con stock disponible --",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Producto a Vender"
    )
    cantidad = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        label="Cantidad de Unidades"
    )
    rut_cliente = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-K ó 12345678-K'}),
        label="RUT del Cliente para Boleta"
    )
    
    # Checkbox para determinar si se guardan datos como cliente habitual
    es_cliente_habitual = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'toggleHabitual'}),
        label="¿Desea registrar o actualizar como Cliente Habitual?"
    )
    
    # Datos opcionales/condicionales si el cliente desea ser habitual
    nombre_cliente = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del cliente'}),
        label="Nombre del Cliente Habitual"
    )
    email_cliente = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.cl'}),
        label="Correo Electrónico"
    )
    telefono_cliente = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
        label="Teléfono de Contacto"
    )

    def clean_rut_cliente(self):
        """
        Valida el RUT del cliente usando la función con algoritmo Módulo 11.
        """
        rut = self.cleaned_data.get('rut_cliente')
        validar_rut_chileno(rut)
        return formatear_rut(rut)

    def clean(self):
        """
        Validaciones cruzadas mediante estructuras de decisión:
        1. Comprobar que el producto seleccionado tenga stock suficiente.
        2. Si se marcó 'es_cliente_habitual', exigir obligatoriamente el nombre.
        """
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        es_habitual = cleaned_data.get('es_cliente_habitual')
        nombre_cliente = cleaned_data.get('nombre_cliente')

        # Estructura de decisión 1: Validación de stock
        if producto and cantidad:
            if cantidad > producto.stock:
                self.add_error(
                    'cantidad', 
                    f"Stock insuficiente. Solo quedan {producto.stock} unidad(es) de '{producto.nombre}'."
                )

        # Estructura de decisión 2: Validación condicional de cliente habitual
        if es_habitual:
            if not nombre_cliente or not nombre_cliente.strip():
                self.add_error(
                    'nombre_cliente', 
                    "Debe indicar el nombre del cliente si desea guardarlo como cliente habitual."
                )

        return cleaned_data