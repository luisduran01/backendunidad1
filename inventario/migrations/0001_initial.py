# Generated manually for Evaluación Sumativa 1 - Caso 2

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rut', models.CharField(max_length=15, unique=True, verbose_name='RUT del Cliente')),
                ('nombre', models.CharField(max_length=120, verbose_name='Nombre Completo')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Correo Electrónico')),
                ('telefono', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono de Contacto')),
                ('es_habitual', models.BooleanField(default=True, help_text='Marcar si el cliente consiente guardar sus datos para futuras compras.', verbose_name='¿Es Cliente Habitual?')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Identificador único del producto (ej: PROD-001)', max_length=20, unique=True, verbose_name='Código de Producto')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre del Producto')),
                ('descripcion', models.TextField(blank=True, help_text='Detalles o especificaciones del producto', null=True, verbose_name='Descripción')),
                ('precio', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='El precio debe ser mayor a 0.')], verbose_name='Precio Unitario ($ CLP)')),
                ('stock', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0, message='El stock no puede ser negativo.')], verbose_name='Cantidad en Stock')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_boleta', models.CharField(max_length=20, unique=True, verbose_name='N° de Boleta')),
                ('rut_cliente', models.CharField(max_length=15, verbose_name='RUT del Comprador')),
                ('fecha_venta', models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora')),
                ('total', models.IntegerField(default=0, verbose_name='Total Pagado ($ CLP)')),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ventas', to='inventario.cliente', verbose_name='Cliente Asociado')),
            ],
            options={
                'verbose_name': 'Venta',
                'verbose_name_plural': 'Ventas',
                'ordering': ['-fecha_venta'],
            },
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='La cantidad mínima a vender es 1.')], verbose_name='Cantidad')),
                ('precio_unitario', models.IntegerField(verbose_name='Precio Unitario')),
                ('subtotal', models.IntegerField(verbose_name='Subtotal')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detalles', to='inventario.producto', verbose_name='Producto')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='inventario.venta', verbose_name='Venta')),
            ],
            options={
                'verbose_name': 'Detalle de Venta',
                'verbose_name_plural': 'Detalles de Ventas',
            },
        ),
    ]
