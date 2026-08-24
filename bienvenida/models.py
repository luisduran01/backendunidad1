from django.db import models

# Create your models here.
class Producto(models.Model):
 nombre = models.CharField(max_length=64)
 precio = models.DecimalField(default=0)
 stock = models.IntegerField(default=0)
 descripcion = models.CharField(max_length=128, null=True, blank=True)
 def __str__(self): 
  return self.nombre 