from rest_framework import filters, routers, viewsets
from .models import Producto, Cliente, Venta, DetalleVenta
from .serializers import (
    ProductoSerializer,
    ClienteSerializer,
    VentaSerializer,
    DetalleVentaSerializer,
)


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('codigo', 'nombre', 'descripcion')
    ordering_fields = ('nombre', 'precio', 'stock', 'fecha_creacion')
    ordering = ('nombre',)

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('rut', 'nombre', 'email')
    ordering_fields = ('nombre', 'fecha_registro')
    ordering = ('nombre',)

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all().select_related('cliente').prefetch_related('detalles__producto')
    serializer_class = VentaSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('numero_boleta', 'rut_cliente')
    ordering_fields = ('fecha_venta', 'total')
    ordering = ('-fecha_venta',)

class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all().select_related('producto')
    serializer_class = DetalleVentaSerializer

router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'ventas', VentaViewSet)
router.register(r'detalles-venta', DetalleVentaViewSet)