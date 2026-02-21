# Task Management API - Backend

Sistema de gestión de tareas con autenticación JWT desarrollado con Django REST Framework.

## Stack Técnico

- Python 3.11
- Django 5.0.1
- Django REST Framework 3.14.0
- PostgreSQL (Neon)
- JWT Authentication
- Gunicorn

## Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/juanescode/Backend-Python-Django-Crud-auth.git
cd Backend-Python-Django-Crud-auth

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env

# Ejecutar migraciones
python manage.py migrate


# Correr servidor
python manage.py runserver
```

La API estará disponible en `http://127.0.0.1:8000/api/`

## Variables de Entorno

```env
DB_NAME=nombre_base_datos
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=tu-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Endpoints

### Autenticación

**POST** `/api/auth/register/`
```json
{
  "username": "usuario",
  "email": "email@example.com",
  "password": "contraseña"
}
```

**POST** `/api/auth/login/`
```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

### Tareas (requieren autenticación)

**GET** `/api/tasks/` - Listar todas las tareas del usuario

**POST** `/api/tasks/` - Crear nueva tarea
```json
{
  "title": "Título de la tarea",
  "description": "Descripción",
  "completed": false
}
```

**PUT** `/api/tasks/{id}/` - Actualizar tarea completa

**PATCH** `/api/tasks/{id}/` - Actualizar campos específicos

**DELETE** `/api/tasks/{id}/` - Eliminar tarea

## Estructura del Proyecto

```
backend/
├── apps/
│   ├── tasks/          # App de tareas
│   └── users/          # App de usuarios
├── config/             # Configuración Django
│   ├── settings.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

## Deployment

Desplegado en Koyeb: https://equal-amalia-entrevista-8a244fe1.koyeb.app

Variables de entorno en producción:
- `DEBUG=False`
- `ALLOWED_HOSTS=equal-amalia-entrevista-8a244fe1.koyeb.app`
- `CORS_ALLOWED_ORIGINS=https://entrevista-tecnica.netlify.app`

## Credenciales de Prueba

Usuario: `testuser`  
Contraseña: `test12345`

