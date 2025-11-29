"""
Guía de Instalación y Configuración - Weigence Inventory
=========================================================

INSTALACIÓN COMPLETA
====================

1. CLONAR EL REPOSITORIO
-------------------------
git clone https://github.com/tu-usuario/weigence-project.git
cd weigence-project/weigence


2. CREAR ENTORNO VIRTUAL
-------------------------
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate


3. INSTALAR DEPENDENCIAS
-------------------------
# Producción
pip install -r app/requirements.txt

# Desarrollo (incluye testing, linting, etc.)
pip install -r app/requirements.txt -r requirements-dev.txt


4. CONFIGURAR VARIABLES DE ENTORNO
-----------------------------------
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env y configurar:
# - SUPABASE_KEY y SUPABASE_URL
# - Credenciales de correo (MAIL_USERNAME, MAIL_PASSWORD)
# - SECRET_KEY (generar con: python -c "import secrets; print(secrets.token_hex(32))")


5. CONFIGURAR SUPABASE
----------------------
a) Crear cuenta en https://supabase.com
b) Crear nuevo proyecto
c) Ejecutar el SQL de migrations/password_reset_tokens.sql
d) Copiar la URL y API Key al archivo .env


6. CONFIGURAR CORREO GMAIL
---------------------------
a) Activar verificación en 2 pasos: https://myaccount.google.com/security
b) Generar contraseña de aplicación: https://myaccount.google.com/apppasswords
c) Copiar la contraseña (16 caracteres) a MAIL_PASSWORD en .env


7. MIGRAR CONTRASEÑAS (SI YA TIENES USUARIOS)
----------------------------------------------
python scripts/migrar_passwords.py


8. INICIAR LA APLICACIÓN
-------------------------
# Desarrollo (con livereload)
python app.py

# Producción
# Configurar FLASK_ENV=production en .env
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"


VERIFICACIÓN
============

1. Abrir navegador: http://localhost:5000
2. Iniciar sesión con tus credenciales
3. Verificar que todas las funciones están operativas


SEGURIDAD EN PRODUCCIÓN
========================

Antes de desplegar a producción, ASEGÚRATE de:

✅ Cambiar SECRET_KEY a una clave única y segura
✅ Configurar SESSION_COOKIE_SECURE=True en .env
✅ Configurar FLASK_ENV=production en .env
✅ Usar HTTPS (certificado SSL)
✅ Cambiar todas las credenciales de Supabase y correo
✅ Revisar que .env esté en .gitignore
✅ Nunca commitear archivos .env al repositorio


PROBLEMAS COMUNES
=================

1. Error: "SECRET_KEY no configurada"
   → Agregar SECRET_KEY a tu archivo .env

2. Error: "No se puede conectar a Supabase"
   → Verificar SUPABASE_URL y SUPABASE_KEY en .env

3. Error: "Contraseña incorrecta"
   → Ejecutar el script de migración: python scripts/migrar_passwords.py

4. Correos no se envían
   → Verificar MAIL_USERNAME y MAIL_PASSWORD
   → Verificar que tengas contraseña de aplicación de Gmail


DOCUMENTACIÓN
=============

- Sistema de Roles: Ver GUIA_RAPIDA_ROLES.md
- API: Ver DOCUMENTACION_API.md (si existe)
- Testing: Ver GUIA_TESTING_COMPLETA.md


CONTACTO
========

Para soporte o reportar problemas:
- GitHub Issues: https://github.com/tu-usuario/weigence-project/issues
