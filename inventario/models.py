from django.db import models
from django.core.validators import MinValueValidator
import uuid

# ==============================================================================
# MODELO 1: PRODUCTO
# Cumple requerimiento: Registrar con nombre, código, cantidad/stock y precio.
# Permite actualizar stock y eliminar.
# ==============================================================================
class Producto(models.Model):
    """
    Representa un producto dentro del catálogo del negocio.
    """
    codigo = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Código de Producto",
        help_text="Identificador único del producto (ej: PROD-001)"
    )
    nombre = models.CharField(
        max_length=100, 
        verbose_name="Nombre del Producto"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Descripción",
        help_text="Detalles o especificaciones del producto"
    )
    precio = models.IntegerField(
        validators=[MinValueValidator(1, message="El precio debe ser mayor a 0.")],
        verbose_name="Precio Unitario ($ CLP)"
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, message="El stock no puede ser negativo.")],
        verbose_name="Cantidad en Stock"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Registro"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre} (${self.precio:,} | Stock: {self.stock})"

    def estado_stock(self):
        """
        Estructura de decisión para evaluar la disponibilidad del producto.
        Retorna una etiqueta según el nivel de inventario disponible.
        """
        if self.stock <= 0:
            return "Agotado"
        elif self.stock <= 5:
            return "Stock Crítico"
        else:
            return "Disponible"

    def esta_disponible(self):
        """
        Determina si el producto tiene unidades disponibles para venta inmediata.
        """
        return self.stock > 0


# ==============================================================================
# MODELO 2: CLIENTE
# Cumple requerimiento: Guardar datos de cliente si quiere ser cliente habitual.
# ==============================================================================
class Cliente(models.Model):
    """
    Representa a los clientes registrados en el sistema (habituales u ocasionales).
    """
    rut = models.CharField(
        max_length=15, 
        unique=True, 
        verbose_name="RUT del Cliente"
    )
    nombre = models.CharField(
        max_length=120, 
        verbose_name="Nombre Completo"
    )
    email = models.EmailField(
        blank=True, 
        null=True, 
        verbose_name="Correo Electrónico"
    )
    telefono = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Teléfono de Contacto"
    )
    es_habitual = models.BooleanField(
        default=True, 
        verbose_name="¿Es Cliente Habitual?",
        help_text="Marcar si el cliente consiente guardar sus datos para futuras compras."
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Registro"
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

    def __str__(self):
        tipo = "Habitual" if self.es_habitual else "Ocasional"
        return f"{self.nombre} ({self.rut}) - {tipo}"


# ==============================================================================
# MODELO 3: VENTA (BOLETA)
# Cumple requerimiento: Registrar ventas designadas a un RUT de cliente.
# ==============================================================================
class Venta(models.Model):
    """
    Representa la transacción comercial (boleta de venta).
    """
    numero_boleta = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="N° de Boleta"
    )
    rut_cliente = models.CharField(
        max_length=15, 
        verbose_name="RUT del Comprador"
    )
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="ventas",
        verbose_name="Cliente Asociado"
    )
    fecha_venta = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha y Hora"
    )
    total = models.IntegerField(
        default=0, 
        verbose_name="Total Pagado ($ CLP)"
    )

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']

    def __str__(self):
        return f"Boleta #{self.numero_boleta} - RUT: {self.rut_cliente} - Total: ${self.total:,}"


# ==============================================================================
# MODELO 4: DETALLE DE VENTA
# ==============================================================================
class DetalleVenta(models.Model):
    """
    Detalle de ítems correspondientes a una venta registrada.
    """
    venta = models.ForeignKey(
        Venta, 
        on_delete=models.CASCADE, 
        related_name="detalles",
        verbose_name="Venta"
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.PROTECT, 
        related_name="detalles",
        verbose_name="Producto"
    )
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1, message="La cantidad mínima a vender es 1.")],
        verbose_name="Cantidad"
    )
    precio_unitario = models.IntegerField(
        verbose_name="Precio Unitario"
    )
    subtotal = models.IntegerField(
        verbose_name="Subtotal"
    )

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Ventas"

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} (${self.subtotal:,})"