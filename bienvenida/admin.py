from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'activo')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('activo',)
    ordering = ('nombre', 'stock')
    list_editable = ('activo',)
    list_per_page = 25