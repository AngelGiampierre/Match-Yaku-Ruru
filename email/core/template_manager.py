"""
Gestiona la plantilla de correo y la personalización con datos.
"""
import pandas as pd

# Plantilla HTML base para el correo del Yaku
# (Confirmada previamente)
YAKU_EMAIL_TEMPLATE = """
<p>Hola [Nombre Yaku],</p>
<p>¡Tenemos excelentes noticias desde Yachay Wasi!</p>
<p>Nos complace informarte que has sido asignado(a) para acompañar a un Ruru (estudiante) en el área de <strong>[Area]</strong>. ¡Tu apoyo será fundamental!</p>
<p><strong>Detalles de tu Ruru asignado:</strong></p>
<ul>
    <li><strong>Nombre:</strong> [Nombre Ruru]</li>
    <li><strong>Grado:</strong> [Grado Original Ruru]</li>
    [SI_ASIGNATURA_TALLER]<li><strong>Asignatura/Taller a reforzar:</strong> [Asignatura/Taller Asignado]</li>[/SI_ASIGNATURA_TALLER]
</ul>
<p><strong>Información de contacto del Apoderado/a:</strong></p>
<ul>
    <li><strong>Nombre:</strong> [Nombre Apoderado Ruru]</li>
    <li><strong>Celular Principal:</strong> [Celular Apoderado Ruru]</li>
    [SI_CELULAR_ASESORIA]<li><strong>Celular Secundario (Asesoría):</strong> [Celular Asesoria Ruru]</li>[/SI_CELULAR_ASESORIA]
</ul>
<p><strong>Compatibilidad Horaria:</strong></p>
<p>Hemos confirmado que existen horarios compatibles entre tu disponibilidad y la del Ruru. Te animamos a coordinar directamente con el/la apoderado/a para definir el horario exacto de las sesiones.</p>
[SI_QUECHUA]
<p><strong>¡Extra!</strong> Notamos que tanto tú ([Quechua Yaku]) como el Ruru ([Quechua Ruru]) tienen conocimientos de Quechua. ¡Esto podría enriquecer mucho la comunicación!</p>
[/SI_QUECHUA]
<p><strong>Próximos Pasos:</strong></p>
<p>Te recomendamos ponerte en contacto con el/la apoderado/a durante esta semana para presentarte y empezar a coordinar. Si tienes alguna pregunta o necesitas apoyo, no dudes en contactar al equipo de coordinación de Yachay Wasi.</p>
<p>¡Agradecemos enormemente tu valioso tiempo y compromiso como voluntario(a)!</p>
<p>Saludos cordiales,<br>
El Equipo de Yachay Wasi</p>
"""

def get_yaku_email_body(assignment_data: pd.Series) -> str:
    """
    Genera el cuerpo HTML personalizado para el correo del Yaku.

    Args:
        assignment_data: Una fila (Serie de Pandas) del DataFrame de asignaciones formateado.

    Returns:
        El string HTML del cuerpo del correo personalizado.
    """
    html_body = YAKU_EMAIL_TEMPLATE

    # Reemplazar placeholders básicos
    placeholders = [
        'Nombre Yaku', 'Area', 'Nombre Ruru', 'Grado Original Ruru',
        'Nombre Apoderado Ruru', 'Celular Apoderado Ruru', 'Quechua Yaku', 'Quechua Ruru'
    ]
    for placeholder in placeholders:
        value = assignment_data.get(placeholder, '') # Obtener valor o string vacío
        html_body = html_body.replace(f"[{placeholder}]", str(value)) # Convertir a string

    # Reemplazos condicionales
    # Asignatura/Taller
    asignatura_taller = assignment_data.get('Asignatura/Taller Asignado', '')
    if pd.notna(asignatura_taller) and str(asignatura_taller).strip() != "N/A" and str(asignatura_taller).strip() != "":
        html_body = html_body.replace("[SI_ASIGNATURA_TALLER]", "").replace("[/SI_ASIGNATURA_TALLER]", "")
        html_body = html_body.replace("[Asignatura/Taller Asignado]", str(asignatura_taller))
    else:
        # Eliminar el bloque condicional si no aplica
        start_tag = "[SI_ASIGNATURA_TALLER]"
        end_tag = "[/SI_ASIGNATURA_TALLER]"
        start_index = html_body.find(start_tag)
        end_index = html_body.find(end_tag)
        if start_index != -1 and end_index != -1:
            html_body = html_body[:start_index] + html_body[end_index + len(end_tag):]

    # Celular Asesoria
    celular_asesoria = assignment_data.get('Celular Asesoria Ruru', '')
    if pd.notna(celular_asesoria) and str(celular_asesoria).strip() != "":
         html_body = html_body.replace("[SI_CELULAR_ASESORIA]", "").replace("[/SI_CELULAR_ASESORIA]", "")
         html_body = html_body.replace("[Celular Asesoria Ruru]", str(celular_asesoria))
    else:
        start_tag = "[SI_CELULAR_ASESORIA]"
        end_tag = "[/SI_CELULAR_ASESORIA]"
        start_index = html_body.find(start_tag)
        end_index = html_body.find(end_tag)
        if start_index != -1 and end_index != -1:
            html_body = html_body[:start_index] + html_body[end_index + len(end_tag):]

    # Quechua
    q_yaku = assignment_data.get('Quechua Yaku', 'No lo hablo')
    q_ruru = assignment_data.get('Quechua Ruru', 'No lo hablo')
    if pd.notna(q_yaku) and q_yaku != 'No lo hablo' and pd.notna(q_ruru) and q_ruru != 'No lo hablo':
        html_body = html_body.replace("[SI_QUECHUA]", "").replace("[/SI_QUECHUA]", "")
        # Los placeholders [Quechua Yaku] y [Quechua Ruru] ya fueron reemplazados antes
    else:
         start_tag = "[SI_QUECHUA]"
         end_tag = "[/SI_QUECHUA]"
         start_index = html_body.find(start_tag)
         end_index = html_body.find(end_tag)
         if start_index != -1 and end_index != -1:
             html_body = html_body[:start_index] + html_body[end_index + len(end_tag):]

    return html_body 