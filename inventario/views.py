"""
Vistas de la Aplicación de Control de Ventas e Inventario
Evaluación Sumativa 1 - Programación Backend
"""
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum

from .models import Producto, Cliente, Venta, DetalleVenta
from .forms import ProductoForm, StockUpdateForm, VentaForm


# ==============================================================================
# GESTIÓN DE PRODUCTOS
# ==============================================================================

def producto_list(request):
    """
    Lista todos los productos registrados en el sistema.
    Permite filtrar por texto de búsqueda y por disponibilidad de stock.
    Calcula variables estadísticas del inventario.
    """
    # 1. Variables y obtención de parámetros GET
    query = request.GET.get('q', '').strip()
    solo_disponibles = request.GET.get('disponibles', '')

    productos = Producto.objects.all()

    # 2. Estructura de decisión: Filtro de búsqueda por nombre o código
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query)
        )

    # 3. Estructura de decisión: Filtro de solo productos con stock
    if solo_disponibles == '1':
        productos = productos.filter(stock__gt=0)

    # 4. Operaciones aritméticas y de resumen
    total_productos = productos.count()
    productos_agotados = productos.filter(stock=0).count()
    
    # Cálculo del valor monetario total del inventario
    valor_total_inventario = sum(p.precio * p.stock for p in productos)

    contexto = {
        'productos': productos,
        'query': query,
        'solo_disponibles': solo_disponibles,
        'total_productos': total_productos,
        'productos_agotados': productos_agotados,
        'valor_total_inventario': valor_total_inventario,
    }
    return render(request, 'inventario/producto_list.html', contexto)


def producto_detail(request, pk):
    """
    Muestra los detalles completos de un producto y su historial de ventas.
    """
    producto = get_object_or_404(Producto, pk=pk)
    detalles_ventas = producto.detalles.select_related('venta').order_by('-venta__fecha_venta')[:10]
    
    contexto = {
        'producto': producto,
        'detalles_ventas': detalles_ventas,
    }
    return render(request, 'inventario/producto_detail.html', contexto)


def producto_create(request):
    """
    Registra un nuevo producto en el catálogo.
    Aplica validaciones de formulario y retroalimentación con mensajes.
    """
    # Estructura de decisión para el método HTTP
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            nuevo_producto = form.save()
            messages.success(request, f"¡Producto '{nuevo_producto.nombre}' registrado exitosamente con código {nuevo_producto.codigo}!")
            return redirect('producto_list')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = ProductoForm()

    return render(request, 'inventario/producto_form.html', {'form': form, 'accion': 'Registrar Producto'})


def producto_update(request, pk):
    """
    Actualiza la información general de un producto existente.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            producto_editado = form.save()
            messages.success(request, f"Producto '{producto_editado.nombre}' actualizado correctamente.")
            return redirect('producto_list')
        else:
            messages.error(request, "No se pudo actualizar el producto. Verifique los campos.")
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'inventario/producto_form.html', {
        'form': form, 
        'producto': producto, 
        'accion': 'Editar Producto'
    })


def producto_actualizar_stock(request, pk):
    """
    Permite actualizar específicamente el stock de un producto sumando o fijando existencias.
    Aplica estructuras de decisión y operadores aritméticos.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = StockUpdateForm(request.POST)
        if form.is_valid():
            tipo_ajuste = form.cleaned_data['tipo_ajuste']
            cantidad = form.cleaned_data['cantidad']
            stock_anterior = producto.stock

            # Estructura de decisión: Elegir operación aritmética
            if tipo_ajuste == 'SUMAR':
                producto.stock += cantidad
                mensaje = f"Se agregaron {cantidad} unidades al stock de '{producto.nombre}'. Nuevo stock: {producto.stock}."
            elif tipo_ajuste == 'REEMPLAZAR':
                producto.stock = cantidad
                mensaje = f"Stock de '{producto.nombre}' actualizado de {stock_anterior} a {producto.stock} unidades."
            else:
                messages.error(request, "Tipo de ajuste no reconocido.")
                return redirect('producto_detail', pk=producto.pk)

            producto.save()
            messages.success(request, mensaje)
            return redirect('producto_detail', pk=producto.pk)
    else:
        form = StockUpdateForm()

    return render(request, 'inventario/producto_stock_form.html', {
        'form': form,
        'producto': producto
    })


