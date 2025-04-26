"""
Pestaña para actualizar los resultados del match usando un archivo
Excel externo que contiene las asignaciones finales deseadas.
Especialmente útil para ajustes masivos o áreas específicas como Arte y Cultura.
"""
import streamlit as st
import pandas as pd
from io import BytesIO

# Reutilizar funciones (asegúrate de que las rutas sean correctas)
try:
    from ..utils.output_generator import generate_excel_output, clean_str_number
except ImportError:
    # Simplemente define fallbacks o lanza el error para depurar
    # st.error("Error al importar utilidades. Verifica la estructura de archivos.") <-- ELIMINAR ESTA LÍNEA
    print("ADVERTENCIA: No se pudieron importar las utilidades desde ..utils.output_generator. Usando fallbacks.") # Opcional: print para consola
    # Fallbacks temporales (si quieres que la app intente funcionar sin las utils)
    def clean_str_number(val):
        if pd.isna(val) or val == '': return ''
        try: cleaned_val = str(int(float(str(val))))
        except (ValueError, TypeError): cleaned_val = str(val).strip()
        if cleaned_val.endswith('.0'): cleaned_val = cleaned_val[:-2]
        return cleaned_val
    def generate_excel_output(df1, df2, df3):
        print("Error: La función generate_excel_output no está disponible.")
        return None # O retorna un error/None


# Columnas esperadas/necesarias
FINAL_ASSIGN_RURU_COL = 'CÓDIGO DEL RURU'
FINAL_ASSIGN_YAKU_COL = 'CÓDIGO DEL YAKU'
YAKU_ID_COLS = ['ID Yaku', 'yaku_id'] # Posibles nombres para ID de Yaku en fuentes
RURU_ID_COLS = ['ID Ruru', 'ID del estudiante:'] # Posibles nombres para ID de Ruru en fuentes


def load_current_results(uploaded_file):
    """Carga las 3 hojas del archivo de resultados actual."""
    data = {}
    sheet_names = ["Asignaciones", "Yakus No Asignados", "Rurus No Asignados"]
    all_sheets_present = True
    try:
        xls = pd.ExcelFile(uploaded_file)
        for sheet in sheet_names:
            if sheet in xls.sheet_names:
                data[sheet] = pd.read_excel(xls, sheet_name=sheet)
            else:
                st.error(f"Error: Falta la hoja requerida '{sheet}' en el archivo de resultados actuales.")
                data[sheet] = pd.DataFrame() # Crear df vacío para evitar errores posteriores
                all_sheets_present = False
        return data if all_sheets_present else None
    except Exception as e:
        st.error(f"Error al leer el archivo de resultados actuales: {e}")
        return None

def load_transformed_rurus(uploaded_file):
    """Carga Rurus Transformados, fuente principal de datos de Rurus."""
    try:
        df = pd.read_excel(uploaded_file)
        # Intentar identificar la columna ID del Ruru
        ruru_id_col = None
        for col_name in RURU_ID_COLS:
             if col_name in df.columns:
                 ruru_id_col = col_name
                 break
        if not ruru_id_col:
            st.error(f"Error: No se encontró una columna de ID de Ruru ({', '.join(RURU_ID_COLS)}) en Rurus Transformados.")
            return None, None
        df[ruru_id_col] = df[ruru_id_col].apply(clean_str_number)
        df = df.astype(str) # Convertir todo a string por si acaso
        # Validar columnas mínimas útiles (puedes añadir más)
        required = [ruru_id_col, 'nombre', 'apellido', 'area', 'grado_original']
        missing = [col for col in required if col not in df.columns]
        if missing:
            st.warning(f"Advertencia: Faltan columnas en Rurus Transformados: {missing}")
        return df, ruru_id_col
    except Exception as e:
        st.error(f"Error al leer Rurus Transformados: {e}")
        return None, None

