"""
Pestaña para generar Asunto y Cuerpo de Correo (HTML) para Yakus
basado en el archivo final de asignaciones. Permite procesar uno por uno.
"""
import streamlit as st
import pandas as pd
from io import BytesIO
import html  # Para escapar caracteres especiales si es necesario en el futuro

# --- Importar clean_str_number (Reutilizar) ---
try:
    from ..utils.output_generator import clean_str_number
except ImportError:
    print("ADVERTENCIA: No se pudo importar clean_str_number desde utils. Usando fallback.")
    def clean_str_number(val):
        if pd.isna(val) or val == '': return ''
        try: cleaned_val = str(int(float(str(val))))
        except (ValueError, TypeError): cleaned_val = str(val).strip()
        if cleaned_val.endswith('.0'): cleaned_val = cleaned_val[:-2]
        return cleaned_val

# --- Constantes de Texto ---
# (Mover textos largos aquí hace el código más limpio)

EMAIL_SUBJECT_TEMPLATE = "[YACHAY WASI-RESULTADOS] ¡Bienvenido, Yaku" # Asunto base sin !

# --- AJUSTE: Modificar template con nueva temporada y fecha de contacto ---
BASE_HTML_TEMPLATE = """
<p>¡Hola, Yaku {yaku_nombre}!</p>

<p>Recibe un cálido saludo del área de {area_nombre_display}. Te escribimos para comunicarte que has sido elegido como Yaku Asesor para la temporada <strong>2025-I</strong>.</p>

<p>De parte de todo el equipo queremos transmitir nuestra emoción y agradecimiento hacia ti.</p>

<p>Nos alegra que seas parte de este equipo que busca mejorar la educación del Perú. {intro_especifica_area} Pronto conocerás a tu Ruru y esperamos que ambos/as tengan una gran experiencia de aprendizaje.</p>

<p>Antes de compartir esta increíble experiencia te pedimos completar los siguientes pasos para formalizar tu voluntariado:</p>
<ul>
    <li>Formulario de carta de compromiso</li>
    <li>En el siguiente formulario buscamos recolectar tu carta de compromiso firmada junto con información importante para las asesorías.</li>
    <li>Leer el Manual y Reglamento interno del Yaku Asesor adjuntos en el correo.</li>
</ul>
<p>🗓️ <strong>INICIO DE LAS ASESORÍAS:</strong> desde el <strong>28 de abril del 2025</strong></p>

<p>Estaremos coordinando por nuestro grupo de Whatsapp, siéntete en libertad de hacer tus consultas a este correo.</p>

<p>Asimismo, con mucha alegría te compartimos la información sobre tu nuevo ruru.</p>

<p><strong>A partir de hoy, 26 de abril</strong> podrás contactarte con tu ruru, conocerlo y coordinar con sus padres las asesorías de las siguientes semanas. Para ello, podrás utilizar la 'guía para el primer contacto con el ruru'. A continuación, te compartimos información relevante para tu rol de Yaku Asesor:</p>

<ul>
    <li><strong>DNI del Yaku:</strong> {yaku_dni}</li>
    <li><strong>Yaku ID:</strong> {yaku_id}</li>
    <li><strong>Ruru ID:</strong> {ruru_id}</li>
    <!-- Celulares se manejarán con las variables condicionales -->
    {celular_asesoria_display}
    {celular_apoderado_display}
    <li><strong>Toolkit:</strong> <a href="https://sites.google.com/view/toolkityakuasesor/inicio?authuser=4">https://sites.google.com/view/toolkityakuasesor/inicio?authuser=4</a></li>
    <li><strong>Guía para el primer contacto con el ruru:</strong> <a href="https://sites.google.com/view/toolkityakuasesor/somos-yakus-asesores/primer-contacto-con-ruru?authuser=0">https://sites.google.com/view/toolkityakuasesor/somos-yakus-asesores/primer-contacto-con-ruru?authuser=0</a></li>
</ul>

<p>Ante cualquier duda que tengas, no dudes en comunicarle a tu Yaku Guía, debido a su experiencia como Yaku Asesor en temporadas previas, podrá guiarte para que tengas el mejor vínculo con tu ruru.</p>

<p>¡Muchas gracias!</p>
"""

