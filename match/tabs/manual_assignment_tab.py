"""
Pestaña para realizar asignaciones manuales Yaku-Ruru.

Permite cargar un archivo de resultados del match, seleccionar un Yaku
y un Ruru de las listas de no asignados, y moverlos a la lista de asignados.
"""
import streamlit as st
import pandas as pd
from io import BytesIO

# Reutilizar función de generación de Excel y limpieza de números
# Asumimos que están en match.utils o las copiamos/importamos
# from ..utils.output_generator import generate_excel_output, clean_str_number
# Temporalmente, copiamos clean_str_number aquí por simplicidad
def clean_str_number(val):
    """Limpia números leídos de Excel, convirtiéndolos a string limpio."""
    if pd.isna(val) or val == '': return ''
    try: cleaned_val = str(int(float(str(val))))
    except (ValueError, TypeError): cleaned_val = str(val).strip()
    if cleaned_val.endswith('.0'): cleaned_val = cleaned_val[:-2]
    return cleaned_val

# Importar generate_excel_output (asegúrate que la ruta relativa sea correcta)
try:
     from ..utils.output_generator import generate_excel_output
except ImportError:
     st.error("Error al importar 'generate_excel_output'. Asegúrate que la estructura de archivos es correcta.")
     # Fallback por si la importación falla
     def generate_excel_output(df1, df2, df3): return None


# Columnas esperadas/necesarias
ASSIGNED_COLS_EXPECTED = ['ID Ruru', 'ID Yaku', 'Nombre Ruru', 'Nombre Yaku', 'Area', 'Asignatura/Taller Asignado', 'Grado Original Ruru', 'Score Match'] # Mínimo
YAKU_NA_ID_COL = 'yaku_id' # ID Yaku en hoja Yakus No Asignados
RURU_NA_ID_COL = 'ID del estudiante:' # ID Ruru en hoja Rurus No Asignados


def load_results_for_manual(uploaded_file):
    """Carga las 3 hojas del archivo de resultados."""
    data = {}
    sheet_names = ["Asignaciones", "Yakus No Asignados", "Rurus No Asignados"]
    try:
        xls = pd.ExcelFile(uploaded_file)
        valid = True
        for sheet in sheet_names:
            if sheet in xls.sheet_names:
                data[sheet] = pd.read_excel(xls, sheet_name=sheet)
                # Asegurar IDs como string
                if sheet == "Asignaciones" and 'ID Ruru' in data[sheet].columns: data[sheet]['ID Ruru'] = data[sheet]['ID Ruru'].astype(str)
                if sheet == "Asignaciones" and 'ID Yaku' in data[sheet].columns: data[sheet]['ID Yaku'] = data[sheet]['ID Yaku'].astype(str)
                if sheet == "Yakus No Asignados" and YAKU_NA_ID_COL in data[sheet].columns: data[sheet][YAKU_NA_ID_COL] = data[sheet][YAKU_NA_ID_COL].astype(str)
                if sheet == "Rurus No Asignados" and RURU_NA_ID_COL in data[sheet].columns: data[sheet][RURU_NA_ID_COL] = data[sheet][RURU_NA_ID_COL].astype(str)
            else:
                st.error(f"Error: Falta la hoja requerida '{sheet}' en el archivo de resultados.")
                valid = False
                data[sheet] = pd.DataFrame() # Evitar errores posteriores
        return data if valid else None
    except Exception as e:
        st.error(f"Error al leer el archivo de resultados: {e}")
        return None

def load_rurus_source(uploaded_file):
    """Carga Rurus Transformados para obtener datos completos."""
    try:
        df = pd.read_excel(uploaded_file)
        # Validar columnas mínimas para construir la fila de asignación
        required = [RURU_NA_ID_COL, 'nombre', 'apellido', 'area', 'grado_original', 'celular', 'celular_asesoria', 'DNI', 'quechua', 'asignatura_opcion1', 'taller_opcion1'] # Ejemplo
        missing = [col for col in required if col not in df.columns]
        if missing:
            st.warning(f"Advertencia: Faltan columnas en Rurus Transformados que podrían ser útiles: {missing}")
        df[RURU_NA_ID_COL] = df[RURU_NA_ID_COL].astype(str)
        return df
    except Exception as e:
        st.error(f"Error al leer Rurus Transformados: {e}")
        return None


