"""
Configuración del Administrador de Django para la app Inventario
"""
import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Producto, Cliente, Venta, DetalleVenta


class StockRangeFilter(admin.SimpleListFilter):
    title = 'rango de stock'
    parameter_name = 'stock_rango'

    def lookups(self, request, model_admin):
        return (
            ('agotado', 'Agotado (0)'),
            ('critico', 'Crítico (1 a 5)'),
            ('disponible', 'Disponible (más de 5)'),
        )

    def queryset(self, request, queryset):
        filters = {
            'agotado': {'stock': 0},
            'critico': {'stock__range': (1, 5)},
            'disponible': {'stock__gt': 5},
        }
        selected_filter = filters.get(self.value())
        return queryset.filter(**selected_filter) if selected_filter else queryset


@admin.action(description='Exportar productos seleccionados a CSV')
def exportar_productos_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="productos_stock.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(('Código', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Estado', 'Fecha de creación'))
    for producto in queryset.order_by('nombre'):
        writer.writerow((
            producto.codigo,
            producto.nombre,
            producto.descripcion or '',
            producto.precio,
            producto.stock,
            producto.estado_stock(),
            producto.fecha_creacion.isoformat(),
        ))

    return response


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'precio', 'stock', 'estado_stock', 'fecha_creacion')
    list_filter = (StockRangeFilter, 'fecha_creacion')
    search_fields = ('codigo', 'nombre')
    ordering = ('nombre',)
    actions = (exportar_productos_csv,)


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
