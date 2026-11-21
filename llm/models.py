from django.db import models
from django.contrib.auth.models import User


class ConversacionIA(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversaciones_llm')
    pregunta = models.TextField()
    respuesta = models.TextField()
    snapshot = models.JSONField(default=dict)
    modelo = models.CharField(max_length=100)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_en']
