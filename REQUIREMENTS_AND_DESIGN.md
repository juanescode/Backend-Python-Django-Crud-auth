# Documento de Diseño - Task Management API

## 1. Requerimientos Funcionales

### Autenticación
- RF-01: Sistema de registro de usuarios con validación de email único
- RF-02: Login con generación de tokens JWT 
- RF-03: Protección de endpoints mediante Bearer token
- RF-04: Logout (limpieza de tokens en cliente)

### Gestión de Tareas
- RF-05: Crear tareas con título, descripción y estado
- RF-06: Listar tareas del usuario autenticado
- RF-07: Actualizar información de tareas existentes
- RF-08: Marcar tareas como completadas/pendientes
- RF-09: Eliminar tareas
- RF-10: Filtrado automático por usuario (cada usuario ve solo sus tareas)

## 2. Requerimientos No Funcionales

- RNF-01: **Seguridad**: Autenticación JWT con tokens de 1 hora de vida
- RNF-02: **Performance**: Respuestas API < 200ms en promedio
- RNF-03: **Escalabilidad**: Base de datos cloud (Neon.tech PostgreSQL)
- RNF-04: **Disponibilidad**: Deployment en Render con auto-deploy
- RNF-05: **CORS**: Configurado para múltiples orígenes (dev + prod)
- RNF-06: **Validación**: Validación de datos en serializers de DRF

## 3. Supuestos y Decisiones

### Tecnológicos
- Django 5.0 por su estabilidad y madurez
- DRF para API RESTful con serializers automáticos
- PostgreSQL sobre SQLite para ambiente productivo desde el inicio
- JWT simple (sin refresh token rotation) para simplificar MVP
- Neon.tech como provider de DB por su tier gratuito y pooling

### Funcionales
- Una tarea pertenece a un solo usuario (no hay colaboración)
- No hay roles (todos los usuarios tienen los mismos permisos)
- Las tareas eliminadas no se guardan (no hay soft delete)
- Email se requiere en registro pero no se valida vía correo
- Timestamps (created_at, updated_at) se manejan automáticamente

### Arquitectura
- Separación total frontend/backend (SPA + API)
- Stateless authentication (solo JWT, sin sesiones)
- CORS explícito (no `CORS_ORIGIN_ALLOW_ALL`)

## 4. Modelo de Datos (ERD)

### User (Django default con extensión)
```
User
├── id (PK)
├── username (unique)
├── email (unique)
├── password (hashed)
├── date_joined
└── last_login
```

### Task
```
Task
├── id (PK)
├── user_id (FK → User) [CASCADE]
├── title (CharField, max 200)
├── description (TextField, nullable)
├── completed (Boolean, default=False)
├── created_at (auto_now_add)
└── updated_at (auto_now)
```

**Relación**: `User 1:N Task`  
**Restricción**: Al eliminar usuario se eliminan sus tareas (CASCADE)

## 5. Endpoints Implementados

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/api/auth/register/` | Registro de nuevo usuario | No |
| POST | `/api/auth/login/` | Login y obtención de tokens | No |
| GET | `/api/tasks/` | Listar tareas del usuario | Sí |
| POST | `/api/tasks/` | Crear nueva tarea | Sí |
| GET | `/api/tasks/{id}/` | Detalle de una tarea | Sí |
| PUT | `/api/tasks/{id}/` | Actualización completa | Sí |
| PATCH | `/api/tasks/{id}/` | Actualización parcial | Sí |
| DELETE | `/api/tasks/{id}/` | Eliminar tarea | Sí |

**Base URL Producción**: `https://backend-python-django-crud-auth.onrender.com/api/`

## 6. Autenticación y Seguridad

### Flow JWT
1. Usuario hace login → recibe `access_token` y `refresh_token`
2. Frontend almacena tokens en localStorage
3. Cada request incluye header: `Authorization: Bearer {access_token}`
4. Token expira en 1 hora → frontend maneja 401 y redirige a login

### Configuración CORS
- Permite orígenes específicos (no wildcard)
- Acepta credenciales (`CORS_ALLOW_CREDENTIALS = True`)
- Headers permitidos: Authorization, Content-Type, etc.
- Métodos: GET, POST, PUT, PATCH, DELETE, OPTIONS

## 7. Validaciones

### Registro
- Username: requerido, único, 3-150 caracteres
- Email: requerido, único, formato válido
- Password: mínimo 8 caracteres (Django validators)

### Tareas
- Title: requerido, max 200 caracteres
- Description: opcional
- Completed: boolean, default false
- User: asignado automáticamente desde token

## 8. Estructura de Respuestas

### Éxito - Login (200)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJ...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJ...",
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "email@example.com"
  }
}
```

### Éxito - Lista Tareas (200)
```json
[
  {
    "id": 1,
    "title": "Tarea ejemplo",
    "description": "Descripción",
    "completed": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### Error - Validación (400)
```json
{
  "email": ["Este campo es obligatorio."],
  "password": ["Este campo es obligatorio."]
}
```

### Error - No Autorizado (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## 9. Consideraciones de Deployment

### Render
- Build command: `./build.sh`
- Start command: `gunicorn config.wsgi:application`
- Auto-deploy habilitado en branch `fix`
- Health check endpoint: `/api/tasks/` (requiere auth)

### Base de Datos
- Neon PostgreSQL pooling (serverless)
- SSL requerido (`sslmode=require`)
- Conexiones manejadas por pool (max 10 en tier gratuito)

### Variables Críticas
- `DEBUG=False` en producción
- `SECRET_KEY` única por ambiente
- `ALLOWED_HOSTS` específico por dominio
- `CORS_ALLOWED_ORIGINS` separado por comas

