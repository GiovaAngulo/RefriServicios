import requests
import urllib.parse
import logging
import config

logger = logging.getLogger(__name__)

ADMIN_PHONE   = config.CALLMEBOT_PHONE
CALLMEBOT_KEY = config.CALLMEBOT_KEY


def enviar_whatsapp(mensaje: str) -> bool:
    """
    Envía un mensaje de WhatsApp al administrador usando la API de CallMeBot.
    Retorna True si el envío fue exitoso, False en caso contrario.
    """
    if CALLMEBOT_KEY == 'TU_API_KEY_AQUI':
        logger.warning('[WhatsApp] API key no configurada. Mensaje no enviado.')
        logger.info('[WhatsApp] Mensaje (simulado): %s', mensaje)
        return False

    try:
        texto_codificado = urllib.parse.quote(mensaje)
        url = (
            f'https://api.callmebot.com/whatsapp.php'
            f'?phone={ADMIN_PHONE}&text={texto_codificado}&apikey={CALLMEBOT_KEY}'
        )
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            logger.info('[WhatsApp] Mensaje enviado correctamente.')
            return True
        else:
            logger.error('[WhatsApp] Error %s: %s', response.status_code, response.text)
            return False
    except requests.exceptions.RequestException as e:
        logger.error('[WhatsApp] Excepción al enviar mensaje: %s', e)
        return False


def notificar_nueva_cita(empresa: str, fecha: str, hora: str, servicio: str) -> bool:
    """
    Construye y envía la notificación de nueva cita al administrador.
    """
    mensaje = (
        f'🧊 *Nueva cita - Refrigeraciones Wilber*\n'
        f'━━━━━━━━━━━━━━━━━\n'
        f'🏢 Empresa: {empresa}\n'
        f'📅 Fecha: {fecha}\n'
        f'⏰ Hora: {hora}\n'
        f'🔧 Servicio: {servicio}\n'
        f'━━━━━━━━━━━━━━━━━\n'
        f'Por favor revisa el panel de administración.'
    )
    return enviar_whatsapp(mensaje)