# --- Pestaña Streamlit ---
def email_generator_tab():
    st.header("Generador de Contenido de Correo para Yakus")
    st.write("Sube el archivo Excel final del match para generar el Asunto y Cuerpo (HTML) de los correos de bienvenida para cada Yaku.")

    # Estado de sesión específico
    if 'emailgen_excel_data' not in st.session_state: st.session_state.emailgen_excel_data = None
    if 'emailgen_area' not in st.session_state: st.session_state.emailgen_area = "Bienestar Psicológico"
    if 'emailgen_generated_content' not in st.session_state: st.session_state.emailgen_generated_content = []
    # --- NUEVO: Estado para rastrear el índice actual ---
    if 'emailgen_current_index' not in st.session_state: st.session_state.emailgen_current_index = 0

    # Selector de Área
    area_options = ["Bienestar Psicológico", "Asesoría a Colegios Nacionales", "Arte & Cultura"]
    selected_area = st.selectbox(
        "Selecciona el Área para generar correos:",
        area_options,
        index=area_options.index(st.session_state.emailgen_area),
        key="emailgen_area_selector"
    )

    # Resetear si cambia el área
    if st.session_state.emailgen_area != selected_area:
        st.session_state.emailgen_area = selected_area
        st.session_state.emailgen_excel_data = None
        st.session_state.emailgen_generated_content = []
        st.session_state.emailgen_current_index = 0 # Resetear índice también
        st.rerun()

    st.subheader(f"Paso 1: Cargar Archivo Excel para '{selected_area}'")

    uploaded_excel = st.file_uploader("Cargar Excel Final del Match (.xlsx)", type=["xlsx", "xls"], key="emailgen_excel_upload")

    # Cargar datos a sesión
    if uploaded_excel:
        if st.session_state.emailgen_excel_data is None: # Cargar solo si no está cargado
            try:
                df_asignaciones = pd.read_excel(uploaded_excel, sheet_name="Asignaciones")
                if 'Area' in df_asignaciones.columns:
                     df_filtrado = df_asignaciones[df_asignaciones['Area'] == selected_area].copy()
                     if df_filtrado.empty:
                         st.warning(f"No se encontraron asignaciones para el área '{selected_area}'.")
                         st.session_state.emailgen_excel_data = pd.DataFrame() # Guardar DF vacío
                         st.session_state.emailgen_generated_content = [] # Asegurar limpieza
                         st.session_state.emailgen_current_index = 0
                     else:
                         st.success(f"Se cargaron {len(df_filtrado)} asignaciones para '{selected_area}'.")
                         st.session_state.emailgen_excel_data = df_filtrado
                         # Resetear contenido e índice si se carga nuevo archivo con datos
                         st.session_state.emailgen_generated_content = []
                         st.session_state.emailgen_current_index = 0
                else:
                     st.error("Error: La hoja 'Asignaciones' no contiene la columna 'Area'.")
                     st.session_state.emailgen_excel_data = None

            except Exception as e:
                st.error(f"Error al leer el archivo Excel: {e}")
                st.session_state.emailgen_excel_data = None

    # Botón para generar
    if st.session_state.emailgen_excel_data is not None and not st.session_state.emailgen_excel_data.empty:
        st.subheader("Paso 2: Generar Contenido de Correos")
        if not st.session_state.emailgen_generated_content:
            if st.button(f"Generar Correos para {selected_area}", key="emailgen_generate_button"):
                with st.spinner("Generando contenido de correos..."):
                    df_data = st.session_state.emailgen_excel_data
                    area_actual = st.session_state.emailgen_area
                    generated_content_list = []
                    errors = []

                    # Nombres de columnas esperados (ajusta si es necesario)
                    col_yaku_nombre = 'Nombre Yaku'
                    col_yaku_id = 'ID Yaku'
                    col_yaku_dni = 'DNI Yaku'
                    col_yaku_correo = 'Correo Yaku' # <-- Añadir columna de correo
                    col_ruru_id = 'ID Ruru'
                    col_cel_asesoria = 'Celular Asesoria Ruru' # Nombre columna en Excel
                    col_cel_apoderado = 'Celular Apoderado Ruru' # Nombre columna en Excel
                    col_asignatura_taller = 'Asignatura/Taller Asignado'

                    for index, row in df_data.iterrows():
                        try:
                            # Extraer datos necesarios
                            yaku_nombre = str(row.get(col_yaku_nombre, 'Yaku')).strip()
                            yaku_id = clean_str_number(row.get(col_yaku_id, 'N/A'))
                            yaku_dni = clean_str_number(row.get(col_yaku_dni, 'N/A'))
                            yaku_correo = str(row.get(col_yaku_correo, '')).strip() # <-- Obtener correo
                            ruru_id = clean_str_number(row.get(col_ruru_id, 'N/A'))
                            asignatura_taller = str(row.get(col_asignatura_taller, 'N/A')).strip()

                            # Generar Asunto Personalizado (opcional, aquí usamos el base)
                            subject = f"{EMAIL_SUBJECT_TEMPLATE} {yaku_nombre}!"

                            # Determinar contenido específico por área
                            intro_especifica = ""
                            area_display = area_actual # Nombre para mostrar en el saludo

                            if area_actual == "Arte & Cultura":
                                intro_especifica = f"Compartirás tus conocimientos y gusto por {asignatura_taller}."
                                area_display = "Arte y Cultura" # Ajustar si el nombre difiere ligeramente
                            elif area_actual == "Asesoría a Colegios Nacionales":
                                intro_especifica = f"Compartirás tus conocimientos en {asignatura_taller}."
                                area_display = "Asesorías a Colegios Nacionales"
                            elif area_actual == "Bienestar Psicológico":
                                intro_especifica = "" # Sin frase adicional para BP (o añade una si existe)
                                area_display = "Bienestar Psicológico"

                            # --- Lógica condicional para celulares ---
                            cel_asesoria_clean = clean_str_number(row.get(col_cel_asesoria))
                            cel_apoderado_clean = clean_str_number(row.get(col_cel_apoderado))

                            cel_asesoria_html = ""
                            if cel_asesoria_clean:
                                cel_asesoria_html = f"<li><strong>Celular para las asesorías:</strong> {cel_asesoria_clean}</li>"

                            cel_apoderado_html = ""
                            if cel_apoderado_clean:
                                # Aquí podrías incluir o no el título "Celular del Apoderado:" si lo deseas
                                cel_apoderado_html = f"<li><strong>Celular del Apoderado:</strong> {cel_apoderado_clean}</li>"
                            # --- Fin lógica celulares ---

                            # Crear contexto para el template HTML
                            context = {
                                "yaku_nombre": html.escape(yaku_nombre), # Escapar por si hay caracteres especiales
                                "area_nombre_display": area_display,
                                "intro_especifica_area": intro_especifica,
                                "yaku_dni": yaku_dni,
                                "yaku_id": yaku_id,
                                "ruru_id": ruru_id,
                                # Pasar las cadenas HTML formateadas condicionalmente
                                "celular_asesoria_display": cel_asesoria_html,
                                "celular_apoderado_display": cel_apoderado_html,
                            }

                            # Formatear el HTML
                            html_body = BASE_HTML_TEMPLATE.format(**context)

                            generated_content_list.append({
                                "yaku_nombre": yaku_nombre,
                                "yaku_id": yaku_id,
                                "yaku_correo": yaku_correo, # <-- Guardar correo
                                "subject": subject,
                                "html_body": html_body
                            })

                        except Exception as e_row:
                            errors.append(f"Error procesando fila {index} (Yaku ID: {row.get(col_yaku_id, 'N/A')}): {e_row}")

                    st.session_state.emailgen_generated_content = generated_content_list
                    st.session_state.emailgen_current_index = 0 # Empezar desde el principio
                    if generated_content_list:
                        st.success(f"Se generó el contenido para {len(generated_content_list)} correos.")
                    if errors:
                        st.error("Ocurrieron errores durante la generación:")
                        for err in errors:
                            st.error(f"- {err}")
                    # Forzar re-render para mostrar el primer correo
                    st.rerun()

    # Mostrar contenido generado
    if st.session_state.emailgen_generated_content:
        st.subheader("Paso 3: Copiar Contenido de Correo")

        # Obtener la lista y el índice actual
        content_list = st.session_state.emailgen_generated_content
        current_index = st.session_state.emailgen_current_index
        total_emails = len(content_list)

        if 0 <= current_index < total_emails:
            # Mostrar el correo actual
            content = content_list[current_index]

            st.markdown(f"---")
            st.markdown(f"**Mostrando Correo {current_index + 1} de {total_emails}**")
            st.markdown(f"**Para:** {content['yaku_nombre']} (ID: {content['yaku_id']})")

            # --- Añadir campo para mostrar/copiar correo ---
            st.text_input(
                "Correo Yaku (Destinatario):",
                value=content.get('yaku_correo', 'No encontrado'), # Usar .get para seguridad
                key=f"email_{content['yaku_id']}_{current_index}",
                help="Copia la dirección de correo del Yaku."
            )

            st.text_input("Asunto:", value=content['subject'], key=f"subj_{content['yaku_id']}_{current_index}", help="Copia este asunto personalizado.")
            st.text_area(
                "Cuerpo HTML:",
                value=content['html_body'],
                height=400, # Ajusta la altura según necesites
                key=f"html_{content['yaku_id']}_{current_index}",
                help="Selecciona todo (Cmd+A o Ctrl+A) y copia (Cmd+C o Ctrl+C)."
            )
            st.caption("👆 Haz clic en el cuadro de arriba, selecciona todo y copia el HTML.")

            # Botón de Siguiente
            if st.button("Siguiente Correo ➡️", key=f"next_email_{current_index}"):
                st.session_state.emailgen_current_index += 1
                st.rerun() # Re-renderizar para mostrar el siguiente o el mensaje final

        elif current_index >= total_emails:
            # Todos los correos han sido mostrados
            st.success("🎉 ¡Has revisado todos los correos generados para esta área!")
            st.balloons()
            # Opcional: Botón para reiniciar desde el principio para esta área
            if st.button("Revisar de Nuevo"):
                 st.session_state.emailgen_current_index = 0
                 st.rerun()
        else:
             # Índice inválido (no debería ocurrir pero por si acaso)
             st.warning("Índice de correo inválido.")
             st.session_state.emailgen_current_index = 0 # Resetear

    elif st.session_state.emailgen_excel_data is not None and st.session_state.emailgen_excel_data.empty:
        st.info(f"No hay asignaciones para el área '{st.session_state.emailgen_area}' en el archivo cargado.")
    else:
         st.info("Carga el archivo Excel final para generar el contenido de los correos.") 