# --- Pestaña Streamlit ---
def manual_assignment_tab():
    st.header("Asignación Manual Yaku-Ruru")
    st.write("Selecciona un Yaku y un Ruru de las listas de 'No Asignados' para moverlos a la hoja de 'Asignaciones'.")

    # Estado de sesión
    if 'manual_results_data' not in st.session_state: st.session_state.manual_results_data = None
    if 'manual_rurus_source' not in st.session_state: st.session_state.manual_rurus_source = None
    if 'manual_area' not in st.session_state: st.session_state.manual_area = None
    if 'manual_updated_excel' not in st.session_state: st.session_state.manual_updated_excel = None


    # Selector de Área
    area_options = ["Asesoría a Colegios Nacionales", "Arte & Cultura", "Bienestar Psicológico"]
    selected_area = st.selectbox("Selecciona el Área del archivo de resultados:", area_options, key="manual_area_selector")

    if st.session_state.manual_area != selected_area:
        # Resetear si cambia el área
        st.session_state.manual_results_data = None
        st.session_state.manual_updated_excel = None
        # No reseteamos rurus_source si es el mismo archivo completo
        st.session_state.manual_area = selected_area

    # Uploaders
    uploaded_results = st.file_uploader(f"1. Cargar Resultados del Match ({selected_area})", type=["xlsx", "xls"], key=f"manual_results_upload_{selected_area}")
    uploaded_rurus_source = st.file_uploader("2. Cargar Rurus Transformados (Fuente de Datos)", type=["xlsx", "xls"], key="manual_rurus_source_upload")

    # Cargar datos
    if uploaded_results and st.session_state.manual_results_data is None:
        loaded_data = load_results_for_manual(uploaded_results)
        if loaded_data:
            # Hacer copias para evitar modificar el objeto original directamente al principio
            st.session_state.manual_results_data = {
                "Asignaciones": loaded_data["Asignaciones"].copy(),
                "Yakus No Asignados": loaded_data["Yakus No Asignados"].copy(),
                "Rurus No Asignados": loaded_data["Rurus No Asignados"].copy()
            }
        else:
             st.session_state.manual_results_data = None # Falló la carga

    if uploaded_rurus_source and st.session_state.manual_rurus_source is None:
        st.session_state.manual_rurus_source = load_rurus_source(uploaded_rurus_source)


    # Lógica de asignación manual
    if st.session_state.manual_results_data is not None and st.session_state.manual_rurus_source is not None:
        # --- LEER DIRECTAMENTE DEL ESTADO DE SESIÓN ---
        # Ya no usamos una variable 'data' separada, trabajamos sobre el estado
        df_asignaciones = st.session_state.manual_results_data["Asignaciones"]
        df_yakus_na = st.session_state.manual_results_data["Yakus No Asignados"]
        df_rurus_na = st.session_state.manual_results_data["Rurus No Asignados"]

        rurus_source_df = st.session_state.manual_rurus_source

        st.markdown("---")
        st.subheader("Seleccionar para Asignar")

        # Validar que las hojas de no asignados no estén vacías y tengan IDs
        # Usamos las copias del estado de sesión
        yakus_na_valid = not df_yakus_na.empty and YAKU_NA_ID_COL in df_yakus_na.columns
        rurus_na_valid = not df_rurus_na.empty and RURU_NA_ID_COL in df_rurus_na.columns

        selected_yaku_id = None
        selected_ruru_id = None

        # Crear copias para evitar SettingWithCopyWarning al añadir 'display_label'
        df_yakus_na_display = df_yakus_na.copy()
        df_rurus_na_display = df_rurus_na.copy()

        if yakus_na_valid:
             # Crear etiquetas legibles para el selector de Yakus en la copia
             df_yakus_na_display['display_label'] = df_yakus_na_display.apply(
                 lambda row: f"{row.get('nombre', 'N/A')} ({row[YAKU_NA_ID_COL]})", axis=1
             )
             yaku_options = df_yakus_na_display['display_label'].tolist()
             selected_yaku_label = st.selectbox("Yaku No Asignado:", ["Seleccionar..."] + yaku_options, key="manual_yaku_select")
             if selected_yaku_label != "Seleccionar...":
                 # Extraer ID del label usando la copia
                 selected_yaku_id = df_yakus_na_display[df_yakus_na_display['display_label'] == selected_yaku_label][YAKU_NA_ID_COL].iloc[0]
        else:
             st.warning("No hay Yakus en la lista de 'No Asignados' o falta la columna ID.")

        if rurus_na_valid:
             # Crear etiquetas legibles para el selector de Rurus en la copia
             df_rurus_na_display['display_label'] = df_rurus_na_display.apply(
                 lambda row: f"{row.get('nombre', '')} {row.get('apellido', '')} ({row[RURU_NA_ID_COL]})".strip(), axis=1
             )
             ruru_options = df_rurus_na_display['display_label'].tolist()
             selected_ruru_label = st.selectbox("Ruru No Asignado:", ["Seleccionar..."] + ruru_options, key="manual_ruru_select")
             if selected_ruru_label != "Seleccionar...":
                  # Extraer ID del label usando la copia
                  selected_ruru_id = df_rurus_na_display[df_rurus_na_display['display_label'] == selected_ruru_label][RURU_NA_ID_COL].iloc[0]
        else:
             st.warning("No hay Rurus en la lista de 'No Asignados' o falta la columna ID.")


        # Botón para realizar la asignación
        if selected_yaku_id and selected_ruru_id:
            if st.button("Confirmar Asignación Manual", key="confirm_manual_assign"):
                with st.spinner("Actualizando asignaciones..."):
                    # --- Lógica de Actualización ---
                    # 1. Obtener datos completos del Yaku y Ruru seleccionados
                    #    Leemos de los DataFrames actuales en el estado de sesión
                    yaku_data = df_yakus_na[df_yakus_na[YAKU_NA_ID_COL] == selected_yaku_id].iloc[0]
                    ruru_data_source = rurus_source_df[rurus_source_df[RURU_NA_ID_COL] == selected_ruru_id]

                    # Verificar si se encontró el Ruru en la fuente de datos
                    if ruru_data_source.empty:
                        st.error(f"Error: No se encontró el Ruru con ID {selected_ruru_id} en el archivo 'Rurus Transformados'. No se puede completar la asignación.")
                        st.stop() # Detener ejecución si el Ruru no está en la fuente

                    ruru_data = ruru_data_source.iloc[0]

                    # 2. Construir la nueva fila para df_asignaciones
                    #    Necesita coincidir con las columnas de 'format_assigned_output'
                    #    Ajustar este mapeo según las columnas REALES
                    new_assignment_row = {
                        'ID Ruru': selected_ruru_id,
                        'ID Yaku': selected_yaku_id,
                        'Nombre Ruru': f"{ruru_data.get('nombre', '')} {ruru_data.get('apellido', '')}".strip(),
                        'Nombre Yaku': yaku_data.get('nombre', ''),
                        'Area': yaku_data.get('area', selected_area), # Tomar área del Yaku o la seleccionada
                        'Asignatura/Taller Asignado': yaku_data.get('asignatura') or yaku_data.get('taller', 'N/A'),
                        'Grado Original Ruru': ruru_data.get('grado_original', ''),
                        'Score Match': 'MANUAL', # Indicar que fue manual
                        'Celular Apoderado Ruru': clean_str_number(ruru_data.get('celular')),
                        'Celular Asesoria Ruru': clean_str_number(ruru_data.get('celular_asesoria')),
                        'DNI Ruru': clean_str_number(ruru_data.get('DNI')),
                        'DNI Yaku': clean_str_number(yaku_data.get('dni')),
                        'Correo Yaku': yaku_data.get('correo', ''),
                        'Celular Yaku': clean_str_number(yaku_data.get('celular')),
                        'Quechua Yaku': yaku_data.get('quechua', ''),
                        'Quechua Ruru': ruru_data.get('quechua', ''),
                        # --- AÑADIR HORARIOS ---
                        # Asume que las columnas fuente son 'horario_dia' (ej. 'horario_lunes')
                        # y las columnas destino son 'Horario Dia Yaku/Ruru' (ej. 'Horario Lunes Yaku')
                        # Ajusta los nombres si son diferentes en tus archivos.
                        'Horario Lunes Yaku': yaku_data.get('horario_lunes', ''),
                        'Horario Martes Yaku': yaku_data.get('horario_martes', ''),
                        'Horario Miercoles Yaku': yaku_data.get('horario_miercoles', ''),
                        'Horario Jueves Yaku': yaku_data.get('horario_jueves', ''),
                        'Horario Viernes Yaku': yaku_data.get('horario_viernes', ''),
                        'Horario Sabado Yaku': yaku_data.get('horario_sabado', ''),
                        'Horario Domingo Yaku': yaku_data.get('horario_domingo', ''),
                        'Horario Lunes Ruru': ruru_data.get('horario_lunes', ''),
                        'Horario Martes Ruru': ruru_data.get('horario_martes', ''),
                        'Horario Miercoles Ruru': ruru_data.get('horario_miercoles', ''),
                        'Horario Jueves Ruru': ruru_data.get('horario_jueves', ''),
                        'Horario Viernes Ruru': ruru_data.get('horario_viernes', ''),
                        'Horario Sabado Ruru': ruru_data.get('horario_sabado', ''),
                        'Horario Domingo Ruru': ruru_data.get('horario_domingo', ''),
                    }

                    # Convertir a DataFrame y asegurar columnas
                    new_row_df = pd.DataFrame([new_assignment_row])
                    # Lee las columnas del DataFrame de asignaciones *actual* en el estado
                    target_assign_cols = st.session_state.manual_results_data["Asignaciones"].columns
                    # Si el DataFrame de asignaciones está vacío inicialmente, usa las columnas esperadas (o las que tenga new_row_df)
                    if target_assign_cols.empty:
                         # Podrías definir aquí un set mínimo si es necesario, o usar las columnas de la fila nueva
                         target_assign_cols = new_row_df.columns
                         # Opcionalmente, si quieres asegurar un set mínimo incluso si la hoja inicial está vacía:
                         # target_assign_cols = pd.Index(ASSIGNED_COLS_EXPECTED + ['Horario Lunes Yaku', ... , 'Horario Domingo Ruru'])


                    # Asegurar que tenga las mismas columnas y en el mismo orden que el DF de destino
                    # Las columnas de horario se añadirán solo si ya existen en la hoja "Asignaciones" cargada.
                    new_row_df = new_row_df.reindex(columns=target_assign_cols, fill_value='')

                    # 3. Crear DataFrames ACTUALIZADOS
                    # Asegurar que ambos dataframes (el existente y la nueva fila) tengan las mismas columnas antes de concatenar
                    df_asignaciones_current = st.session_state.manual_results_data["Asignaciones"]
                    # Alinear columnas del df existente por si acaso (aunque reindex en new_row_df debería bastar)
                    df_asignaciones_current = df_asignaciones_current.reindex(columns=target_assign_cols, fill_value='')

                    updated_asignaciones = pd.concat([df_asignaciones_current, new_row_df], ignore_index=True)
                    updated_yakus_na = df_yakus_na[df_yakus_na[YAKU_NA_ID_COL] != selected_yaku_id].copy()
                    updated_rurus_na = df_rurus_na[df_rurus_na[RURU_NA_ID_COL] != selected_ruru_id].copy()

                    # --- ACTUALIZAR EL ESTADO DE SESIÓN ---
                    st.session_state.manual_results_data["Asignaciones"] = updated_asignaciones
                    st.session_state.manual_results_data["Yakus No Asignados"] = updated_yakus_na
                    st.session_state.manual_results_data["Rurus No Asignados"] = updated_rurus_na

                    # 4. Generar nuevo Excel DESDE EL ESTADO ACTUALIZADO
                    excel_buffer = generate_excel_output(
                        updated_asignaciones,
                        updated_yakus_na,
                        updated_rurus_na
                    )

                    if excel_buffer:
                        # Guardar el buffer del excel generado en el estado para la descarga
                        st.session_state.manual_updated_excel = excel_buffer
                        st.success(f"¡Asignación manual completada! Yaku {selected_yaku_id} asignado a Ruru {selected_ruru_id}.")
                        # Forzar recarga de la UI para refrescar los selectores
                        st.rerun()
                    else:
                        st.error("Error al generar el archivo Excel actualizado.")


        # Botón de descarga (si se generó el archivo)
        # Leer el buffer guardado en el estado de sesión
        if st.session_state.get('manual_updated_excel'):
            st.markdown("---")
            st.download_button(
                label=f"Descargar Resultados Actualizados ({selected_area})",
                data=st.session_state.manual_updated_excel.getvalue(),
                file_name=f"Resultados_Match_{selected_area.replace(' ', '_')}_ManualUpdate.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_manual_update"
            )
    else:
        st.info("Carga ambos archivos (Resultados del área y Rurus Transformados) para habilitar la asignación manual.") 