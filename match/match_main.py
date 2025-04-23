"""
Página principal del módulo de Match en Streamlit.

Permite al usuario cargar los archivos de Yakus y Rurus procesados,
ejecutar el algoritmo de asignación y visualizar/descargar los resultados.
"""
import streamlit as st
import pandas as pd

# Importar funciones de los submódulos (se añadirán después)
from .core.data_loader import load_yaku_data, load_ruru_data, filter_rurus_by_area
from .core.scorer import create_scores_list
from .core.assignment import find_best_matches
# from .ui.match_display import display_match_results
# from .utils.output_generator import generate_output_files

# --- MODIFICADO: Descomentar e importar ui y utils ---
from .ui.match_display import display_match_results # Ahora lo usaremos
from .utils.output_generator import (
    format_assigned_output,
    format_unassigned_output,
    generate_excel_output,
    UNASSIGNED_YAKU_COLS,
    UNASSIGNED_RURU_COLS
)

# --- Inicializar variables en estado de sesión ---
if 'yakus_loaded' not in st.session_state:
    st.session_state.yakus_loaded = None
if 'rurus_loaded' not in st.session_state:
    st.session_state.rurus_loaded = None
if 'rurus_filtered' not in st.session_state:
    st.session_state.rurus_filtered = None
if 'current_match_area' not in st.session_state:
    st.session_state.current_match_area = None
if 'scores_list' not in st.session_state:
    st.session_state.scores_list = None
if 'assigned_df' not in st.session_state:
    st.session_state.assigned_df = None
if 'unassigned_yakus' not in st.session_state:
    st.session_state.unassigned_yakus = None
if 'unassigned_rurus' not in st.session_state:
    st.session_state.unassigned_rurus = None

# --- Añadir estado para DFs formateados ---
if 'assigned_formatted_df' not in st.session_state:
    st.session_state.assigned_formatted_df = None
if 'unassigned_yakus_formatted_df' not in st.session_state:
    st.session_state.unassigned_yakus_formatted_df = None
if 'unassigned_rurus_formatted_df' not in st.session_state:
    st.session_state.unassigned_rurus_formatted_df = None
if 'excel_output' not in st.session_state:
    st.session_state.excel_output = None

