"""
Módulo de Validaciones y Operaciones de Lógica de Negocio
Evaluación Sumativa 1 - Programación Backend
"""
import re
from django.core.exceptions import ValidationError


def validar_rut_chileno(rut_str):
    """
    Valida el formato y el dígito verificador de un RUT chileno usando el algoritmo Módulo 11.
    Aplica estructuras de decisión y operadores lógicos/aritméticos.
    """
    if not rut_str:
        raise ValidationError("El RUT es obligatorio.")

    # Limpieza del RUT (eliminar espacios, puntos y guiones)
    rut_limpio = rut_str.strip().replace(".", "").replace("-", "").upper()

    # Estructura de decisión: Validar longitud mínima y máxima (ej: 7 a 9 caracteres)
    if len(rut_limpio) < 8 or len(rut_limpio) > 9:
        raise ValidationError("El RUT debe tener entre 7 y 9 caracteres numéricos más el dígito verificador.")

    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]

    # Estructura de decisión: Validar que el cuerpo sean solo números
    if not cuerpo.isdigit():
        raise ValidationError("El cuerpo del RUT debe contener únicamente dígitos numéricos.")

    # Algoritmo Módulo 11 para cálculo del Dígito Verificador
    suma = 0
    multiplicador = 2

    # Recorrido inverso del cuerpo numérico
    for caracter in reversed(cuerpo):
        suma += int(caracter) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    resto = suma % 11
    resultado = 11 - resto

    # Estructura de decisión para determinar el dígito esperado
    if resultado == 11:
        dv_esperado = "0"
    elif resultado == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(resultado)

    # Estructura de decisión: Comparación final
    if dv != dv_esperado:
        raise ValidationError(f"El RUT ingresado no es válido. El dígito verificador esperado es '{dv_esperado}'.")

    return rut_limpio


def formatear_rut(rut_str):
    """
    Formatea un RUT a su representación estándar (ej: 12.345.678-K).
    """
    if not rut_str:
        return ""
    rut_limpio = rut_str.strip().replace(".", "").replace("-", "").upper()
    if len(rut_limpio) < 2:
        return rut_limpio
    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]
    # Formateo con puntos de miles
    cuerpo_formateado = f"{int(cuerpo):,}".replace(",", ".")
    return f"{cuerpo_formateado}-{dv}"
