"""
Página principal del módulo de Preparación Manual de Correos en Streamlit.

Permite cargar el archivo de resultados del match, seleccionar una asignación
y obtener el asunto y cuerpo del correo personalizado para el Yaku, listo para copiar.
"""
import streamlit as st
import pandas as pd

# Importar solo el gestor de plantillas
from .core.template_manager import get_yaku_email_body

# Columnas mínimas requeridas en la hoja 'Asignaciones'
REQUIRED_ASSIGNMENT_COLS = [
    'Correo Yaku', 'Nombre Yaku', 'Nombre Ruru', 'Grado Original Ruru', 'Area',
    'Nombre Apoderado Ruru', 'Celular Apoderado Ruru', 'Celular Asesoria Ruru',
    'Quechua Yaku', 'Quechua Ruru', 'Asignatura/Taller Asignado'
]

def email_page():
    """Renderiza la página de preparación manual de correos."""
    st.title(" Módulo de Preparación Manual de Correos")
    st.write("""
    Carga el archivo Excel con los resultados del match, selecciona una asignación
    y copia el asunto y el cuerpo del correo para enviarlo manualmente a cada Yaku.
    """)

    # --- Carga de Archivo de Resultados ---
    st.header("1. Cargar Resultados del Match")
    uploaded_results_file = st.file_uploader(
        "Cargar archivo Excel de resultados (generado por el módulo Match)",
        type=["xlsx", "xls"],
        key="email_prep_results_upload"
    )

    # Usar estado de sesión para el DataFrame
    if 'assignments_prep_df' not in st.session_state:
         st.session_state.assignments_prep_df = None

    if uploaded_results_file:
        try:
            temp_df = pd.read_excel(uploaded_results_file, sheet_name='Asignaciones')
            missing = [col for col in REQUIRED_ASSIGNMENT_COLS if col not in temp_df.columns]
            if missing:
                st.error(f"❌ El archivo Excel no contiene las columnas requeridas en la hoja 'Asignaciones': {', '.join(missing)}")
                st.session_state.assignments_prep_df = None
            else:
                # Crear una columna legible para el selector
                temp_df['display_label'] = temp_df.apply(lambda row: f"{row['Nombre Yaku']} - {row['Nombre Ruru']} ({row['ID Yaku']})", axis=1)
                st.session_state.assignments_prep_df = temp_df
                st.success(f"✅ Archivo de resultados cargado. Se encontraron {len(st.session_state.assignments_prep_df)} asignaciones.")
                with st.expander("Vista previa de Asignaciones Cargadas"):
                    st.dataframe(st.session_state.assignments_prep_df[['display_label', 'ID Yaku', 'ID Ruru', 'Correo Yaku']].head())

        except Exception as e:
            st.error(f"❌ Error al leer la hoja 'Asignaciones' del archivo Excel: {e}")
            st.session_state.assignments_prep_df = None

    # Acceder al DataFrame desde el estado de sesión
    assignments_df = st.session_state.assignments_prep_df

    # --- Selección de Asignación y Generación de Correo ---
    st.header("2. Preparar Correo Individual")

    if assignments_df is not None and not assignments_df.empty:
        # Selector para elegir la asignación
        assignment_labels = assignments_df['display_label'].tolist()
        selected_label = st.selectbox(
            "Selecciona la asignación para preparar el correo:",
            options=assignment_labels,
            index=0, # Empezar con la primera por defecto
            key="assignment_selector"
        )

        if selected_label:
            # Obtener la fila completa de datos para la selección
            selected_row = assignments_df[assignments_df['display_label'] == selected_label].iloc[0]

            # Generar contenido del correo
            email_to = selected_row.get('Correo Yaku', 'Correo no encontrado')
            ruru_name = selected_row.get('Nombre Ruru', 'N/A')
            subject = f"¡Asignación Yachay Wasi: Conoce a tu Ruru {ruru_name}!"
            try:
                html_body = get_yaku_email_body(selected_row)

                st.subheader("Correo Listo para Copiar y Pegar:")

                # --- Destinatario y Asunto ---
                st.write("Destinatario (Para):")
                st.code(email_to, language='text')
                st.write("Asunto:")
                st.code(subject, language='text')
                # --- Fin Destinatario y Asunto ---

                st.markdown("---") # Separador

                # --- Cuerpo del Correo (Renderizado con Fondo Blanco Forzado) ---
                st.write("**Cuerpo del Correo (Selecciona y Copia el texto de abajo):**")

                # --- CSS Personalizado para Forzar Fondo Blanco ---
                # Este CSS apunta a un div con la clase 'email-preview-container'
                # que pondremos alrededor del markdown. !important asegura prioridad.
                st.markdown("""
                <style>
                .email-preview-container {
                    background-color: white !important;
                    color: black !important; /* Asegura texto legible */
                    padding: 15px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                /* Asegura que los elementos dentro hereden el color de texto */
                .email-preview-container * {
                    color: black !important;
                    background-color: transparent !important; /* Evita otros fondos internos */
                }
                </style>
                """, unsafe_allow_html=True)
                # --- Fin CSS Personalizado ---

                # Envolver el markdown en un div con la clase específica
                st.markdown(f'<div class="email-preview-container">{html_body}</div>', unsafe_allow_html=True)
                # --- Fin Cuerpo del Correo ---

                st.markdown("---") # Separador

                # --- Instrucciones Simplificadas ---
                st.info(
                    "**Instrucciones para Enviar Manualmente:**\n"
                    "1. Usa los botones de copia para 'Destinatario' y 'Asunto' y pégalos en Gmail.\n"
                    "2. Selecciona TODO el texto dentro del cuadro **'Cuerpo del Correo'** de arriba.\n"
                    "3. Copia el texto seleccionado (Ctrl+C o Cmd+C) y pégalo en el cuerpo de Gmail.\n"
                    "4. El formato y el fondo *deberían* pegarse correctamente ahora. Revisa y envía."
                 )

            except Exception as e:
                st.error(f"Error al generar el cuerpo del correo: {e}")

    else:
        st.info("Carga un archivo de resultados válido para preparar los correos.") 