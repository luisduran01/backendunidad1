from django.contrib import admin
from django.urls import include, path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from inventario.models import Producto, Venta, AnalisisIA
import json
import os


class AnalisisInventarioThrottle(UserRateThrottle):
    rate = '5/hour'


class AnalisisInventarioView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnalisisInventarioThrottle]

    def post(self, request):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return Response(
                {'detail': 'GROQ_API_KEY no configurada. Configure el secreto en el servidor.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        productos = list(Producto.objects.all().values(
            'id', 'codigo', 'nombre', 'descripcion', 'precio', 'stock',
        ))
        ventas = list(Venta.objects.order_by('-fecha_venta').values(
            'numero_boleta', 'rut_cliente', 'total', 'fecha_venta',
        )[:20])
        snapshot = {
            'productos': productos,
            'ventas_recientes': [
                {**venta, 'fecha_venta': venta['fecha_venta'].isoformat()}
                for venta in ventas
            ],
            'valor_inventario': sum(p['precio'] * p['stock'] for p in productos),
            'total_recaudado': sum(v['total'] for v in ventas),
        }

        prompt = (
            "Eres un analista de operaciones de inventario. Usa exclusivamente los datos "
            "proporcionados en JSON. Devuelve SOLO JSON valido con estas claves: "
            "resumen (texto breve), alertas (lista de strings), recomendaciones "
            "(lista de strings). Identifica agotados, criticos y acciones concretas."
        )

        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                model=os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant'),
                temperature=0.2,
                response_format={'type': 'json_object'},
                messages=[
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': json.dumps(snapshot, ensure_ascii=False)},
                ],
                timeout=30,
            )
            raw = completion.choices[0].message.content
            parsed = json.loads(raw)
            if not isinstance(parsed.get('resumen'), str):
                raise ValueError('El modelo no devolvio un resumen valido.')
            if not isinstance(parsed.get('alertas'), list) or not isinstance(parsed.get('recomendaciones'), list):
                raise ValueError('El modelo no devolvio listas validas.')
        except json.JSONDecodeError:
            return Response(
                {'detail': 'La IA devolvio una respuesta invalida.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as exc:
            return Response(
                {'detail': f'No fue posible consultar GroqCloud: {str(exc)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        analisis = AnalisisIA.objects.create(
            usuario=request.user,
            resumen=parsed['resumen'],
            alertas=parsed['alertas'],
            recomendaciones=parsed['recomendaciones'],
            snapshot=snapshot,
            modelo=os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant'),
        )
        return Response({
            'id': analisis.id,
            'resumen': analisis.resumen,
            'alertas': analisis.alertas,
            'recomendaciones': analisis.recomendaciones,
            'modelo': analisis.modelo,
            'creado_en': analisis.creado_en,
            'snapshot': {
                'productos': len(productos),
                'ventas': len(ventas),
                'valor_inventario': snapshot['valor_inventario'],
            },
        }, status=status.HTTP_201_CREATED)

from inventario.api import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventario.urls')),
    path("api-auth/", include("rest_framework.urls")),
    
    path('api/', include(router.urls)),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/ia/analizar-inventario/', AnalisisInventarioView.as_view(), name='analizar_inventario'),
]