def load_final_assignments(uploaded_file):
    """Carga el archivo Excel con las asignaciones finales."""
    try:
        df = pd.read_excel(uploaded_file)
        # Validar columnas
        if FINAL_ASSIGN_RURU_COL not in df.columns or FINAL_ASSIGN_YAKU_COL not in df.columns:
            st.error(f"Error: El archivo de asignaciones finales debe contener las columnas '{FINAL_ASSIGN_RURU_COL}' y '{FINAL_ASSIGN_YAKU_COL}'.")
            return None
        # Limpiar IDs
        df[FINAL_ASSIGN_RURU_COL] = df[FINAL_ASSIGN_RURU_COL].apply(clean_str_number)
        df[FINAL_ASSIGN_YAKU_COL] = df[FINAL_ASSIGN_YAKU_COL].apply(clean_str_number)
        # Eliminar filas donde falte algún ID
        df = df.dropna(subset=[FINAL_ASSIGN_RURU_COL, FINAL_ASSIGN_YAKU_COL])
        # Eliminar filas con IDs vacíos después de limpiar
        df = df[(df[FINAL_ASSIGN_RURU_COL] != '') & (df[FINAL_ASSIGN_YAKU_COL] != '')]

        st.success(f"Se cargaron {len(df)} asignaciones finales del archivo.")
        return df[[FINAL_ASSIGN_RURU_COL, FINAL_ASSIGN_YAKU_COL]] # Devolver solo las columnas relevantes
    except Exception as e:
        st.error(f"Error al leer el archivo de asignaciones finales: {e}")
        return None

def get_consolidated_yakus(current_results_data):
    """Crea un DataFrame consolidado de todos los Yakus del área."""
    df_assigned = current_results_data.get("Asignaciones", pd.DataFrame())
    df_na = current_results_data.get("Yakus No Asignados", pd.DataFrame())

    yakus_all = {} # Usar dict para evitar duplicados por ID

    # Identificar columna ID Yaku en No Asignados
    yaku_na_id_col = None
    for col in YAKU_ID_COLS:
        if col in df_na.columns:
            yaku_na_id_col = col
            break

    # Identificar columna ID Yaku en Asignados
    yaku_as_id_col = None
    for col in YAKU_ID_COLS:
        if col in df_assigned.columns:
            yaku_as_id_col = col
            break

    # Procesar Yakus No Asignados
    if yaku_na_id_col and not df_na.empty:
        df_na[yaku_na_id_col] = df_na[yaku_na_id_col].apply(clean_str_number)
        for _, row in df_na.iterrows():
            yaku_id = row[yaku_na_id_col]
            if yaku_id and yaku_id not in yakus_all:
                yakus_all[yaku_id] = row.to_dict()
                yakus_all[yaku_id]['origen'] = 'Yakus No Asignados' # Marcar origen por si acaso
                yakus_all[yaku_id]['ID'] = yaku_id # Asegurar un campo ID estándar

    # Procesar Yakus Asignados (obtener detalles del Yaku, no del Ruru)
    if yaku_as_id_col and not df_assigned.empty:
         df_assigned[yaku_as_id_col] = df_assigned[yaku_as_id_col].apply(clean_str_number)
         for _, row in df_assigned.iterrows():
            yaku_id = row[yaku_as_id_col]
            if yaku_id and yaku_id not in yakus_all:
                # Extraer columnas relevantes del Yaku de la fila de asignación
                yaku_data = { 'ID': yaku_id }
                # Intentar obtener datos relevantes del Yaku (ajusta nombres si es necesario)
                yaku_data['nombre'] = row.get('Nombre Yaku')
                yaku_data['area'] = row.get('Area')
                yaku_data['asignatura'] = row.get('Asignatura/Taller Asignado') # O como se llame
                yaku_data['dni'] = row.get('DNI Yaku')
                yaku_data['correo'] = row.get('Correo Yaku')
                yaku_data['celular'] = row.get('Celular Yaku')
                yaku_data['quechua'] = row.get('Quechua Yaku')
                for dia in ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']:
                    col_name = f'Horario {dia} Yaku'
                    if col_name in row:
                        yaku_data[f'horario_{dia.lower()}'] = row[col_name]
                yaku_data['origen'] = 'Asignaciones'
                yakus_all[yaku_id] = yaku_data

    if not yakus_all:
        st.warning("No se encontraron Yakus en las hojas 'Asignaciones' o 'Yakus No Asignados' del archivo de resultados actual.")
        return pd.DataFrame(), None

    # Convertir a DataFrame
    consolidated_df = pd.DataFrame.from_dict(yakus_all, orient='index')
    # Identificar la columna ID final (debería ser 'ID')
    final_yaku_id_col = 'ID'
    if final_yaku_id_col not in consolidated_df.columns:
         # Fallback si 'ID' no se creó
         if yaku_na_id_col in consolidated_df.columns: final_yaku_id_col = yaku_na_id_col
         elif yaku_as_id_col in consolidated_df.columns: final_yaku_id_col = yaku_as_id_col
         else:
             st.error("No se pudo determinar una columna ID única para los Yakus consolidados.")
             return pd.DataFrame(), None

    consolidated_df[final_yaku_id_col] = consolidated_df[final_yaku_id_col].astype(str) # Asegurar string
    consolidated_df = consolidated_df.astype(str) # Convertir todo a string
    return consolidated_df, final_yaku_id_col


