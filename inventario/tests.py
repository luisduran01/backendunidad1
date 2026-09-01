"""
Pruebas Unitarias y de Integración para el Caso 2 (Control de Ventas e Inventario)
Evaluación Sumativa 1 - Programación Backend
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import Producto, Cliente, Venta, DetalleVenta
from .validators import validar_rut_chileno, formatear_rut
from .forms import ProductoForm, VentaForm


class ValidadorRutTest(TestCase):
    """
    Pruebas para las estructuras de decisión y algoritmo Módulo 11 del validador de RUT.
    """
    def test_rut_valido(self):
        # RUTs válidos conocidos
        rut_valido_k = "18345675K"
        self.assertEqual(validar_rut_chileno(rut_valido_k), "18345675K")
        self.assertEqual(formatear_rut("18345675K"), "18.345.675-K")

        rut_valido_num = "183456784"
        self.assertEqual(validar_rut_chileno(rut_valido_num), "183456784")
        self.assertEqual(formatear_rut("183456784"), "18.345.678-4")

    def test_rut_invalido_dv(self):
        # Dígito verificador incorrecto
        with self.assertRaises(ValidationError):
            validar_rut_chileno("18345678-9")

    def test_rut_invalido_formato(self):
        # RUT con caracteres no numéricos en el cuerpo
        with self.assertRaises(ValidationError):
            validar_rut_chileno("18ABC678-K")


class ProductoModelTest(TestCase):
    """
    Pruebas para el modelo Producto y estructuras de decisión de stock.
    """
    def setUp(self):
        self.prod_disponible = Producto.objects.create(
            codigo="P001", nombre="Mouse", precio=10000, stock=10
        )
        self.prod_critico = Producto.objects.create(
            codigo="P002", nombre="Teclado", precio=25000, stock=3
        )
        self.prod_agotado = Producto.objects.create(
            codigo="P003", nombre="Monitor", precio=90000, stock=0
        )

    def test_estado_stock(self):
        self.assertEqual(self.prod_disponible.estado_stock(), "Disponible")
        self.assertEqual(self.prod_critico.estado_stock(), "Stock Crítico")
        self.assertEqual(self.prod_agotado.estado_stock(), "Agotado")

    def test_esta_disponible(self):
        self.assertTrue(self.prod_disponible.esta_disponible())
        self.assertFalse(self.prod_agotado.esta_disponible())


class VentaFlowTest(TestCase):
    """
    Pruebas de flujo de venta, descuento de stock y creación de cliente habitual.
    """
    def setUp(self):
        self.client = Client()
        self.producto = Producto.objects.create(
            codigo="TEST-01",
            nombre="Disco SSD 1TB",
            precio=60000,
            stock=5
        )

    def test_venta_con_cliente_habitual_descuenta_stock(self):
        url = reverse('venta_create')
        data = {
            'producto': self.producto.id,
            'cantidad': 2,
            'rut_cliente': '18.345.675-K',
            'es_cliente_habitual': True,
            'nombre_cliente': 'Juan Pérez',
            'email_cliente': 'juan@ejemplo.cl',
            'telefono_cliente': '+56911223344',
        }
        response = self.client.post(url, data)
        # Debe redirigir al detalle de la boleta (302)
        self.assertEqual(response.status_code, 302)

        # Verificar que el stock se descontó (5 - 2 = 3)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)

        # Verificar que se creó el cliente
        cliente = Cliente.objects.get(rut='18.345.675-K')
        self.assertEqual(cliente.nombre, 'Juan Pérez')
        self.assertTrue(cliente.es_habitual)

        # Verificar que se creó la venta y el detalle
        venta = Venta.objects.get(rut_cliente='18.345.675-K')
        self.assertEqual(venta.total, 120000)
        self.assertEqual(venta.detalles.first().cantidad, 2)

    def test_venta_rechazada_por_stock_insuficiente(self):
        url = reverse('venta_create')
        data = {
            'producto': self.producto.id,
            'cantidad': 10, # Mayor al stock de 5
            'rut_cliente': '18.345.675-K',
        }
        response = self.client.post(url, data)
        # Formulario no es válido, vuelve a renderizar (código 200)
        self.assertEqual(response.status_code, 200)
        
        # Stock no debe haber cambiado
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)
        self.assertEqual(Venta.objects.count(), 0)
