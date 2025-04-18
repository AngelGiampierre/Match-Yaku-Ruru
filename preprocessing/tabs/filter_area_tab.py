"""
Tab para filtrar datos por área y lista de selección.

Este tab permite cargar dos archivos: uno con datos generales y otro con una lista
de selección, para filtrar los datos por área y por IDs específicos.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple

# Importamos componentes de UI
from ..ui.file_uploaders import upload_excel_file, show_download_buttons
from ..ui.selectors import select_id_column
from ..ui.displays import preview_dataframe, show_column_statistics

# Importamos funciones de filtrado
from ..data.filters import (
    identify_area_column,
    get_unique_areas,
    filter_by_area,
    identify_id_column,
    load_and_parse_selection_list,
    filter_by_ids,
    combine_filters
)

# Importamos utilidades
from ..utils.file_io import save_temp_file
from ..utils import save_data, load_data


def filter_area_tab():
    """
    Tab para filtrar datos por área y lista de selección.
    """
    st.header("Filtrado por Área")
    st.write("""
    Esta sección te permite cargar un archivo principal y uno con lista de selección (opcional),
    para filtrar los datos por área y por IDs específicos como DNI o correo electrónico.
    """)
    
    # Inicializar variables
    main_df = None
    main_file_name = None
    selection_df = None
    selection_file_name = None
    filtered_df = None
    
    # Paso 1: Cargar archivo principal
    st.subheader("Paso 1: Cargar archivo principal")
    st.write("Carga el archivo principal con todos los datos:")
    
    main_df, main_file_name, main_success = upload_excel_file(
        key="main_file_upload",
        label="Cargar archivo principal (Excel o CSV)",
        help_text="Este archivo contiene todos los datos que quieres filtrar"
    )
    
    if main_success and main_df is not None:
        # Identificar columna de área
        area_column = identify_area_column(main_df)
        
        if area_column:
            st.success(f"✅ Se detectó automáticamente la columna de área: '{area_column}'")
        else:
            st.warning("⚠️ No se detectó automáticamente una columna de área")
            # Permitir selección manual
            area_column = st.selectbox(
                "Selecciona la columna de área:",
                options=main_df.columns.tolist(),
                key="area_column_select"
            )
        
        # Obtener áreas únicas
        areas = ["Todas las áreas"] + get_unique_areas(main_df, area_column)
        
        # Seleccionar área
        selected_area = st.selectbox(
            "Selecciona un área:",
            options=areas,
            key="area_select"
        )
        
        # Paso 2: Cargar archivo de selección (opcional)
        st.subheader("Paso 2: Cargar lista de selección (opcional)")
        st.write("""
        Opcionalmente, puedes cargar un archivo con una lista de selección. 
        Este archivo debe contener una columna con identificadores (DNI o correo) 
        que se usarán para filtrar los datos principales.
        """)
        
        # Radio button para elegir el tipo de identificador
        id_type = st.radio(
            "Tipo de identificador en la lista de selección:",
            options=["DNI/Documento", "Correo electrónico", "Nombre"],
            horizontal=True,
            key="id_type"
        )
        
        # Cargar archivo de selección
        selection_df, selection_file_name, selection_success = upload_excel_file(
            key="selection_file_upload",
            label=f"Cargar archivo con lista de {id_type}",
            help_text=f"Este archivo debe contener una columna con {id_type}"
        )
        
        id_column = None
        id_list = []
        
        if selection_success and selection_df is not None:
            # Identificar columna de ID en el archivo de selección
            if id_type == "DNI/Documento":
                id_sel_column = identify_id_column(selection_df, "dni")
            elif id_type == "Correo electrónico":
                id_sel_column = identify_id_column(selection_df, "email")
            else:  # Nombre
                id_sel_column = identify_id_column(selection_df, "nombre")
            
            if id_sel_column:
                st.success(f"✅ Se detectó automáticamente la columna de {id_type}: '{id_sel_column}'")
            else:
                st.warning(f"⚠️ No se detectó automáticamente una columna de {id_type}")
                # Permitir selección manual
                id_sel_column = st.selectbox(
                    f"Selecciona la columna de {id_type} en el archivo de selección:",
                    options=selection_df.columns.tolist(),
                    key="id_sel_column_select"
                )
            
            # Cargar lista de IDs desde el archivo de selección
            id_list = load_and_parse_selection_list(selection_df, id_sel_column)
            
            if id_list:
                st.success(f"✅ Se cargaron {len(id_list)} identificadores de la lista de selección")
                
                # Mostrar algunos ejemplos
                st.write("Ejemplos de identificadores cargados:")
                for i, id_val in enumerate(id_list[:5]):
                    st.write(f"- {id_val}")
                if len(id_list) > 5:
                    st.write(f"- ... y {len(id_list) - 5} más")
            else:
                st.warning("⚠️ No se encontraron identificadores válidos en la lista de selección")
        
        # Identificar columna de ID en el archivo principal
        if id_type == "DNI/Documento":
            id_column = identify_id_column(main_df, "dni")
        elif id_type == "Correo electrónico":
            id_column = identify_id_column(main_df, "email")
        else:  # Nombre
            id_column = identify_id_column(main_df, "nombre")
        
        if id_column:
            st.success(f"✅ Se detectó automáticamente la columna de {id_type} en el archivo principal: '{id_column}'")
        else:
            st.warning(f"⚠️ No se detectó automáticamente una columna de {id_type} en el archivo principal")
            # Permitir selección manual
            id_column = st.selectbox(
                f"Selecciona la columna de {id_type} en el archivo principal:",
                options=main_df.columns.tolist(),
                key="id_main_column_select"
            )
        
        # Paso 3: Aplicar filtros
        st.subheader("Paso 3: Aplicar filtros")
        
        # Opciones de filtrado
        filter_options = []
        
        if selected_area != "Todas las áreas":
            filter_options.append(f"Área: {selected_area}")
        
        if id_list:
            filter_options.append(f"Lista de {id_type} ({len(id_list)} identificadores)")
        
        if filter_options:
            st.write("Se aplicarán los siguientes filtros:")
            for option in filter_options:
                st.write(f"- {option}")
        else:
            st.info("No hay filtros seleccionados. Se mostrarán todos los datos.")
        
        # Botón para aplicar filtros
        if st.button("Aplicar filtros", key="apply_filters_button"):
            # Aplicar filtros
            filtered_df, not_found_ids = combine_filters(
                main_df,
                area_column,
                selected_area,
                id_column,
                id_list
            )
            
            # Guardar resultados en el estado de sesión
            save_data(filtered_df, "filtered_data")
            save_data(not_found_ids, "not_found_ids")
            
            # Mostrar resultados
            if not filtered_df.empty:
                st.success(f"✅ Filtrado completado. Se encontraron {len(filtered_df)} registros.")
                
                # Mostrar vista previa
                preview_dataframe(
                    filtered_df,
                    rows=10,
                    title="Vista previa de datos filtrados",
                    expanded=True
                )
                
                # Mostrar IDs no encontrados
                if not_found_ids:
                    st.warning(f"⚠️ {len(not_found_ids)} identificadores de la lista no se encontraron")
                    
                    # Mostrar algunos ejemplos
                    st.write("Ejemplos de identificadores no encontrados:")
                    for i, id_val in enumerate(not_found_ids[:5]):
                        st.write(f"- {id_val}")
                    if len(not_found_ids) > 5:
                        st.write(f"- ... y {len(not_found_ids) - 5} más")
                
                # Paso 4: Guardar resultados
                st.subheader("Paso 4: Guardar resultados")
                
                # Opción para guardar temporalmente
                if st.button("Guardar datos filtrados temporalmente", key="save_temp_filtered"):
                    # Generar nombre base
                    base_name = "datos_filtrados"
                    if main_file_name:
                        base_name = main_file_name.split('.')[0]  # Quitar extensión
                    
                    if selected_area != "Todas las áreas":
                        area_suffix = selected_area.lower().replace(' ', '_')
                        base_name += f"_area_{area_suffix}"
                    
                    if id_list:
                        base_name += "_seleccion"
                    
                    # Guardar temporalmente
                    temp_file_path = save_temp_file(filtered_df, base_name)
                    if temp_file_path:
                        st.success(f"✅ Datos guardados temporalmente para uso en otros tabs")
                
                # Botones para descargar
                st.write("#### Descargar datos filtrados")
                
                # Generar nombre base para el archivo
                base_filename = "datos_filtrados"
                if main_file_name:
                    base_name = main_file_name.split('.')[0]  # Quitar extensión
                    base_filename = base_name
                
                if selected_area != "Todas las áreas":
                    area_suffix = selected_area.lower().replace(' ', '_')
                    base_filename += f"_area_{area_suffix}"
                
                if id_list:
                    base_filename += "_seleccion"
                
                # Mostrar botones de descarga
                show_download_buttons(filtered_df, base_filename)
            else:
                st.warning("⚠️ No se encontraron registros que cumplan con los criterios de filtrado")
        
        # Cargar datos filtrados del estado de sesión (si están disponibles)
        elif load_data("filtered_data") is not None:
            filtered_df = load_data("filtered_data")
            not_found_ids = load_data("not_found_ids") or []
            
            st.info("ℹ️ Mostrando resultados del último filtrado")
            
            if not filtered_df.empty:
                st.success(f"✅ Filtrado completado. Se encontraron {len(filtered_df)} registros.")
                
                # Mostrar vista previa
                preview_dataframe(
                    filtered_df,
                    rows=10,
                    title="Vista previa de datos filtrados",
                    expanded=True
                )
                
                # Mostrar botones de descarga
                base_filename = "datos_filtrados"
                if main_file_name:
                    base_name = main_file_name.split('.')[0]
                    base_filename = base_name
                
                if selected_area != "Todas las áreas":
                    area_suffix = selected_area.lower().replace(' ', '_')
                    base_filename += f"_area_{area_suffix}"
                
                if id_list:
                    base_filename += "_seleccion"
                
                show_download_buttons(filtered_df, base_filename)
    
    # Mostrar instrucciones si no hay archivo cargado
    elif not main_success:
        st.info("👆 Carga un archivo principal para comenzar el proceso de filtrado.")


if __name__ == "__main__":
    # Esto permite probar el tab individualmente
    filter_area_tab() 