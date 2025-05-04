import streamlit as st
import pandas as pd

# --- Funciones Auxiliares (si son necesarias, como limpieza de DNI) ---
def clean_dni_series(series):
    """Limpia una serie de Pandas que contiene DNIs."""
    # Asegurar que sea string, quitar espacios y '.0' si viene de número
    return series.astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

# --- Pestaña Streamlit ---
def yaku_analysis_tab():
    st.header("📊 Análisis de Universidades de Yakus Asignados")
    st.write("Analiza de qué universidades provienen los Yakus asignados en un área específica, comparando el archivo de resultados del match con un archivo global de Yakus.")

    # Estado de sesión específico para esta pestaña
    if 'analysis_area' not in st.session_state: st.session_state.analysis_area = "Bienestar Psicológico"
    if 'analysis_global_df' not in st.session_state: st.session_state.analysis_global_df = None
    if 'analysis_match_df' not in st.session_state: st.session_state.analysis_match_df = None
    if 'analysis_results' not in st.session_state: st.session_state.analysis_results = None
    if 'analysis_dnis_not_found' not in st.session_state: st.session_state.analysis_dnis_not_found = []

    # --- Selección de Área ---
    area_options = ["Bienestar Psicológico", "Asesoría a Colegios Nacionales", "Arte & Cultura"]
    selected_area = st.selectbox(
        "1. Selecciona el Área a Analizar:",
        area_options,
        index=area_options.index(st.session_state.analysis_area),
        key="analysis_area_selector"
    )

    # Resetear si cambia el área
    if st.session_state.analysis_area != selected_area:
        st.session_state.analysis_area = selected_area
        st.session_state.analysis_global_df = None
        st.session_state.analysis_match_df = None
        st.session_state.analysis_results = None
        st.session_state.analysis_dnis_not_found = []
        st.rerun()

    st.markdown("---")

    # --- Carga de Archivos ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("2. Cargar Archivo Global")
        uploaded_global = st.file_uploader(
            "Archivo Excel con lista maestra de Yakus (incluye 'DNI o Pasaporte' y 'Universidades')",
            type=["xlsx", "xls"],
            key="analysis_global_upload"
        )
        if uploaded_global and st.session_state.analysis_global_df is None:
            try:
                # Leer todo el archivo por si los datos están en diferentes hojas (asumimos la primera por defecto)
                df_global = pd.read_excel(uploaded_global)
                # Validar columnas esenciales
                if "DNI o Pasaporte" in df_global.columns and "Universidades" in df_global.columns:
                    st.session_state.analysis_global_df = df_global
                    st.success("Archivo Global cargado.")
                    # Limpiar resultados si se carga nuevo archivo global
                    st.session_state.analysis_results = None
                    st.session_state.analysis_dnis_not_found = []
                else:
                    st.error("El archivo global debe contener las columnas 'DNI o Pasaporte' y 'Universidades'.")
                    st.session_state.analysis_global_df = None
            except Exception as e:
                st.error(f"Error al leer el archivo global: {e}")
                st.session_state.analysis_global_df = None

    with col2:
        st.subheader(f"3. Cargar Resultados Match")
        uploaded_match = st.file_uploader(
            f"Archivo Excel con los resultados del Match para '{selected_area}'",
            type=["xlsx", "xls"],
            key="analysis_match_upload"
        )
        if uploaded_match and st.session_state.analysis_match_df is None:
            try:
                # Leer específicamente la hoja de Asignaciones
                df_match = pd.read_excel(uploaded_match, sheet_name="Asignaciones")
                # Validar columna esencial
                if "DNI Yaku" in df_match.columns:
                    # Filtrar por área DENTRO de la hoja (si existe columna Area) - Doble seguridad
                    if 'Area' in df_match.columns:
                        df_match_area = df_match[df_match['Area'] == selected_area].copy()
                        if df_match_area.empty:
                             st.warning(f"No se encontraron asignaciones para '{selected_area}' en este archivo.")
                             # Guardamos un DF vacío para evitar errores posteriores
                             st.session_state.analysis_match_df = pd.DataFrame(columns=["DNI Yaku"])
                        else:
                            st.session_state.analysis_match_df = df_match_area
                            st.success(f"Resultados del Match para '{selected_area}' cargados.")
                    else:
                        # Si no hay columna Area, asumimos que el archivo ya es del área correcta
                         st.session_state.analysis_match_df = df_match
                         st.success(f"Resultados del Match cargados (se asume que son de '{selected_area}').")

                    # Limpiar resultados si se carga nuevo archivo de match
                    st.session_state.analysis_results = None
                    st.session_state.analysis_dnis_not_found = []

                else:
                    st.error("La hoja 'Asignaciones' del archivo de resultados debe contener la columna 'DNI Yaku'.")
                    st.session_state.analysis_match_df = None
            except Exception as e:
                st.error(f"Error al leer el archivo de resultados del Match: {e}")
                st.session_state.analysis_match_df = None

    st.markdown("---")

    # --- Lógica de Procesamiento y Visualización (a implementar en el siguiente paso) ---
    if st.session_state.analysis_global_df is not None and st.session_state.analysis_match_df is not None:
        st.subheader("4. Resultados del Análisis")

        # Evitar recalcular si ya se hizo
        if st.session_state.analysis_results is None:
            with st.spinner("Realizando análisis..."):
                try:
                    df_global = st.session_state.analysis_global_df
                    df_match = st.session_state.analysis_match_df

                    # --- Paso 3: Lógica de Carga y Procesamiento ---
                    # Limpiar DNIs
                    dnis_asignados_limpios = clean_dni_series(df_match['DNI Yaku']).unique()
                    df_global['DNI Limpio'] = clean_dni_series(df_global['DNI o Pasaporte'])

                    # Crear mapa DNI -> Universidad (manejando duplicados, tomando el primero)
                    # Asegurarse de que los DNIs limpios sean únicos en el mapeo
                    df_global_unique_dni = df_global.drop_duplicates(subset=['DNI Limpio'], keep='first')
                    dni_uni_map = df_global_unique_dni.set_index('DNI Limpio')['Universidades'].to_dict()

                    # Contar universidades y registrar no encontrados
                    conteo_universidades = {}
                    dnis_no_encontrados = []

                    if len(dnis_asignados_limpios) > 0: # Solo procesar si hay DNIs asignados
                        for dni in dnis_asignados_limpios:
                            if dni in dni_uni_map:
                                universidad = dni_uni_map[dni]
                                # Tratar NaNs o vacíos en Universidad como 'Desconocida' o similar
                                if pd.isna(universidad) or str(universidad).strip() == '':
                                    universidad = 'Universidad Desconocida/Vacía'
                                conteo_universidades[universidad] = conteo_universidades.get(universidad, 0) + 1
                            else:
                                dnis_no_encontrados.append(dni)

                        # Calcular resultados
                        if conteo_universidades:
                            df_results = pd.DataFrame(list(conteo_universidades.items()), columns=['Universidad', 'Cantidad'])
                            total_encontrados = df_results['Cantidad'].sum()
                            if total_encontrados > 0:
                                df_results['Porcentaje'] = (df_results['Cantidad'] / total_encontrados * 100).round(2)
                            else:
                                df_results['Porcentaje'] = 0.0
                            df_results = df_results.sort_values(by='Cantidad', ascending=False).reset_index(drop=True)
                            st.session_state.analysis_results = df_results
                        else:
                             st.session_state.analysis_results = pd.DataFrame(columns=['Universidad', 'Cantidad', 'Porcentaje']) # DF vacío

                        st.session_state.analysis_dnis_not_found = dnis_no_encontrados
                    else:
                         # No había DNIs asignados en el archivo de match
                         st.session_state.analysis_results = pd.DataFrame(columns=['Universidad', 'Cantidad', 'Porcentaje'])
                         st.session_state.analysis_dnis_not_found = []
                         st.info(f"No se encontraron DNIs de Yakus asignados en el archivo de resultados para '{selected_area}'.")


                except Exception as e:
                    st.error(f"Error durante el análisis: {e}")
                    st.session_state.analysis_results = None
                    st.session_state.analysis_dnis_not_found = []

        # Mostrar resultados si existen
        if st.session_state.analysis_results is not None:
            st.dataframe(st.session_state.analysis_results)

            # Mostrar DNIs no encontrados si los hay
            if st.session_state.analysis_dnis_not_found:
                st.warning("⚠️ Se encontraron DNIs de Yakus asignados que no están en el archivo global:")
                # Usar st.expander para no ocupar mucho espacio si son muchos
                with st.expander(f"Ver {len(st.session_state.analysis_dnis_not_found)} DNI(s) no encontrados"):
                    st.code('\n'.join(st.session_state.analysis_dnis_not_found))
            elif not st.session_state.analysis_results.empty : # Si hubo resultados pero no hubo no encontrados
                st.success("✅ ¡Todos los DNIs de Yakus asignados fueron encontrados en el archivo global!")

        elif st.session_state.analysis_results is not None and st.session_state.analysis_results.empty and not st.session_state.analysis_dnis_not_found :
             st.info(f"No se encontraron datos de universidad para los Yakus asignados en el archivo global o no había Yakus asignados.")


    elif not uploaded_global or not uploaded_match:
        st.info("Carga ambos archivos Excel (Global y Resultados del Match) para iniciar el análisis.") 