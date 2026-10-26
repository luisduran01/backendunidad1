from rest_framework import serializers
from .models import Producto


class BienvenidaProductoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Producto de la app bienvenida.
    """
    class Meta:
        model = Producto
        fields = '__all__'
