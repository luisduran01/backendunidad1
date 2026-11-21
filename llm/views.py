import os
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
from dotenv import load_dotenv
from groq import Groq
from inventario.models import Producto, Venta
from .models import ConversacionIA

load_dotenv()

# Create your views here.

@login_required
def chatbot_view(request):
    """Vista principal del chatbot"""
    return render(request, 'llm/chatbot.html')

@csrf_protect
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint para procesar mensajes del chatbot"""
    try:
        user = request.user if request.user.is_authenticated else None
        if user is None:
            auth = JWTAuthentication()
            result = auth.authenticate(request)
            if result is None:
                return JsonResponse({'error': 'Autenticacion JWT requerida.', 'status': 'error'}, status=401)
            user, _ = result

        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'No se proporcionó ningún mensaje'}, status=400)
        
        if len(user_message) > 2000:
            return JsonResponse({'error': 'El mensaje supera el limite de 2000 caracteres.'}, status=400)

        cache_key = f'groq-chat:{user.pk}'
        count = cache.get(cache_key, 0)
        if count >= 10:
            return JsonResponse({'error': 'Limite de uso alcanzado. Intenta nuevamente en una hora.', 'status': 'error'}, status=429)
        cache.set(cache_key, count + 1, timeout=3600)

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return JsonResponse({'error': 'GROQ_API_KEY no configurada en el servidor.', 'status': 'error'}, status=503)

        productos = list(Producto.objects.all().values(
            'codigo', 'nombre', 'descripcion', 'precio', 'stock'
        ))
        ventas = list(Venta.objects.order_by('-fecha_venta').values(
            'numero_boleta', 'rut_cliente', 'total', 'fecha_venta'
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

        system_prompt = (
            "Eres el asistente operativo del sistema real de inventario y ventas. "
            "Responde usando exclusivamente el contexto JSON real entregado. "
            "Si la informacion no aparece, indicalo claramente. No inventes datos. "
            "Responde en espanol, de forma breve y accionable."
        )

        client = Groq(api_key=api_key)
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": json.dumps(snapshot, ensure_ascii=False)},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_completion_tokens=1024,
            top_p=0.9,
            stream=False,
            stop=None
        )
        
        response_message = completion.choices[0].message.content
        if not response_message or not response_message.strip():
            return JsonResponse({'error': 'La IA devolvio una respuesta vacia.', 'status': 'error'}, status=502)

        ConversacionIA.objects.create(
            usuario=user,
            pregunta=user_message,
            respuesta=response_message,
            snapshot=snapshot,
            modelo=model,
        )
        
        return JsonResponse({
            'response': response_message,
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'La solicitud debe contener JSON valido.', 'status': 'error'}, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'No fue posible consultar GroqCloud: {str(e)}',
            'status': 'error'
        }, status=502)