# --- Pestaña Streamlit ---
def final_update_tab():
    st.header("Actualizar Match desde Archivo Final (Arte y Cultura)")
    st.write("Carga el archivo de resultados actual, Rurus Transformados y el Excel con las asignaciones finales (Col D: Ruru ID, Col G: Yaku ID) para generar el estado final.")

    # Estado de sesión específico para esta pestaña
    if 'finalup_current_results' not in st.session_state: st.session_state.finalup_current_results = None
    if 'finalup_rurus_transformed' not in st.session_state: st.session_state.finalup_rurus_transformed = None
    if 'finalup_rurus_id_col' not in st.session_state: st.session_state.finalup_rurus_id_col = None
    if 'finalup_final_assign' not in st.session_state: st.session_state.finalup_final_assign = None
    if 'finalup_processed_output' not in st.session_state: st.session_state.finalup_processed_output = None
    if 'finalup_yakus_consolidated' not in st.session_state: st.session_state.finalup_yakus_consolidated = None
    if 'finalup_yakus_id_col' not in st.session_state: st.session_state.finalup_yakus_id_col = None


    # Uploaders
    uploaded_current = st.file_uploader("1. Cargar Resultados Actuales (Excel con 3 hojas)", type=["xlsx", "xls"], key="finalup_current_upload")
    uploaded_rurus = st.file_uploader("2. Cargar Rurus Transformados (Fuente Datos Ruru)", type=["xlsx", "xls"], key="finalup_rurus_upload")
    uploaded_final = st.file_uploader("3. Cargar Asignaciones Finales (Excel con Col D y G)", type=["xlsx", "xls"], key="finalup_final_upload")

    # Cargar datos y guardar en estado de sesión
    if uploaded_current:
        if st.session_state.finalup_current_results is None: # Cargar solo una vez
            st.session_state.finalup_current_results = load_current_results(uploaded_current)
            # Si se cargaron resultados, consolidar Yakus
            if st.session_state.finalup_current_results:
                 st.session_state.finalup_yakus_consolidated, st.session_state.finalup_yakus_id_col = get_consolidated_yakus(st.session_state.finalup_current_results)

    if uploaded_rurus:
        if st.session_state.finalup_rurus_transformed is None: # Cargar solo una vez
            # Cargar el dataframe completo y la columna ID
            rurus_df_completo, ruru_id_col_nombre = load_transformed_rurus(uploaded_rurus)
            if rurus_df_completo is not None:
                 # --- NUEVO: Filtrar por Área ---
                 area_para_filtrar = "Arte & Cultura"
                 columna_area = 'area'

                 if columna_area not in rurus_df_completo.columns:
                      st.error(f"Error: No se encontró la columna de área '{columna_area}' en Rurus Transformados. No se puede filtrar.")
                      st.session_state.finalup_rurus_transformed = None
                      st.session_state.finalup_rurus_id_col = None
                 else:
                      # Filtrar
                      rurus_df_filtrado = rurus_df_completo[rurus_df_completo[columna_area] == area_para_filtrar].copy()
                      st.success(f"Se cargó y filtró Rurus Transformados por '{area_para_filtrar}'. Se encontraron {len(rurus_df_filtrado)} Rurus para esta área.")

                      # Guardar el DF *filtrado* y el nombre de la columna ID en el estado
                      st.session_state.finalup_rurus_transformed = rurus_df_filtrado
                      st.session_state.finalup_rurus_id_col = ruru_id_col_nombre
            else:
                # Si load_transformed_rurus falló
                st.session_state.finalup_rurus_transformed = None
                st.session_state.finalup_rurus_id_col = None

    if uploaded_final:
        if st.session_state.finalup_final_assign is None: # Cargar solo una vez
            st.session_state.finalup_final_assign = load_final_assignments(uploaded_final)


    # Botón para procesar
    if st.session_state.finalup_current_results and \
       st.session_state.finalup_rurus_transformed is not None and \
       st.session_state.finalup_final_assign is not None and \
       st.session_state.finalup_yakus_consolidated is not None:

        if st.button("Generar Resultados Finales", key="finalup_process_button"):
            with st.spinner("Procesando asignaciones finales para Arte y Cultura..."):
                final_assignments = st.session_state.finalup_final_assign
                # --- Usar el DataFrame de Rurus YA FILTRADO ---
                rurus_transformed_df_filtered = st.session_state.finalup_rurus_transformed
                rurus_id_col = st.session_state.finalup_rurus_id_col

                # --- Revisar duplicados DESPUÉS de filtrar ---
                # Ahora, un duplicado significaría que el mismo Ruru está listado dos veces PARA ARTE Y CULTURA, lo cual sí sería un problema de datos.
                if rurus_transformed_df_filtered[rurus_id_col].duplicated().any():
                     st.warning(f"Advertencia: Se encontraron IDs duplicados en la columna '{rurus_id_col}' del archivo Rurus Transformados *DENTRO DEL ÁREA 'Arte y Cultura'*. Esto puede indicar un problema en los datos fuente. Se usará la primera ocurrencia de cada ID.")
                     # Aplicar drop_duplicates aquí es más seguro ahora que estamos dentro del área
                     rurus_db = rurus_transformed_df_filtered.drop_duplicates(subset=[rurus_id_col], keep='first').set_index(rurus_id_col)
                else:
                     # Si no hay duplicados dentro del área, simplemente settear el índice
                     rurus_db = rurus_transformed_df_filtered.set_index(rurus_id_col)


                yakus_consolidated_df = st.session_state.finalup_yakus_consolidated
                yakus_id_col = st.session_state.finalup_yakus_id_col
                # (La lógica para duplicados de Yakus se mantiene por si acaso)
                if yakus_consolidated_df[yakus_id_col].duplicated().any():
                     st.warning(f"Advertencia: Se encontraron IDs duplicados para Yakus ('{yakus_id_col}'). Se usará la primera ocurrencia.")
                     yakus_db = yakus_consolidated_df.drop_duplicates(subset=[yakus_id_col], keep='first').set_index(yakus_id_col)
                else:
                     yakus_db = yakus_consolidated_df.set_index(yakus_id_col)


                current_results = st.session_state.finalup_current_results
                new_assignments_list = []
                processed_ruru_ids = set()
                processed_yaku_ids = set()
                errors = []
                # Ya no necesitamos la lista 'warnings' para duplicados esperados entre áreas

                # 1. Construir la nueva hoja de Asignaciones
                for idx, row in final_assignments.iterrows():
                    ruru_id = row[FINAL_ASSIGN_RURU_COL]
                    yaku_id = row[FINAL_ASSIGN_YAKU_COL]

                    # Validar existencia en los índices (que ahora son filtrados por área para Rurus)
                    if ruru_id not in rurus_db.index:
                        errors.append(f"ID Ruru '{ruru_id}' (Fila {idx+2} archivo final) no encontrado en Rurus Transformados para 'Arte y Cultura'.")
                        continue
                    if yaku_id not in yakus_db.index:
                        errors.append(f"ID Yaku '{yaku_id}' (Fila {idx+2} archivo final) no encontrado en Yakus consolidados.")
                        continue

                    # --- OBTENER DATOS (YA NO DEBERÍA HABER AMBIGÜEDAD POR ÁREA) ---
                    try:
                        # .loc ahora debería devolver una Serie única porque filtramos por área y manejamos duplicados *dentro* del área.
                        ruru_data = rurus_db.loc[ruru_id]
                        yaku_data = yakus_db.loc[yaku_id] # Asume ID Yaku único
                        # Si aún hubiera duplicados en Yakus, necesitaríamos .iloc[0]
                        if isinstance(yaku_data, pd.DataFrame):
                             yaku_data = yaku_data.iloc[0]

                    except Exception as e:
                         errors.append(f"Error inesperado al buscar Ruru '{ruru_id}' o Yaku '{yaku_id}' (después de filtrar por área): {e}")
                         continue
                    # --- FIN OBTENER DATOS ---

                    # Construir fila (el código aquí es el mismo que antes)
                    assignment_row = {
                        'ID Ruru': ruru_id,
                        'ID Yaku': yaku_id,
                        'Nombre Ruru': f"{ruru_data.get('nombre', '')} {ruru_data.get('apellido', '')}".strip(),
                        'Nombre Yaku': yaku_data.get('nombre', ''),
                        'Area': yaku_data.get('area', 'Arte y Cultura'), # Forzar o tomar del Yaku
                        'Asignatura/Taller Asignado': yaku_data.get('asignatura') or yaku_data.get('taller', 'N/A'),
                        'Grado Original Ruru': ruru_data.get('grado_original', ''),
                        'Score Match': 'FINAL',
                        'Celular Apoderado Ruru': clean_str_number(ruru_data.get('celular')),
                        'Celular Asesoria Ruru': clean_str_number(ruru_data.get('celular_asesoria')),
                        'DNI Ruru': clean_str_number(ruru_data.get('DNI')),
                        'DNI Yaku': clean_str_number(yaku_data.get('dni')),
                        'Correo Yaku': yaku_data.get('correo', ''),
                        'Celular Yaku': clean_str_number(yaku_data.get('celular')),
                        'Quechua Yaku': yaku_data.get('quechua', ''),
                        'Quechua Ruru': ruru_data.get('quechua', ''),
                    }
                    for dia in ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']:
                         yaku_col = f'horario_{dia.lower()}'
                         ruru_col = f'horario_{dia.lower()}'
                         assignment_row[f'Horario {dia} Yaku'] = yaku_data.get(yaku_col, '')
                         assignment_row[f'Horario {dia} Ruru'] = ruru_data.get(ruru_col, '')

                    new_assignments_list.append(assignment_row)
                    processed_ruru_ids.add(ruru_id)
                    processed_yaku_ids.add(yaku_id)

                # Mostrar errores (ya no mostramos warnings de duplicados entre áreas)
                if errors:
                    st.error("Se encontraron errores al procesar el archivo final:")
                    for error in errors:
                        st.error(f"- {error}")
                    st.warning("Las filas con errores fueron omitidas.")

                # 2. Determinar No Asignados Finales
                #    all_ruru_ids ahora se basa en el índice de rurus_db, que ya está filtrado por área.
                all_ruru_ids_area = set(rurus_db.index)
                all_yaku_ids = set(yakus_db.index) # Yakus son consolidados, asumimos que pertenecen a esta área o son generales.

                final_rurus_na_ids = all_ruru_ids_area - processed_ruru_ids
                final_yakus_na_ids = all_yaku_ids - processed_yaku_ids

                # 3. Construir Hojas No Asignados Finales
                # Usar Rurus Transformados *filtrados* para datos de Rurus NA
                # Usamos el DataFrame filtrado original (antes del set_index)
                rurus_na_final_df = st.session_state.finalup_rurus_transformed[
                    st.session_state.finalup_rurus_transformed[st.session_state.finalup_rurus_id_col].isin(final_rurus_na_ids)
                ].copy()
                # Renombrar columnas si es necesario para coincidir con hoja "Rurus No Asignados" original
                # Ejemplo: renombrar 'ID del estudiante:' a 'ID Ruru' si es necesario
                # rurus_na_final_df.rename(columns={'ID del estudiante:': 'ID Ruru'}, inplace=True)
                # Asegúrate de que tenga las columnas esperadas por generate_excel_output

                # Usar Yakus Consolidados para datos de Yakus NA
                yakus_na_final_df = st.session_state.finalup_yakus_consolidated[
                    st.session_state.finalup_yakus_consolidated[st.session_state.finalup_yakus_id_col].isin(final_yakus_na_ids)
                ].copy()
                # Renombrar columnas si es necesario (ej. 'ID' a 'yaku_id')
                # yakus_na_final_df.rename(columns={'ID': 'yaku_id'}, inplace=True)


                # 4. Generar Excel Final
                st.session_state.finalup_processed_output = generate_excel_output(
                    pd.DataFrame(new_assignments_list),
                    yakus_na_final_df,
                    rurus_na_final_df
                )

                if st.session_state.finalup_processed_output:
                    st.success(f"Procesamiento completado. Se generaron {len(new_assignments_list)} asignaciones finales.")
                    st.info(f"{len(yakus_na_final_df)} Yakus y {len(rurus_na_final_df)} Rurus quedaron como No Asignados.")
                else:
                    st.error("Error al generar el archivo Excel de salida.")

    # Botón de descarga
    if st.session_state.get('finalup_processed_output'):
        st.markdown("---")
        st.download_button(
            label="Descargar Resultados Finales Actualizados",
            data=st.session_state.finalup_processed_output.getvalue(),
            file_name="Resultados_Match_ArteCultura_FinalUpdate.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_final_update"
        )

    # Limpiar estado si cambian los archivos cargados (opcional, pero bueno para evitar confusiones)
    # Podrías añadir lógica para resetear el estado si un nuevo archivo es cargado en un uploader existente.
    # Ejemplo simple: si uploaded_current cambia, resetear todo lo demás
    # if uploaded_current and st.session_state.get('finalup_last_uploaded_current') != uploaded_current.name:
    #     st.session_state.finalup_current_results = None
    #     st.session_state.finalup_yakus_consolidated = None
    #     # ... resetear otros estados ...
    #     st.session_state.finalup_last_uploaded_current = uploaded_current.name
    #     st.rerun() # Recargar para aplicar el reseteo 