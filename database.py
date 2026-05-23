import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash
import config


def get_connection():
    conn = psycopg2.connect(config.DATABASE_URL, sslmode='require')
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            contacto TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'usuario',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id SERIAL PRIMARY KEY,
            empresa_id INTEGER NOT NULL REFERENCES empresas(id),
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    cur.execute("SELECT id FROM empresas WHERE email = %s", (config.ADMIN_EMAIL,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO empresas (nombre,contacto,email,contrasena,rol) VALUES (%s,%s,%s,%s,'admin')",
            (config.ADMIN_NOMBRE, config.ADMIN_CONTACTO, config.ADMIN_EMAIL,
             generate_password_hash(config.ADMIN_PASSWORD))
        )
    conn.commit()
    cur.close()
    conn.close()


def _row(cur):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def _one(cur):
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    return dict(zip(cols, row)) if row else None


# ── Empresas ──────────────────────────────────────────────────────────────────

def crear_empresa(nombre, contacto, email, contrasena):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO empresas (nombre,contacto,email,contrasena,rol) VALUES (%s,%s,%s,%s,'usuario')",
            (nombre, contacto, email, generate_password_hash(contrasena))
        )
        conn.commit()
        cur.close(); conn.close()
        return True, 'Empresa registrada exitosamente.'
    except psycopg2.errors.UniqueViolation:
        return False, 'El correo electrónico ya está registrado.'


def obtener_empresa_por_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM empresas WHERE email = %s", (email,))
    row = _one(cur)
    cur.close(); conn.close()
    return row


def obtener_empresa_por_id(eid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM empresas WHERE id = %s", (eid,))
    row = _one(cur)
    cur.close(); conn.close()
    return row


def listar_empresas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM empresas WHERE rol='usuario' ORDER BY nombre")
    rows = _row(cur)
    cur.close(); conn.close()
    return rows


# ── Citas ─────────────────────────────────────────────────────────────────────

def crear_cita(empresa_id, fecha, hora, descripcion):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO citas (empresa_id,fecha,hora,descripcion,estado) VALUES (%s,%s,%s,%s,'pendiente') RETURNING id",
        (empresa_id, fecha, hora, descripcion)
    )
    cita_id = cur.fetchone()[0]
    conn.commit()
    cur.close(); conn.close()
    return cita_id


def obtener_citas_empresa(empresa_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM citas WHERE empresa_id=%s ORDER BY fecha DESC, hora DESC", (empresa_id,))
    rows = _row(cur)
    cur.close(); conn.close()
    return rows


def obtener_todas_las_citas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT c.*, e.nombre AS empresa_nombre, e.contacto, e.email
        FROM citas c JOIN empresas e ON c.empresa_id = e.id
        ORDER BY c.fecha DESC, c.hora DESC
    ''')
    rows = _row(cur)
    cur.close(); conn.close()
    return rows


def actualizar_estado_cita(cita_id, nuevo_estado):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE citas SET estado=%s WHERE id=%s", (nuevo_estado, cita_id))
    conn.commit()
    cur.close(); conn.close()


def obtener_cita_por_id(cita_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM citas WHERE id=%s", (cita_id,))
    row = _one(cur)
    cur.close(); conn.close()
    return row


def estadisticas_admin():
    conn = get_connection()
    cur = conn.cursor()
    def q(sql): cur.execute(sql); return cur.fetchone()[0]
    stats = {
        'total_citas':    q("SELECT COUNT(*) FROM citas"),
        'pendientes':     q("SELECT COUNT(*) FROM citas WHERE estado='pendiente'"),
        'aceptadas':      q("SELECT COUNT(*) FROM citas WHERE estado='aceptada'"),
        'canceladas':     q("SELECT COUNT(*) FROM citas WHERE estado='cancelada'"),
        'total_empresas': q("SELECT COUNT(*) FROM empresas WHERE rol='usuario'"),
    }
    cur.close(); conn.close()
    return stats
