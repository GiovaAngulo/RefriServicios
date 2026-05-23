"""
config.py – Configuración centralizada de Refrigeraciones Wilber
Modifica este archivo según el entorno (desarrollo / producción).
"""

import os

# ─── Entorno ──────────────────────────────────────────────────────────────────
ENV = os.environ.get('FLASK_ENV', 'development')

# ─── Seguridad ────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'refrigeraciones-wilber-dev-key-2024')

# ─── Base de datos (Supabase / PostgreSQL) ────────────────────────────────────
# Formato: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:PASSWORD@db.PROYECTO.supabase.co:5432/postgres')

# ─── Administrador por defecto ────────────────────────────────────────────────
ADMIN_EMAIL    = os.environ.get('ADMIN_EMAIL',    'admin@wilber.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
ADMIN_NOMBRE   = 'Refrigeraciones Wilber'
ADMIN_CONTACTO = 'Wilber'

# ─── WhatsApp (CallMeBot) ─────────────────────────────────────────────────────
# Pasos para activar:
# 1. Envía "I allow callmebot to send me messages" al +34 644 32 10 99 por WhatsApp
# 2. Recibirás tu API key por respuesta
# 3. Rellena los valores aquí o defínelos como variables de entorno
CALLMEBOT_PHONE = os.environ.get('CALLMEBOT_PHONE', '+573001234567')
CALLMEBOT_KEY   = os.environ.get('CALLMEBOT_KEY',   'TU_API_KEY_AQUI')

# ─── Servicios disponibles ────────────────────────────────────────────────────
SERVICIOS = [
    'Instalación de equipo nuevo',
    'Mantenimiento preventivo',
    'Reparación de compresor',
    'Reparación de evaporador',
    'Reparación de condensador',
    'Recarga de gas refrigerante',
    'Revisión eléctrica',
    'Diagnóstico general',
    'Otros',
]

# ─── Servidor ─────────────────────────────────────────────────────────────────
HOST  = os.environ.get('HOST', '0.0.0.0')
PORT  = int(os.environ.get('PORT', 5000))
DEBUG = ENV == 'development'
