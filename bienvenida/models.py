from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=64)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    stock = models.IntegerField(default=0)
    descripcion = models.CharField(
        max_length=128,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre