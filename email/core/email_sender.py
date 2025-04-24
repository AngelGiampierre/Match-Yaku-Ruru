"""
Funciones para enviar correos usando SMTP.
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import streamlit as st # Para mensajes

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales (con valores por defecto por si no están en .env)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587)) # Convertir a int
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

def send_single_email(recipient_email: str, subject: str, html_content: str):
    """
    Envía un único correo electrónico usando la configuración SMTP del .env.

    Args:
        recipient_email: Email del destinatario.
        subject: Asunto del correo.
        html_content: Contenido HTML del correo.

    Raises:
        Exception: Si ocurre un error durante la conexión o el envío.
    """
    if not all([EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
        st.error("Error: Faltan credenciales de correo (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD) en el archivo .env")
        raise ValueError("Credenciales de correo no configuradas.")

    sender_email = EMAIL_HOST_USER

    # Crear el mensaje
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"Yachay Wasi Notificaciones <{sender_email}>" # Nombre amigable
    message["To"] = recipient_email

    # Adjuntar parte HTML - Especificar UTF-8
    part_html = MIMEText(html_content, "html", _charset="utf-8")
    message.attach(part_html)

    # Intentar conexión y envío
    try:
        # Usar conexión segura con STARTTLS (recomendado para puerto 587)
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.ehlo() # Can be omitted
            server.starttls() # Secure the connection
            server.ehlo() # Can be omitted
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print(f"Correo enviado exitosamente a {recipient_email}") # Log para consola
    except smtplib.SMTPAuthenticationError:
        st.error(f"Error de autenticación SMTP. Verifica usuario/contraseña o configuración de 'Contraseña de aplicación' en Gmail.")
        raise
    except Exception as e:
        st.error(f"Error al enviar correo a {recipient_email}: {e}")
        raise # Re-lanzar la excepción para que se capture en el bucle principal 