def match_page():
    """Función principal que renderiza la página de Match."""
    st.title(" Módulo de Asignación (Match)")
    st.write("""
    Carga los datos preprocesados de Yakus (por área) y Rurus,
    ejecuta el algoritmo de asignación 1-a-1 y muestra los resultados.
    """)

    # --- Sección de Carga de Archivos ---
    st.header("1. Cargar Datos")
    area_options = ["Asesoría a Colegios Nacionales", "Arte & Cultura", "Bienestar Psicológico"]
    selected_area = st.selectbox("Selecciona el Área para el Match:", area_options, key="area_selector")

    # Reiniciar estado si cambia el área
    if st.session_state.current_match_area != selected_area:
        st.session_state.yakus_loaded = None
        st.session_state.rurus_filtered = None
        st.session_state.current_match_area = selected_area
        st.rerun() # Forzar recarga para limpiar uploaders si es necesario

    # File Uploaders
    uploaded_yaku_file = st.file_uploader(f"Cargar archivo Excel de Yakus ({selected_area})", type=["xlsx", "xls"], key=f"yaku_upload_{selected_area}")
    uploaded_ruru_file = st.file_uploader("Cargar archivo Excel de Rurus (Preprocesado)", type=["xlsx", "xls"], key="ruru_upload")

    # Procesar archivos cargados
    if uploaded_yaku_file and st.session_state.yakus_loaded is None:
        st.session_state.yakus_loaded = load_yaku_data(uploaded_yaku_file, selected_area)
        if st.session_state.yakus_loaded is not None:
            st.info(f"{len(st.session_state.yakus_loaded)} Yakus cargados para {selected_area}.")
            # Mostrar vista previa opcional
            with st.expander("Vista previa Yakus"):
                 st.dataframe(st.session_state.yakus_loaded.head())


    # Cargar Rurus solo una vez, ya que son los mismos para todas las áreas
    if uploaded_ruru_file and st.session_state.rurus_loaded is None:
        st.session_state.rurus_loaded = load_ruru_data(uploaded_ruru_file)
        if st.session_state.rurus_loaded is not None:
            st.info(f"{len(st.session_state.rurus_loaded)} Rurus totales cargados.")
            # Mostrar vista previa opcional
            with st.expander("Vista previa Rurus (Todos)"):
                 st.dataframe(st.session_state.rurus_loaded.head())

    # Filtrar Rurus si ambos DFs están cargados y el filtro no se ha hecho para el área actual
    if st.session_state.yakus_loaded is not None and st.session_state.rurus_loaded is not None and st.session_state.rurus_filtered is None:
         st.session_state.rurus_filtered = filter_rurus_by_area(st.session_state.rurus_loaded, selected_area)
         if st.session_state.rurus_filtered is not None:
              with st.expander(f"Vista previa Rurus Filtrados ({selected_area})"):
                   st.dataframe(st.session_state.rurus_filtered.head())


    # --- Sección de Ejecución del Match ---
    st.header("2. Ejecutar Match")

    # Habilitar botón solo si los datos están listos para el área seleccionada
    match_ready = st.session_state.yakus_loaded is not None and st.session_state.rurus_filtered is not None

    if st.button(f"Realizar Match para {selected_area}", disabled=not match_ready):
        if match_ready:
            # Reiniciar resultados previos
            st.session_state.scores_list = None
            st.session_state.assigned_df = None
            st.session_state.unassigned_yakus = None
            st.session_state.unassigned_rurus = None
            st.session_state.assigned_formatted_df = None # Limpiar formateados también
            st.session_state.unassigned_yakus_formatted_df = None
            st.session_state.unassigned_rurus_formatted_df = None
            st.session_state.excel_output = None

            with st.spinner(f"Procesando match completo para {selected_area}..."):
                yakus_to_match = st.session_state.yakus_loaded
                rurus_to_match = st.session_state.rurus_filtered

                # -- Puntuación --
                st.write("Calculando compatibilidad...")
                scores = create_scores_list(yakus_to_match, rurus_to_match, selected_area)
                st.session_state.scores_list = scores
                if not scores:
                     st.warning("No se encontraron pares compatibles.")
                     st.stop()

                # -- Asignación --
                st.write("Realizando asignación final...")
                assigned_df, unassigned_yakus_ids, unassigned_rurus_ids = find_best_matches(
                    yakus_to_match, rurus_to_match, scores
                )
                st.session_state.assigned_df = assigned_df
                st.session_state.unassigned_yakus = unassigned_yakus_ids
                st.session_state.unassigned_rurus = unassigned_rurus_ids

                # --- Formatear Resultados para Output ---
                st.write("Formateando resultados...")
                st.session_state.assigned_formatted_df = format_assigned_output(
                    assigned_df,
                    yakus_to_match,
                    rurus_to_match
                )
                st.session_state.unassigned_yakus_formatted_df = format_unassigned_output(
                    unassigned_yakus_ids,
                    yakus_to_match,
                    'yaku_id',
                    UNASSIGNED_YAKU_COLS
                )
                st.session_state.unassigned_rurus_formatted_df = format_unassigned_output(
                    unassigned_rurus_ids,
                    rurus_to_match,
                    'ID del estudiante:',
                    UNASSIGNED_RURU_COLS
                )

                # --- Generar Excel en Memoria ---
                st.write("Generando archivo Excel...")
                st.session_state.excel_output = generate_excel_output(
                    st.session_state.assigned_formatted_df,
                    st.session_state.unassigned_yakus_formatted_df,
                    st.session_state.unassigned_rurus_formatted_df
                )

                st.success(f"¡Proceso de Match para {selected_area} completado!")

        else:
             st.warning("Por favor, carga ambos archivos (Yakus y Rurus) para el área seleccionada antes de ejecutar el match.")


    # --- Sección de Resultados (Usa la función de UI) ---
    st.header("3. Resultados")
    if st.session_state.assigned_formatted_df is not None:
        # --- LLAMADA A LA FUNCIÓN DE DISPLAY ---
        display_match_results(
            assigned_df=st.session_state.assigned_formatted_df,
            unassigned_yakus_df=st.session_state.unassigned_yakus_formatted_df,
            unassigned_rurus_df=st.session_state.unassigned_rurus_formatted_df
        )
        # --- FIN LLAMADA ---
    else:
        st.info("Ejecuta el match para ver los resultados de la asignación.")


    # --- Sección de Descarga ---
    st.header("4. Descargar Resultados")
    if st.session_state.excel_output:
        excel_bytes = st.session_state.excel_output.getvalue()
        st.download_button(
            label="Descargar Resultados en Excel",
            data=excel_bytes,
            file_name=f"Resultados_Match_{st.session_state.current_match_area.replace(' ', '_')}.xlsx", # Usar área del estado
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_button"
        )
    else:
        st.info("Ejecuta el match para generar el archivo de descarga.")

# Llamada a la función principal de la página
# No es necesaria aquí si se llama desde app.py
# match_page() 