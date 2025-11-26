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
        print(f"[EMAIL] 📝 Almacenando token para: {email}")
        expiracion = datetime.now() + timedelta(hours=1)
        print(f"[EMAIL] ⏰ Expiración configurada para: {expiracion.isoformat()}")
        
        # Verificar si ya existe un token para este email
        print(f"[EMAIL] 🔍 Buscando tokens existentes para: {email}")
        tokens_existentes = supabase.table("token").select("*").eq("correo", email).execute().data
        print(f"[EMAIL] Tokens existentes encontrados: {len(tokens_existentes)}")
        
        if tokens_existentes:
            # Actualizar token existente
            print(f"[EMAIL] 🔄 Actualizando token existente para: {email}")
            resultado = supabase.table("token").update({
                "token": token,
                "expires_at": expiracion.isoformat(),
                "usado": False
            }).eq("correo", email).execute()
            print(f"[EMAIL] ✅ Token actualizado: {resultado}")
        else:
            # Crear nuevo registro
            print(f"[EMAIL] ➕ Creando nuevo registro de token para: {email}")
            resultado = supabase.table("token").insert({
                "correo": email,
                "token": token,
                "expires_at": expiracion.isoformat(),
                "usado": False
            }).execute()
            print(f"[EMAIL] ✅ Nuevo token creado: {resultado}")
        
        print(f"[EMAIL] ✅✅ Token de recuperación almacenado exitosamente para: {email}")
        return True
    except Exception as e:
        print(f"[EMAIL] ❌❌ Error almacenando token: {e}")
        print(f"[EMAIL] Tipo de error: {type(e).__name__}")
        import traceback
        print(f"[EMAIL] Stack trace completo:\n{traceback.format_exc()}")
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
        print(f"[EMAIL] 🚀 Iniciando proceso de envío de correo para: {email_destino}")
        
        # Obtener configuración de variables de entorno
        # Forzar recarga del .env
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
        MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
        MAIL_USERNAME = os.getenv("MAIL_USERNAME")
        MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
        MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)
        BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
        
        print(f"[EMAIL] 📧 Configuración SMTP:")
        print(f"[EMAIL]   - Servidor: {MAIL_SERVER}:{MAIL_PORT}")
        print(f"[EMAIL]   - Usuario: {MAIL_USERNAME}")
        print(f"[EMAIL]   - Password (primeros 4): {MAIL_PASSWORD[:4] if MAIL_PASSWORD else 'None'}...")
        print(f"[EMAIL]   - From: {MAIL_FROM}")
        print(f"[EMAIL]   - Base URL: {BASE_URL}")
        
        # Validar configuración
        if not MAIL_USERNAME or not MAIL_PASSWORD:
            print("[EMAIL] ⚠️ Variables MAIL_USERNAME o MAIL_PASSWORD no configuradas")
            print("[EMAIL] Para habilitar: Configure en .env las credenciales SMTP")
            return False
        
        # Generar token
        print(f"[EMAIL] 🔑 Generando token de recuperación...")
        token = generar_token_recuperacion()
        print(f"[EMAIL] Token generado (primeros 10 caracteres): {token[:10]}...")
        
        # Almacenar token
        print(f"[EMAIL] 💾 Almacenando token en BD...")
        if not almacenar_token_recuperacion(email_destino, token):
            print("[EMAIL] ❌ Fallo al almacenar token - Abortando envío")
            return False
        print(f"[EMAIL] ✅ Token almacenado correctamente")
        
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
        print("="*80)
        print(f"[EMAIL-VERIFY] ========== INICIO VERIFICACIÓN ==========")
        print(f"[EMAIL-VERIFY] Email recibido: '{email}'")
        print(f"[EMAIL-VERIFY] Token recibido (primeros 20): '{token[:20] if token else 'VACÍO'}'")
        print(f"[EMAIL-VERIFY] Token completo: '{token}'")
        
        # Buscar en la base de datos
        print(f"[EMAIL-VERIFY] 🔍 Buscando en tabla 'token'...")
        print(f"[EMAIL-VERIFY]   WHERE correo = '{email}'")
        print(f"[EMAIL-VERIFY]   AND token = '{token[:20]}...'")
        
        registro = supabase.table("token").select("*").eq("correo", email).eq("token", token).execute().data
        
        print(f"[EMAIL-VERIFY] 📊 Registros encontrados: {len(registro)}")
        print(f"[EMAIL-VERIFY] Datos completos: {registro}")
        
        if not registro:
            print(f"[EMAIL-VERIFY] ❌ Token NO encontrado en BD para: {email}")
            
            # Buscar TODOS los tokens de este email para debug
            print(f"[EMAIL-VERIFY] 🔍 Buscando TODOS los tokens de {email}...")
            todos_tokens = supabase.table("token").select("*").eq("correo", email).execute().data
            print(f"[EMAIL-VERIFY] Total tokens para {email}: {len(todos_tokens)}")
            for idx, t in enumerate(todos_tokens):
                print(f"[EMAIL-VERIFY]   Token #{idx+1}:")
                print(f"[EMAIL-VERIFY]     - id_token: {t.get('id_token')}")
                print(f"[EMAIL-VERIFY]     - token: {t.get('token')[:20]}...")
                print(f"[EMAIL-VERIFY]     - usado: {t.get('usado')}")
                print(f"[EMAIL-VERIFY]     - expires_at: {t.get('expires_at')}")
            
            return False
        
        token_data = registro[0]
        print(f"[EMAIL-VERIFY] ✅ Token encontrado en BD!")
        print(f"[EMAIL-VERIFY]   - id_token: {token_data.get('id_token')}")
        print(f"[EMAIL-VERIFY]   - correo: {token_data.get('correo')}")
        print(f"[EMAIL-VERIFY]   - usado: {token_data.get('usado')}")
        print(f"[EMAIL-VERIFY]   - expires_at: {token_data.get('expires_at')}")
        
        # Verificar si ya fue usado
        usado = token_data.get("usado")
        print(f"[EMAIL-VERIFY] 🔒 Verificando estado 'usado': {usado}")
        if usado:
            print(f"[EMAIL-VERIFY] ❌ Token ya fue utilizado para: {email}")
            return False
        print(f"[EMAIL-VERIFY] ✅ Token NO ha sido usado")
        
        # Verificar expiración
        expires_at_str = token_data.get("expires_at")
        print(f"[EMAIL-VERIFY] ⏰ Verificando expiración...")
        print(f"[EMAIL-VERIFY]   - expires_at (string): {expires_at_str}")
        
        expiracion = datetime.fromisoformat(expires_at_str)
        ahora = datetime.now()
        print(f"[EMAIL-VERIFY]   - Expira en: {expiracion}")
        print(f"[EMAIL-VERIFY]   - Hora actual: {ahora}")
        print(f"[EMAIL-VERIFY]   - Diferencia: {(expiracion - ahora).total_seconds()} segundos")
        
        if ahora > expiracion:
            print(f"[EMAIL-VERIFY] ❌ Token EXPIRADO para: {email}")
            return False
        print(f"[EMAIL-VERIFY] ✅ Token NO expirado")
        
        print(f"[EMAIL-VERIFY] ✅✅ Token VÁLIDO para: {email}")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"[EMAIL-VERIFY] ❌❌ EXCEPTION: {str(e)}")
        import traceback
        print(f"[EMAIL-VERIFY] Traceback:\n{traceback.format_exc()}")
        print("="*80)
        return False


def marcar_token_usado(email, token):
    """Marca un token como usado después de cambiar la contraseña"""
    try:
        supabase.table("token").update({
            "usado": True
        }).eq("correo", email).eq("token", token).execute()
        
        print(f"[EMAIL] Token marcado como usado: {email}")
        return True
    except Exception as e:
        print(f"[EMAIL] Error marcando token como usado: {e}")
        return False
