"""
Configuración de URLs para la aplicación Inventario y Ventas
"""
from django.urls import path
from . import views

urlpatterns = [
    # Gestión de Catálogo e Inventario de Productos
    path('', views.producto_list, name='home'),
    path('productos/', views.producto_list, name='producto_list'),
    path('productos/nuevo/', views.producto_create, name='producto_create'),
    path('productos/<int:pk>/', views.producto_detail, name='producto_detail'),
    path('productos/<int:pk>/editar/', views.producto_update, name='producto_update'),
    path('productos/<int:pk>/stock/', views.producto_actualizar_stock, name='producto_actualizar_stock'),
    path('productos/<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),

    # Registro y Control de Ventas
    path('ventas/', views.venta_list, name='venta_list'),
    path('ventas/nueva/', views.venta_create, name='venta_create'),
    path('ventas/<int:pk>/boleta/', views.venta_detail, name='venta_detail'),

    # Directorio de Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
]
