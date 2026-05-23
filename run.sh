#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run.sh – Script de inicio rápido para Refrigeraciones Wilber
# Uso:
#   chmod +x run.sh
#   ./run.sh             (modo desarrollo)
#   ./run.sh prod        (modo producción con Gunicorn)
# ─────────────────────────────────────────────────────────────────────────────

set -e

VENV_DIR="venv"
MODE="${1:-dev}"

# ── 1. Crear entorno virtual si no existe ─────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
fi

# ── 2. Activar entorno ────────────────────────────────────────────────────────
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# ── 3. Instalar dependencias ──────────────────────────────────────────────────
echo "🔧 Verificando dependencias..."
pip install -q -r requirements.txt

# ── 4. Cargar variables de entorno si existe .env ─────────────────────────────
if [ -f ".env" ]; then
    echo "⚙️  Cargando variables de entorno desde .env..."
    # shellcheck disable=SC2046
    export $(grep -v '^#' .env | xargs)
fi

# ── 5. Ejecutar ───────────────────────────────────────────────────────────────
if [ "$MODE" = "prod" ]; then
    echo "🚀 Iniciando en modo PRODUCCIÓN con Gunicorn..."
    pip install -q gunicorn
    gunicorn "app:app" --bind 0.0.0.0:5000 --workers 2 --timeout 60 --access-logfile -
else
    echo "🧊 Iniciando Refrigeraciones Wilber en modo DESARROLLO..."
    echo "   → http://localhost:5000"
    echo "   → Admin: admin@wilber.com / admin123"
    echo ""
    FLASK_ENV=development python3 app.py
fi
