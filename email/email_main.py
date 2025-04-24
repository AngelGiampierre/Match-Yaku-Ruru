"""
Página principal del módulo de Envío de Correos en Streamlit.

Permite cargar el archivo de resultados del match y enviar correos
personalizados a los Yakus asignados.
"""
import streamlit as st
import pandas as pd
import time # Importar time para posible delay

# Importaciones futuras
# from .core.email_sender import send_single_email
# from .core.template_manager import get_yaku_email_body

# --- MODIFICADO: Descomentar e importar funciones ---
from .core.email_sender import send_single_email
from .core.template_manager import get_yaku_email_body

def email_page():
    """Renderiza la página de envío de correos."""
    st.title(" Módulo de Envío de Correos")
    st.write("""
    Carga el archivo Excel con los resultados del match y envía correos
    de notificación a cada Yaku asignado.
    """)

    # --- Carga de Archivo de Resultados ---
    st.header("1. Cargar Resultados del Match")
    uploaded_results_file = st.file_uploader(
        "Cargar archivo Excel de resultados (generado por el módulo Match)",
        type=["xlsx", "xls"],
        key="email_results_upload" # Añadir key única
    )

    assignments_df = None
    if 'assignments_email_df' not in st.session_state:
         st.session_state.assignments_email_df = None

    if uploaded_results_file:
        # Cargar solo si no está ya en el estado de sesión o si cambia el archivo
        # (Evita recargar cada vez que se interactúa con la página)
        # Nota: Streamlit podría re-ejecutar y perder el estado si no se maneja con cuidado.
        # Por simplicidad, recargaremos si hay un archivo nuevo.
        try:
            # Leer específicamente la hoja de asignaciones
            temp_df = pd.read_excel(uploaded_results_file, sheet_name='Asignaciones')
            # Validar columnas necesarias para el correo
            required_cols = [
                'Correo Yaku', 'Nombre Yaku', 'Nombre Ruru', 'Grado Original Ruru', 'Area',
                'Nombre Apoderado Ruru', 'Celular Apoderado Ruru', 'Celular Asesoria Ruru',
                'Quechua Yaku', 'Quechua Ruru', 'Asignatura/Taller Asignado' # Asegurarse que estas existen
            ]
            missing = [col for col in required_cols if col not in temp_df.columns]
            if missing:
                st.error(f"❌ El archivo Excel no contiene las columnas requeridas en la hoja 'Asignaciones': {', '.join(missing)}")
                st.session_state.assignments_email_df = None # Invalidar
            else:
                st.session_state.assignments_email_df = temp_df # Guardar en estado si es válido
                st.success(f"✅ Archivo de resultados cargado. Se encontraron {len(st.session_state.assignments_email_df)} asignaciones.")
                with st.expander("Vista previa de Asignaciones"):
                    st.dataframe(st.session_state.assignments_email_df.head())

        except Exception as e:
            st.error(f"❌ Error al leer la hoja 'Asignaciones' del archivo Excel: {e}")
            st.session_state.assignments_email_df = None

    # Acceder al DataFrame desde el estado de sesión
    assignments_df = st.session_state.assignments_email_df

    # --- Envío de Correos ---
    st.header("2. Enviar Correos a Yakus")
    if assignments_df is not None:
        num_assignments = len(assignments_df)
        st.info(f"Listo para enviar {num_assignments} correos a los Yakus asignados.")

        # Selección opcional para enviar solo algunos
        send_all = st.checkbox("Enviar a todos los Yakus listados", value=True, key="send_all_check")
        num_to_send = num_assignments
        if not send_all:
            num_to_send = st.number_input("Número de correos de prueba a enviar:", min_value=1, max_value=num_assignments, value=1, step=1, key="num_test_emails")

        # Opcional: Delay entre correos para evitar rate limiting
        delay_seconds = st.number_input("Delay entre correos (segundos):", min_value=0.0, max_value=10.0, value=0.5, step=0.1, key="email_delay", help="Pequeño delay para evitar ser bloqueado por el proveedor de correo (ej. 0.5)")

        if st.button(f"Enviar {num_to_send if not send_all else 'todos los'} correos", key="send_button"):
            if num_to_send > 0:
                 data_to_send = assignments_df.head(num_to_send) if not send_all else assignments_df
                 progress_bar = st.progress(0)
                 success_count = 0
                 error_count = 0
                 errors = []
                 total_to_process = len(data_to_send)

                 st.write(f"Iniciando envío de {total_to_process} correos...")

                 for index, row in data_to_send.iterrows():
                     # Validar correo del destinatario
                     email_to = row.get('Correo Yaku')
                     if pd.isna(email_to) or not isinstance(email_to, str) or '@' not in email_to:
                         error_msg = f"Correo inválido o faltante para Yaku '{row.get('Nombre Yaku', 'Desconocido')}' (Índice: {index}). Saltando."
                         st.warning(error_msg)
                         errors.append(error_msg)
                         error_count += 1
                         # Actualizar progreso
                         progress = (index + 1) / total_to_process
                         progress_bar.progress(min(1.0, progress))
                         continue # Saltar al siguiente

                     # Construir Asunto y Cuerpo
                     subject = f"¡Asignación Yachay Wasi: Conoce a tu Ruru {row.get('Nombre Ruru', 'N/A')}!"
                     try:
                         html_body = get_yaku_email_body(row)
                         # Enviar Correo
                         send_single_email(email_to, subject, html_body)
                         success_count += 1
                         # Pequeño delay
                         time.sleep(delay_seconds)
                     except Exception as e:
                         error_count += 1
                         error_detail = f"Error enviando a {email_to} (Yaku: {row.get('Nombre Yaku', 'N/A')}): {str(e)}"
                         errors.append(error_detail)
                         st.warning(error_detail) # Mostrar advertencia en UI

                     # Actualizar progreso
                     progress = (index + 1) / total_to_process
                     progress_bar.progress(min(1.0, progress))


                 progress_bar.empty() # Limpiar barra de progreso
                 st.success(f"Proceso finalizado: {success_count} correos enviados exitosamente.")
                 if error_count > 0:
                      st.error(f"{error_count} correos fallaron o fueron saltados.")
                      with st.expander("Ver errores detallados"):
                           st.json({"errors": errors}) # Mostrar errores en formato json para legibilidad
            else:
                 st.warning("No hay correos seleccionados para enviar.")
    else:
        st.info("Carga el archivo de resultados del match para habilitar el envío.") 