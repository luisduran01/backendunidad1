"""
URL configuration for mi_proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path

from bienvenida.views import inicio, lista_productos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicio/', view=inicio, name='inicio'),
    path('lista_productos/', view=lista_productos, name='lista_productos'),
]