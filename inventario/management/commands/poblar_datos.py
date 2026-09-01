"""
Comando personalizado de Django para poblar la base de datos con datos de prueba
Permite verificar de inmediato el funcionamiento del Caso 2 (Control de Ventas e Inventario).
Uso: python manage.py poblar_datos
"""
from django.core.management.base import BaseCommand
from inventario.models import Producto, Cliente, Venta, DetalleVenta
from inventario.validators import formatear_rut


class Command(BaseCommand):
    help = 'Carga datos de prueba para productos, clientes habituales y ventas.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Iniciando carga de datos de prueba..."))

        # 1. Crear Productos
        productos_data = [
            {
                'codigo': 'TECH-001',
                'nombre': 'Mouse Ergonómico Inalámbrico',
                'descripcion': 'Sensor óptico de 1600 DPI, conexión 2.4GHz y batería recargable.',
                'precio': 19990,
                'stock': 15,
            },
            {
                'codigo': 'TECH-002',
                'nombre': 'Teclado Mecánico RGB Switch Blue',
                'descripcion': 'Teclado mecánico retroiluminado con distribución en español.',
                'precio': 45990,
                'stock': 8,
            },
            {
                'codigo': 'TECH-003',
                'nombre': 'Audífonos Gamer con Micrófono',
                'descripcion': 'Sonido envolvente 7.1, almohadillas viscoelásticas y cancelación pasiva.',
                'precio': 29990,
                'stock': 4, # Stock crítico
            },
            {
                'codigo': 'TECH-004',
                'nombre': 'Monitor 24 Pulgadas Full HD 100Hz',
                'descripcion': 'Panel IPS, tiempo de respuesta 1ms, puertos HDMI y DisplayPort.',
                'precio': 119990,
                'stock': 10,
            },
            {
                'codigo': 'TECH-005',
                'nombre': 'Cámara Web Full HD 1080p con Trípode',
                'descripcion': 'Enfoque automático, micrófono dual integrado y tapa de privacidad.',
                'precio': 34990,
                'stock': 0, # Agotado
            },
            {
                'codigo': 'ACC-101',
                'nombre': 'Mousepad XXL Gamer 90x40cm',
                'descripcion': 'Superficie de microfibra de baja fricción y base antideslizante.',
                'precio': 12990,
                'stock': 25,
            },
        ]

        for p_data in productos_data:
            prod, created = Producto.objects.update_or_create(
                codigo=p_data['codigo'],
                defaults=p_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [+] Producto creado: {prod.nombre}"))

        # 2. Crear Clientes Habituales
        clientes_data = [
            {
                'rut': '18.345.675-K',
                'nombre': 'Carlos Muñoz Soto',
                'email': 'carlos.munoz@ejemplo.cl',
                'telefono': '+56 9 8765 4321',
                'es_habitual': True,
            },
            {
                'rut': '12.345.678-5',
                'nombre': 'María Fernanda Rojas',
                'email': 'maria.rojas@ejemplo.cl',
                'telefono': '+56 9 9123 4567',
                'es_habitual': True,
            }
        ]

        for c_data in clientes_data:
            cli, created = Cliente.objects.update_or_create(
                rut=c_data['rut'],
                defaults=c_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [+] Cliente creado: {cli.nombre}"))

        # 3. Registrar Ventas Iniciales de Ejemplo
        cliente_carlos = Cliente.objects.filter(rut='18.345.675-K').first()
        prod_teclado = Producto.objects.filter(codigo='TECH-002').first()
        prod_mouse = Producto.objects.filter(codigo='TECH-001').first()

        if cliente_carlos and prod_teclado:
            # Venta con cliente habitual
            if not Venta.objects.filter(numero_boleta='BOL-100201').exists():
                v1 = Venta.objects.create(
                    numero_boleta='BOL-100201',
                    rut_cliente=cliente_carlos.rut,
                    cliente=cliente_carlos,
                    total=prod_teclado.precio * 1
                )
                DetalleVenta.objects.create(
                    venta=v1,
                    producto=prod_teclado,
                    cantidad=1,
                    precio_unitario=prod_teclado.precio,
                    subtotal=prod_teclado.precio
                )
                self.stdout.write(self.style.SUCCESS("  [+] Venta de ejemplo registrada (Boleta #BOL-100201)"))

        # Venta ocasional (solo RUT)
        if prod_mouse:
            if not Venta.objects.filter(numero_boleta='BOL-100202').exists():
                v2 = Venta.objects.create(
                    numero_boleta='BOL-100202',
                    rut_cliente='18.345.678-4',
                    cliente=None, # Cliente ocasional
                    total=prod_mouse.precio * 2
                )
                DetalleVenta.objects.create(
                    venta=v2,
                    producto=prod_mouse,
                    cantidad=2,
                    precio_unitario=prod_mouse.precio,
                    subtotal=prod_mouse.precio * 2
                )
                self.stdout.write(self.style.SUCCESS("  [+] Venta ocasional registrada (Boleta #BOL-100202)"))

        self.stdout.write(self.style.SUCCESS("\n¡Base de datos inicializada y poblada con éxito!"))
