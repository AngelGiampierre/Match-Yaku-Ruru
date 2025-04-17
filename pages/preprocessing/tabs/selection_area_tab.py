import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import sys
import io
from pages.preprocessing.components.file_handlers import export_dataframe
from datetime import datetime

# Importamos las funciones de utilidad
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from utils.data_processors import (
    standardize_dni, filter_by_area_and_selection
)
from utils import load_data, save_data

def selection_area_tab():
    """
    Tab para filtrar y seleccionar por área.
    Permite cargar un archivo con una lista de selección y filtrar los datos por área.
    """
    st.header("Selección por Área")
    st.subheader("Filtra los datos por área utilizando listas de selección")
    
    # Opciones para cargar datos
    data_source = st.radio(
        "Selecciona la fuente de datos:",
        options=["Usar datos procesados previamente", "Cargar nuevo archivo de Yakus"],
        horizontal=True
    )
    
    yakus_data = None
    
    if data_source == "Usar datos procesados previamente":
        # Cargar datos existentes
        yakus_data = load_data("yakus_processed.pkl") or load_data("yakus_initial.pkl")
        
        if yakus_data is None:
            st.warning("⚠️ No se encontraron datos de Yakus. Por favor, carga y procesa los datos primero o selecciona 'Cargar nuevo archivo de Yakus'.")
            return
        
        # Mostrar información básica de los datos cargados
        st.success(f"✅ Datos de Yakus cargados: {yakus_data.shape[0]} filas x {yakus_data.shape[1]} columnas")
    
    else:
        # Opción para cargar directamente un archivo nuevo
        st.write("### Cargar archivo de Yakus")
        uploaded_file = st.file_uploader(
            "Carga el archivo con datos de Yakus (.xlsx, .csv)",
            type=["xlsx", "csv"],
            key="yakus_direct_upload"
        )
        
        if uploaded_file is not None:
            try:
                # Determinar el tipo de archivo y leer los datos
                file_extension = uploaded_file.name.split(".")[-1].lower()
                
                if file_extension == "csv":
                    yakus_data = pd.read_csv(uploaded_file)
                elif file_extension == "xlsx":
                    yakus_data = pd.read_excel(uploaded_file)
                
                # Mostrar información básica del archivo
                st.success(f"✅ Archivo cargado correctamente: {uploaded_file.name}")
                st.write(f"Dimensiones del DataFrame: {yakus_data.shape[0]} filas x {yakus_data.shape[1]} columnas")
                
                # Vista previa de los datos
                with st.expander("Vista previa de los datos cargados", expanded=True):
                    st.dataframe(yakus_data.head())
                
                # Guardar en la memoria temporal para uso posterior
                save_data(yakus_data, "yakus_direct_upload.pkl")
                
            except Exception as e:
                st.error(f"Error al procesar el archivo: {str(e)}")
                return
    
    # Si no hay datos disponibles, detener la ejecución
    if yakus_data is None:
        st.info("Por favor, carga un archivo o selecciona datos existentes para continuar.")
        return
        
    # Determinar la columna de área
    area_cols = [col for col in yakus_data.columns if 'area' in col.lower() or 'área' in col.lower()]
    
    if not area_cols:
        st.warning("⚠️ No se encontró una columna de área en los datos. Por favor, asegúrate de que los datos contengan información sobre el área.")
        return
    
    area_col = area_cols[0]  # Usar la primera columna de área encontrada
    
    # Mostrar áreas disponibles
    areas_disponibles = yakus_data[area_col].dropna().unique()
    st.write("### Áreas disponibles")
    for area in sorted(areas_disponibles):
        count = len(yakus_data[yakus_data[area_col] == area])
        st.write(f"- **{area}**: {count} Yakus")
    
    # Selección de área
    st.write("### Seleccionar área para filtrar")
    area_seleccionada = st.selectbox(
        "Selecciona un área:",
        options=["Todas las áreas"] + sorted(areas_disponibles.tolist())
    )
    
    # Cargar archivo de selección (opcional)
    st.write("### Cargar lista de selección (opcional)")
    st.info("Puedes cargar un archivo con DNIs de Yakus seleccionados para filtrar aún más los resultados.")
    
    seleccion_file = st.file_uploader(
        "Carga archivo con DNIs seleccionados (.xlsx, .csv)",
        type=["xlsx", "csv"],
        key="seleccion_file"
    )
    
    dni_seleccionados = []
    if seleccion_file is not None:
        try:
            # Leer archivo de selección
            file_extension = seleccion_file.name.split(".")[-1].lower()
            if file_extension == "csv":
                seleccion_df = pd.read_csv(seleccion_file)
            elif file_extension == "xlsx":
                seleccion_df = pd.read_excel(seleccion_file)
            
            # Identificar columna de DNI
            dni_cols = [col for col in seleccion_df.columns if any(term in col.lower() for term in 
                                            ['dni', 'documento', 'document', 'identidad', 'identity', 'id'])]
            
            if not dni_cols:
                st.warning("⚠️ No se encontró una columna de DNI en el archivo de selección.")
            else:
                dni_col = dni_cols[0]  # Usar la primera columna de DNI encontrada
                dni_seleccionados = seleccion_df[dni_col].dropna().astype(str).tolist()
                st.success(f"✅ Lista de selección cargada: {len(dni_seleccionados)} DNIs")
                
                # Mostrar algunos DNIs de ejemplo
                if dni_seleccionados:
                    st.write("Primeros DNIs en la lista:")
                    for dni in dni_seleccionados[:5]:
                        st.write(f"- {dni}")
                    if len(dni_seleccionados) > 5:
                        st.write(f"- ... y {len(dni_seleccionados) - 5} más")
        except Exception as e:
            st.error(f"Error al procesar el archivo de selección: {str(e)}")
    
    # Filtrar datos según selección
    if st.button("Aplicar filtro", key="apply_filter_button"):
        with st.spinner("Filtrando datos..."):
            # Determinar la columna de DNI
            dni_data_cols = [col for col in yakus_data.columns if any(term in col.lower() for term in 
                                            ['dni', 'documento', 'document', 'identidad', 'identity'])]
            
            if not dni_data_cols:
                st.warning("⚠️ No se encontró una columna de DNI en los datos.")
                return
            
            dni_data_col = dni_data_cols[0]  # Usar la primera columna de DNI encontrada
            
            # Aplicar filtro por área
            if area_seleccionada != "Todas las áreas":
                filtered_data = yakus_data[yakus_data[area_col] == area_seleccionada].copy()
            else:
                filtered_data = yakus_data.copy()
            
            # Aplicar filtro adicional por DNI si hay selección
            if dni_seleccionados:
                # Convertir los DNI del DataFrame a strings para comparar
                filtered_data[dni_data_col] = filtered_data[dni_data_col].astype(str)
                
                # Filtrar por DNIs seleccionados
                filtered_data = filtered_data[filtered_data[dni_data_col].isin(dni_seleccionados)]
                
                # Verificar DNIs no encontrados
                dnis_encontrados = filtered_data[dni_data_col].tolist()
                dnis_no_encontrados = [dni for dni in dni_seleccionados if dni not in dnis_encontrados]
                
                if dnis_no_encontrados:
                    st.warning(f"⚠️ {len(dnis_no_encontrados)} DNIs de la selección no se encontraron en el área seleccionada.")
                    
                    # Opción para buscar en todas las áreas
                    if area_seleccionada != "Todas las áreas" and st.button("Buscar DNIs en todas las áreas"):
                        yakus_data[dni_data_col] = yakus_data[dni_data_col].astype(str)
                        dnis_en_otras_areas = yakus_data[yakus_data[dni_data_col].isin(dnis_no_encontrados)]
                        
                        if not dnis_en_otras_areas.empty:
                            st.success(f"✅ Se encontraron {len(dnis_en_otras_areas)} DNIs en otras áreas.")
                            st.dataframe(dnis_en_otras_areas[[dni_data_col, area_col]])
                        else:
                            st.error("❌ No se encontraron los DNIs en ninguna área.")
            
            # Guardar datos filtrados
            if not filtered_data.empty:
                file_prefix = f"yakus_area_{area_seleccionada.replace(' ', '_').lower()}" if area_seleccionada != "Todas las áreas" else "yakus_todas_areas"
                if dni_seleccionados:
                    file_prefix += "_seleccionados"
                
                save_data(filtered_data, f"{file_prefix}.pkl")
                st.success(f"✅ Datos filtrados guardados como {file_prefix}.pkl")
                
                # Mostrar resultados
                st.subheader("Resultados del filtrado")
                st.write(f"- Número de filas filtradas: {filtered_data.shape[0]}")
                
                # Mostrar datos filtrados
                st.write("Vista previa de los datos filtrados:")
                st.dataframe(filtered_data.head(10))
                
                # Descargar datos filtrados
                col1, col2 = st.columns(2)
                
                with col1:
                    # Opción para descargar como Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        filtered_data.to_excel(writer, index=False, sheet_name='Datos Filtrados')
                    excel_data = output.getvalue()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="📥 Descargar como Excel",
                        data=excel_data,
                        file_name=f"{file_prefix}_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                with col2:
                    # Opción para descargar como CSV
                    csv = filtered_data.to_csv(index=False)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="📥 Descargar como CSV",
                        data=csv,
                        file_name=f"{file_prefix}_{timestamp}.csv",
                        mime="text/csv"
                    )
            else:
                st.warning("⚠️ No se encontraron datos que cumplan con los criterios de filtrado.")
    
    # Funcionalidad de búsqueda
    st.write("### Búsqueda específica")
    
    # Determinar la columna de DNI
    dni_data_cols = [col for col in yakus_data.columns if any(term in col.lower() for term in 
                                        ['dni', 'documento', 'document', 'identidad', 'identity'])]
    
    if dni_data_cols:
        dni_data_col = dni_data_cols[0]  # Usar la primera columna de DNI encontrada
        
        # Campo de búsqueda
        dni_busqueda = st.text_input("Buscar por DNI:")
        
        if dni_busqueda:
            yakus_data[dni_data_col] = yakus_data[dni_data_col].astype(str)
            resultados = yakus_data[yakus_data[dni_data_col].str.contains(dni_busqueda, regex=False)]
            
            if not resultados.empty:
                st.success(f"✅ Se encontraron {len(resultados)} resultados.")
                st.dataframe(resultados)
            else:
                st.error(f"❌ No se encontró ningún registro con DNI que contenga '{dni_busqueda}'.") 