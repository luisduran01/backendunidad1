from rest_framework import serializers
from .models import Producto, Cliente, Venta, DetalleVenta


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializador completo para el modelo Producto.
    Incluye campos calculados de estado y disponibilidad.
    """
    estado_stock = serializers.CharField(read_only=True)
    esta_disponible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Producto
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializador completo para el modelo Cliente.
    """
    class Meta:
        model = Cliente
        fields = '__all__'


class DetalleVentaSerializer(serializers.ModelSerializer):
    """
    Serializador para DetalleVenta.
    Expone el nombre y código del producto asociado.
    """
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    producto_codigo = serializers.ReadOnlyField(source='producto.codigo')

    class Meta:
        model = DetalleVenta
        fields = '__all__'


class VentaSerializer(serializers.ModelSerializer):
    """
    Serializador para Venta (Boleta).
    Incluye los detalles anidados de la venta y datos del cliente.
    """
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre')

    class Meta:
        model = Venta
        fields = '__all__'