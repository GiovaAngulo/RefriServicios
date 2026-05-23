import csv
import io
import logging
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, Response
)
from werkzeug.security import check_password_hash

import config
import database as db
from notificaciones import notificar_nueva_cita

# ─── Configuración ───────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

SERVICIOS = config.SERVICIOS

# ─── Decoradores de seguridad ─────────────────────────────────────────────────

def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'empresa_id' not in session:
            flash('Debes iniciar sesión para acceder.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorada


def admin_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'empresa_id' not in session:
            flash('Debes iniciar sesión.', 'warning')
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            flash('Acceso denegado. Solo administradores.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorada


# ─── Inicialización ──────────────────────────────────────────────────────────

with app.app_context():
    db.init_db()

# ─── Manejadores de error ─────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404,
                           titulo='Página no encontrada',
                           mensaje='La página que buscas no existe o fue movida.'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403,
                           titulo='Acceso denegado',
                           mensaje='No tienes permisos para acceder a esta sección.'), 403


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500,
                           titulo='Error interno',
                           mensaje='Algo salió mal. Por favor intenta de nuevo más tarde.'), 500

# ─── Rutas públicas ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'empresa_id' in session:
        if session.get('rol') == 'admin':
            return redirect(url_for('admin_panel'))
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'empresa_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre    = request.form.get('nombre', '').strip()
        contacto  = request.form.get('contacto', '').strip()
        email     = request.form.get('email', '').strip().lower()
        contrasena = request.form.get('contrasena', '')
        confirmar = request.form.get('confirmar', '')

        errores = []
        if not nombre:
            errores.append('El nombre de la empresa es obligatorio.')
        if not contacto:
            errores.append('El nombre del contacto es obligatorio.')
        if not email or '@' not in email:
            errores.append('Ingresa un correo válido.')
        if len(contrasena) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres.')
        if contrasena != confirmar:
            errores.append('Las contraseñas no coinciden.')

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('registro.html',
                                   nombre=nombre, contacto=contacto, email=email)

        ok, mensaje = db.crear_empresa(nombre, contacto, email, contrasena)
        if ok:
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash(mensaje, 'danger')
            return render_template('registro.html',
                                   nombre=nombre, contacto=contacto, email=email)

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'empresa_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email     = request.form.get('email', '').strip().lower()
        contrasena = request.form.get('contrasena', '')

        empresa = db.obtener_empresa_por_email(email)
        if empresa and check_password_hash(empresa['contrasena'], contrasena):
            session['empresa_id']     = empresa['id']
            session['empresa_nombre'] = empresa['nombre']
            session['rol']            = empresa['rol']

            flash(f'¡Bienvenido, {empresa["nombre"]}!', 'success')
            if empresa['rol'] == 'admin':
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        else:
            flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('index'))

# ─── Rutas de usuario ─────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_requerido
def dashboard():
    citas = db.obtener_citas_empresa(session['empresa_id'])
    empresa = db.obtener_empresa_por_id(session['empresa_id'])
    return render_template('dashboard.html', citas=citas, empresa=empresa)


@app.route('/agendar', methods=['GET', 'POST'])
@login_requerido
def agendar():
    if request.method == 'POST':
        fecha       = request.form.get('fecha', '').strip()
        hora        = request.form.get('hora', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        errores = []
        if not fecha:
            errores.append('La fecha es obligatoria.')
        if not hora:
            errores.append('La hora es obligatoria.')
        if not descripcion:
            errores.append('Debes seleccionar un tipo de servicio.')

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('agendar.html', servicios=SERVICIOS,
                                   fecha=fecha, hora=hora)

        db.crear_cita(session['empresa_id'], fecha, hora, descripcion)

        # Notificar al administrador por WhatsApp
        notificar_nueva_cita(
            empresa=session['empresa_nombre'],
            fecha=fecha,
            hora=hora,
            servicio=descripcion
        )

        flash('✅ Cita agendada exitosamente. Pronto recibirás confirmación.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('agendar.html', servicios=SERVICIOS)

# ─── Rutas de administrador ───────────────────────────────────────────────────

@app.route('/admin')
@admin_requerido
def admin_panel():
    citas    = db.obtener_todas_las_citas()
    empresas = db.listar_empresas()
    stats    = db.estadisticas_admin()
    return render_template('admin.html', citas=citas, empresas=empresas, stats=stats)


@app.route('/admin/cita/<int:cita_id>/estado', methods=['POST'])
@admin_requerido
def cambiar_estado(cita_id):
    nuevo_estado = request.form.get('estado')
    estados_validos = ('pendiente', 'aceptada', 'cancelada')

    if nuevo_estado not in estados_validos:
        flash('Estado no válido.', 'danger')
        return redirect(url_for('admin_panel'))

    cita = db.obtener_cita_por_id(cita_id)
    if not cita:
        flash('Cita no encontrada.', 'danger')
        return redirect(url_for('admin_panel'))

    db.actualizar_estado_cita(cita_id, nuevo_estado)
    flash(f'Estado de la cita #{cita_id} actualizado a "{nuevo_estado}".', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/api/stats')
@admin_requerido
def api_stats():
    return jsonify(db.estadisticas_admin())

@app.route('/admin/exportar/citas')
@admin_requerido
def exportar_citas():
    """Descarga todas las citas en formato CSV."""
    citas = db.obtener_todas_las_citas()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Empresa', 'Contacto', 'Email', 'Fecha', 'Hora', 'Servicio', 'Estado', 'Creada el'])
    for c in citas:
        writer.writerow([
            c['id'], c['empresa_nombre'], c['contacto'], c['email'],
            c['fecha'], c['hora'], c['descripcion'], c['estado'],
            c['fecha_creacion'][:16]
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=citas_wilber.csv'}
    )


@app.route('/perfil')
@login_requerido
def perfil():
    empresa = db.obtener_empresa_por_id(session['empresa_id'])
    citas   = db.obtener_citas_empresa(session['empresa_id'])
    return render_template('perfil.html', empresa=empresa, citas=citas)


# ─── Arranque ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