def producto_delete(request, pk):
    """
    Elimina un producto del sistema previa confirmación.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        nombre = producto.nombre
        try:
            producto.delete()
            messages.success(request, f"El producto '{nombre}' fue eliminado del catálogo correctamente.")
        except Exception as e:
            messages.error(request, f"No se puede eliminar el producto porque tiene ventas asociadas.")
        return redirect('producto_list')

    return render(request, 'inventario/producto_confirm_delete.html', {'producto': producto})


# ==============================================================================
# GESTIÓN DE VENTAS Y CLIENTES
# ==============================================================================

def venta_create(request):
    """
    Registra una nueva venta con las siguientes reglas de negocio:
    1. Validar existencias del producto.
    2. Calcular subtotal y total.
    3. Registrar o actualizar datos si el cliente consiente ser habitual.
    4. Si no, registrar únicamente el RUT para la boleta.
    5. Disminuir el stock del producto vendido mediante operación aritmética.
    """
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            rut_cliente = form.cleaned_data['rut_cliente']
            es_habitual = form.cleaned_data['es_cliente_habitual']
            nombre_cliente = form.cleaned_data['nombre_cliente']
            email_cliente = form.cleaned_data['email_cliente']
            telefono_cliente = form.cleaned_data['telefono_cliente']

            # Operación aritmética: Cálculo del subtotal y total
            precio_unitario = producto.precio
            total_venta = precio_unitario * cantidad

            # Estructura de decisión final de seguridad: Comprobar disponibilidad de stock
            if producto.stock < cantidad:
                messages.error(request, f"Stock insuficiente al procesar la venta. Quedan {producto.stock} unidades.")
                return render(request, 'inventario/venta_form.html', {'form': form})

            # Uso de transacción atómica para asegurar la integridad de la base de datos
            with transaction.atomic():
                cliente_obj = None

                # Estructura de decisión: Gestión de cliente habitual vs ocasional
                if es_habitual:
                    # Buscar si el cliente ya existe por RUT o crearlo
                    cliente_obj, creado = Cliente.objects.get_or_create(
                        rut=rut_cliente,
                        defaults={
                            'nombre': nombre_cliente,
                            'email': email_cliente,
                            'telefono': telefono_cliente,
                            'es_habitual': True,
                        }
                    )
                    # Si ya existía, actualizar sus datos con la información reciente
                    if not creado:
                        cliente_obj.nombre = nombre_cliente or cliente_obj.nombre
                        cliente_obj.email = email_cliente or cliente_obj.email
                        cliente_obj.telefono = telefono_cliente or cliente_obj.telefono
                        cliente_obj.es_habitual = True
                        cliente_obj.save()
                else:
                    # Si no desea ser habitual, verificar si ya estaba registrado previamente
                    cliente_obj = Cliente.objects.filter(rut=rut_cliente).first()

                # Generar número de boleta único
                numero_boleta = f"BOL-{random.randint(100000, 999999)}"

                # Crear el registro de la Venta
                venta = Venta.objects.create(
                    numero_boleta=numero_boleta,
                    rut_cliente=rut_cliente,
                    cliente=cliente_obj,
                    total=total_venta
                )

                # Crear el Detalle de la Venta
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=total_venta
                )

                # Operación de actualización de inventario: Descontar stock
                producto.stock -= cantidad
                producto.save()

            messages.success(
                request, 
                f"¡Venta registrada con éxito! Boleta N° {numero_boleta} por un total de ${total_venta:,}."
            )
            return redirect('venta_detail', pk=venta.pk)
        else:
            messages.error(request, "Por favor revise los errores antes de confirmar la venta.")
    else:
        # Pre-seleccionar producto si viene por GET ?producto_id=
        producto_id = request.GET.get('producto_id')
        initial_data = {}
        if producto_id:
            try:
                prod = Producto.objects.get(pk=producto_id)
                initial_data['producto'] = prod
            except Producto.DoesNotExist:
                pass
        form = VentaForm(initial=initial_data)

    return render(request, 'inventario/venta_form.html', {'form': form})


def venta_list(request):
    """
    Listado del historial de ventas y boletas emitidas.
    Permite filtrar por RUT de cliente o número de boleta.
    """
    query = request.GET.get('q', '').strip()
    ventas = Venta.objects.select_related('cliente').prefetch_related('detalles__producto').all()

    if query:
        ventas = ventas.filter(
            Q(rut_cliente__icontains=query) | Q(numero_boleta__icontains=query)
        )

    total_recaudado = ventas.aggregate(Sum('total'))['total__sum'] or 0
    cantidad_ventas = ventas.count()

    contexto = {
        'ventas': ventas,
        'query': query,
        'total_recaudado': total_recaudado,
        'cantidad_ventas': cantidad_ventas,
    }
    return render(request, 'inventario/venta_list.html', contexto)


def venta_detail(request, pk):
    """
    Vista de detalle de boleta comercial generada para impresión o visualización.
    """
    venta = get_object_or_404(
        Venta.objects.select_related('cliente').prefetch_related('detalles__producto'), 
        pk=pk
    )
    return render(request, 'inventario/venta_detail.html', {'venta': venta})


def cliente_list(request):
    """
    Directorio de clientes registrados con opción de filtrado.
    """
    query = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()

    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) | Q(rut__icontains=query) | Q(email__icontains=query)
        )

    total_clientes = clientes.count()
    habituales = clientes.filter(es_habitual=True).count()

    contexto = {
        'clientes': clientes,
        'query': query,
        'total_clientes': total_clientes,
        'habituales': habituales,
    }
    return render(request, 'inventario/cliente_list.html', contexto)