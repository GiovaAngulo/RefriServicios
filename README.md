# ❄️ Refrigeraciones Wilber – Sistema de Gestión de Citas

Sistema web para gestión de servicios de refrigeración técnica.  
Permite a empresas clientes registrarse, iniciar sesión y agendar citas,
mientras el administrador gestiona todo desde un panel centralizado.

---

## 🚀 Instalación y puesta en marcha

### 1. Requisitos previos
- Python 3.9 o superior
- pip

### 2. Clonar/descomprimir el proyecto

```bash
# Si descargaste el ZIP:
unzip refrigeraciones_wilber.zip
cd refrigeraciones_wilber
```

### 3. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar la aplicación

```bash
python app.py
```

La app estará disponible en: **http://localhost:5000**

---

## 🔑 Acceso inicial

| Rol           | Email                | Contraseña |
|---------------|----------------------|------------|
| Administrador | admin@wilber.com     | admin123   |
| Usuario       | (registro desde web) | (la tuya)  |

> ⚠️ **Importante:** Cambia la contraseña del admin y la `secret_key` de Flask antes de desplegar en producción.

---

## 📲 Configurar notificaciones de WhatsApp (CallMeBot)

1. Desde el teléfono del administrador, envía el mensaje:
   ```
   I allow callmebot to send me messages
   ```
   al número de WhatsApp: **+34 644 32 10 99**

2. Recibirás una respuesta con tu **API Key**.

3. Abre el archivo `notificaciones.py` y actualiza:
   ```python
   ADMIN_PHONE   = '+57XXXXXXXXXX'   # Tu número con código de país
   CALLMEBOT_KEY = 'TU_API_KEY'      # La clave recibida
   ```

4. ¡Listo! Cada vez que un cliente agende una cita, recibirás un WhatsApp automático.

---

## 📁 Estructura del proyecto

```
refrigeraciones_wilber/
│
├── app.py              # Aplicación principal Flask + rutas
├── database.py         # Inicialización de BD y todas las consultas SQL
├── notificaciones.py   # Módulo de notificaciones WhatsApp (CallMeBot)
├── requirements.txt    # Dependencias Python
├── refrigeraciones.db  # Base de datos SQLite (se crea automáticamente)
│
└── templates/
    ├── base.html       # Plantilla base (navbar, footer, estilos globales)
    ├── index.html      # Página de inicio / landing
    ├── login.html      # Inicio de sesión
    ├── registro.html   # Registro de empresa
    ├── dashboard.html  # Panel del usuario (ver sus citas)
    ├── agendar.html    # Formulario para agendar cita
    └── admin.html      # Panel del administrador (todas las citas)
```

---

## 🛡️ Seguridad implementada

- Contraseñas con hash **bcrypt** (Werkzeug)
- Validación de correos únicos en la base de datos
- Decoradores `@login_requerido` y `@admin_requerido` en rutas sensibles
- Separación estricta de roles (usuario / admin)
- Sesiones de Flask con `secret_key`

---

## 🗄️ Base de datos (SQLite)

### Tabla `empresas`
| Campo          | Tipo    | Descripción                  |
|----------------|---------|------------------------------|
| id             | INTEGER | PK, autoincrement            |
| nombre         | TEXT    | Nombre de la empresa         |
| contacto       | TEXT    | Nombre del contacto          |
| email          | TEXT    | UNIQUE, login                |
| contrasena     | TEXT    | Hash bcrypt                  |
| rol            | TEXT    | 'admin' o 'usuario'          |
| fecha_registro | DATETIME| Automático                   |

### Tabla `citas`
| Campo         | Tipo    | Descripción                       |
|---------------|---------|-----------------------------------|
| id            | INTEGER | PK, autoincrement                 |
| empresa_id    | INTEGER | FK → empresas.id                  |
| fecha         | TEXT    | Fecha de la cita (YYYY-MM-DD)     |
| hora          | TEXT    | Hora de la cita (HH:MM)           |
| descripcion   | TEXT    | Tipo de servicio                  |
| estado        | TEXT    | 'pendiente' / 'aceptada' / 'cancelada' |
| fecha_creacion| DATETIME| Automático                        |

---

## 🚀 Mejoras futuras sugeridas

- [ ] Calendario visual con FullCalendar.js
- [ ] Notificación por email al cliente (Flask-Mail)
- [ ] Bloqueo de horarios ya ocupados
- [ ] Exportar citas a Excel/PDF
- [ ] Migración a PostgreSQL o MySQL
- [ ] Despliegue en Railway, Render o VPS propio
- [ ] Panel de métricas con gráficos (Chart.js)
- [ ] Autenticación con tokens JWT para API REST

---

## 📞 Soporte

Sistema desarrollado para **Refrigeraciones Wilber**.  
Para modificaciones o mejoras, contacta al desarrollador.
