# Evaluación Sumativa 2: Programación Backend (Django)
**Asignatura:** Programación Back End (TI3041)  
**Institución:** INACAP  
**Caso desarrollado:** **Caso 2 - Aplicación de Control de Venta e Inventario**

---

## 📌 Descripción del Proyecto
Aplicación web desarrollada en el framework **Django (arquitectura Modelo-Vista-Plantilla / MVT)** para la gestión y digitalización de productos, control de existencias (stock), emisión de boletas y administración de clientes (habituales y ocasionales).

---

## 🎯 Cumplimiento de Requerimientos (Caso 2)
- **Gestión de Productos:**
  - Registro de productos con: `nombre`, `código` (único), `precio`, `stock / cantidad` y `descripción`.
  - Actualización directa de stock (sumar existencias o fijar valor) y eliminación de productos con confirmación.
  - Listado de productos disponibles con indicadores visuales de disponibilidad (`Disponible`, `Stock Crítico`, `Agotado`).
- **Control de Ventas y Emisión de Boletas:**
  - Registro de ventas asociadas a un RUT de comprador.
  - Validación del RUT chileno mediante algoritmo de **Módulo 11** y control de formato.
  - Disminución automática del stock al concretar una venta y validación de inventario suficiente mediante estructuras de decisión (`if / elif / else`).
- **Gestión Condicional de Clientes:**
  - **Cliente Habitual:** Si el cliente consiente guardar sus datos, se solicita nombre, correo electrónico y teléfono de contacto.
  - **Cliente Ocasional:** En caso de que no desee registrarse como habitual, solo se solicita el RUT para la emisión de la boleta.
- **Historial, reportes e impresión:**
  - Módulo de historial de boletas emitidas con cálculo de totales y montos recaudados.
  - Filtros por RUT, boleta y rango de fechas, con paginación.
  - Vista e impresión de Boleta Electrónica detallada.

## Administración y producción

El proyecto activo usa `core.settings` y `core.wsgi`. Django Admin incluye búsquedas por producto, cliente, RUT y boleta, filtros de stock y fecha, exportación CSV, acciones e inline de detalles de venta.

En desarrollo se puede usar SQLite. Para producción se configura PostgreSQL (Supabase o un PaaS) con las variables `host`, `port`, `database`, `user` y `password`. `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` también se leen desde el entorno; consulta `.env.example` como plantilla y nunca publiques un `.env` real.

---

## 🛠️ Tecnologías y Paquetes Externos Utilizados
- **Python 3.10+ / 3.13 / 3.14**
- **Django 5.x / 6.x**
- **Paquete externo `django-crispy-forms` y `crispy-bootstrap5`:** Integración para renderizado limpio de formularios.
- **Bootstrap 5 & Bootstrap Icons:** Diseño responsivo y moderno.
- **PostgreSQL:** Base de datos recomendada para producción; SQLite queda solo como fallback local.
- **WhiteNoise:** Servicio de archivos estáticos para producción.

---

## 🚀 Instrucciones de Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd backendunidad1
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Aplicar migraciones a la base de datos
```bash
python manage.py migrate
```

### 4. (Opcional) Cargar datos de prueba iniciales
Se incluye un comando personalizado para cargar productos, clientes y ventas de ejemplo:
```bash
python manage.py poblar_datos
```

### 5. Preparar estáticos y comprobar el proyecto

```bash
python manage.py check --deploy
python manage.py collectstatic --noinput
python manage.py test inventario
```

### 6. Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```
Abra su navegador en: **http://127.0.0.1:8000/**

---

## ☁️ Despliegue en Vercel

1. Conecta el repositorio a Vercel y conserva `vercel.json`, que apunta a `core/wsgi.py`.
2. Configura en Vercel las variables de `.env.example`, incluyendo las credenciales PostgreSQL de Supabase.
3. Ejecuta las migraciones contra la base productiva: `python manage.py migrate`.
4. Revisa los logs de la función Python en Vercel para validar solicitudes y errores.

## 🧪 Ejecución de Pruebas Unitarias
Para verificar el correcto funcionamiento de todas las validaciones de negocio, estructuras de decisión y flujo de ventas:
```bash
python manage.py test inventario
```

---

## 📂 Estructura del Proyecto
```text
backendunidad1/
├── manage.py
├── requirements.txt
├── README.md
├── core/
│   ├── settings.py           # Configuración general, paquetes externos y localización
│   ├── urls.py               # Enrutamiento principal
│   └── wsgi.py
├── inventario/
│   ├── models.py             # Modelos: Producto, Cliente, Venta, DetalleVenta
│   ├── forms.py              # Formularios con crispy-forms y validaciones
│   ├── validators.py         # Validador de RUT chileno (Módulo 11) y utilidades
│   ├── views.py              # Vistas con lógica de negocio y estructuras de decisión
│   ├── urls.py               # Rutas de la app
│   ├── admin.py              # Panel de administración de Django
│   ├── tests.py              # Pruebas unitarias automatizadas
│   ├── management/
│   │   └── commands/
│   │       └── poblar_datos.py # Carga de datos de prueba
│   └── templates/
│       └── inventario/
│           ├── base.html
│           ├── producto_list.html
│           ├── producto_detail.html
│           ├── producto_form.html
│           ├── producto_stock_form.html
│           ├── producto_confirm_delete.html
│           ├── venta_form.html
│           ├── venta_list.html
│           ├── venta_detail.html
│           └── cliente_list.html
```
