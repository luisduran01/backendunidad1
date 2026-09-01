"""
Configuración del Administrador de Django para la app Inventario
"""
from django.contrib import admin
from .models import Producto, Cliente, Venta, DetalleVenta


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'precio', 'stock', 'estado_stock', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('codigo', 'nombre')
    ordering = ('nombre',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'email', 'telefono', 'es_habitual', 'fecha_registro')
    list_filter = ('es_habitual', 'fecha_registro')
    search_fields = ('rut', 'nombre', 'email')
    ordering = ('nombre',)


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero_boleta', 'rut_cliente', 'cliente', 'fecha_venta', 'total')
    list_filter = ('fecha_venta',)
    search_fields = ('numero_boleta', 'rut_cliente')
    inlines = [DetalleVentaInline]
    readonly_fields = ('numero_boleta', 'fecha_venta', 'total')
