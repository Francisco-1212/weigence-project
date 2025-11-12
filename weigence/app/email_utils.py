"""
Utilidades para envío de correos de recuperación de contraseña
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
import hashlib
from api.conexion_supabase import supabase


def generar_token_recuperacion():
    """Genera un token seguro para recuperación de contraseña"""
    return secrets.token_urlsafe(32)


def almacenar_token_recuperacion(email, token):
    """
    Almacena el token de recuperación en Supabase con expiración de 1 hora
    """
    try:
        expiracion = datetime.now() + timedelta(hours=1)
        
        # Verificar si ya existe un token para este email
        tokens_existentes = supabase.table("password_reset_tokens").select("*").eq("email", email).execute().data
        
        if tokens_existentes:
            # Actualizar token existente
            supabase.table("password_reset_tokens").update({
                "token": token,
                "created_at": datetime.now().isoformat(),
                "expires_at": expiracion.isoformat(),
                "usado": False
            }).eq("email", email).execute()
        else:
            # Crear nuevo registro
            supabase.table("password_reset_tokens").insert({
                "email": email,
                "token": token,
                "created_at": datetime.now().isoformat(),
                "expires_at": expiracion.isoformat(),
                "usado": False
            }).execute()
        
        print(f"[EMAIL] Token de recuperación almacenado para: {email}")
        return True
    except Exception as e:
        print(f"[EMAIL] Error almacenando token: {e}")
        return False


def enviar_correo_recuperacion(email_destino, nombre_usuario=None):
    """
    Envía un correo de recuperación de contraseña
    
    Soporta:
    1. Gmail con contraseña de aplicación
    2. Outlook/Office365
    3. SMTP personalizado
    """
    try:
        # Obtener configuración de variables de entorno
        MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
        MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
        MAIL_USERNAME = os.getenv("MAIL_USERNAME")
        MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
        MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)
        BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
        
        # Validar configuración
        if not MAIL_USERNAME or not MAIL_PASSWORD:
            print("[EMAIL] ⚠️ Variables MAIL_USERNAME o MAIL_PASSWORD no configuradas")
            print("[EMAIL] Para habilitar: Configure en .env las credenciales SMTP")
            return False
        
        # Generar token
        token = generar_token_recuperacion()
        
        # Almacenar token
        if not almacenar_token_recuperacion(email_destino, token):
            return False
        
        # Construir URL de recuperación
        reset_url = f"{BASE_URL}/reset-password?token={token}&email={email_destino}"
        
        # Crear mensaje
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = "Recuperación de contraseña - Weigence Inventory"
        mensaje["From"] = MAIL_FROM
        mensaje["To"] = email_destino
        
        # Texto plano
        texto_plano = f"""
Hola {nombre_usuario or 'Usuario'},

Recibimos una solicitud para restablecer tu contraseña.
Si no fuiste tú, ignora este correo.

Para recuperar tu contraseña, haz clic en el siguiente enlace:
{reset_url}

Este enlace expira en 1 hora.

Saludos,
Equipo Weigence
        """
        
        # HTML
        html = f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #0f3567;">Recuperación de Contraseña</h2>
      
      <p>Hola <strong>{nombre_usuario or 'Usuario'}</strong>,</p>
      
      <p>Recibimos una solicitud para restablecer tu contraseña en <strong>Weigence Inventory</strong>.</p>
      
      <p>Si no fuiste tú, puedes ignorar este correo con seguridad.</p>
      
      <div style="margin: 30px 0; text-align: center;">
        <a href="{reset_url}" 
           style="display: inline-block; padding: 12px 30px; background-color: #0f3567; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
          Restablecer Contraseña
        </a>
      </div>
      
      <p style="font-size: 12px; color: #666;">
        <strong>Nota:</strong> Este enlace expira en 1 hora.<br>
        Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
        <code style="background-color: #f5f5f5; padding: 5px; border-radius: 3px;">{reset_url}</code>
      </p>
      
      <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
      
      <p style="font-size: 12px; color: #999;">
        © 2025 Weigence Inventory. Todos los derechos reservados.
      </p>
    </div>
  </body>
</html>
        """
        
        # Adjuntar partes
        parte_texto = MIMEText(texto_plano, "plain")
        parte_html = MIMEText(html, "html")
        mensaje.attach(parte_texto)
        mensaje.attach(parte_html)
        
        # Enviar correo
        print(f"[EMAIL] Conectando a {MAIL_SERVER}:{MAIL_PORT}...")
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as servidor:
            servidor.starttls()
            servidor.login(MAIL_USERNAME, MAIL_PASSWORD)
            servidor.send_message(mensaje)
        
        print(f"[EMAIL] ✅ Correo enviado exitosamente a: {email_destino}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(f"[EMAIL] ❌ Error de autenticación SMTP. Verifica MAIL_USERNAME y MAIL_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        print(f"[EMAIL] ❌ Error SMTP: {e}")
        return False
    except Exception as e:
        print(f"[EMAIL] ❌ Error enviando correo: {e}")
        return False


def verificar_token_valido(email, token):
    """
    Verifica si un token de recuperación es válido y no ha expirado
    """
    try:
        registro = supabase.table("password_reset_tokens").select("*").eq("email", email).eq("token", token).execute().data
        
        if not registro:
            print(f"[EMAIL] Token no encontrado para: {email}")
            return False
        
        token_data = registro[0]
        
        # Verificar si ya fue usado
        if token_data.get("usado"):
            print(f"[EMAIL] Token ya fue utilizado: {email}")
            return False
        
        # Verificar expiración
        expiracion = datetime.fromisoformat(token_data.get("expires_at"))
        if datetime.now() > expiracion:
            print(f"[EMAIL] Token expirado para: {email}")
            return False
        
        print(f"[EMAIL] ✅ Token válido para: {email}")
        return True
        
    except Exception as e:
        print(f"[EMAIL] Error verificando token: {e}")
        return False


def marcar_token_usado(email, token):
    """Marca un token como usado después de cambiar la contraseña"""
    try:
        supabase.table("password_reset_tokens").update({
            "usado": True
        }).eq("email", email).eq("token", token).execute()
        
        print(f"[EMAIL] Token marcado como usado: {email}")
        return True
    except Exception as e:
        print(f"[EMAIL] Error marcando token como usado: {e}")
        return False
