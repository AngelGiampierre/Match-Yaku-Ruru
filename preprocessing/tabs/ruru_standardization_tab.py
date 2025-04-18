"""
Pestaña para estandarización de datos de Rurus.

Este módulo permite cargar un archivo de Rurus, renombrar y estandarizar
sus columnas, y exportar el resultado.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any

# Importamos componentes de UI
from ..ui.file_uploaders import upload_excel_file, show_download_buttons
from ..ui.displays import preview_dataframe, show_column_statistics

# Importamos utilidades
from ..utils.file_io import save_temp_file
from ..utils.temp_storage import save_data, load_data


def ruru_standardization_tab():
    """
    Tab para estandarizar datos de Rurus.
    """
    st.header("Estandarización de Datos de Rurus")
    st.write("""
    Esta sección te permite cargar un archivo de Rurus, estandarizar sus columnas
    y prepararlo para el proceso de match. En esta primera fase, se renombrarán 
    las columnas y se eliminarán las que no son necesarias.
    """)
    
    # Inicializar variables
    ruru_df = None
    ruru_file_name = None
    processed_df = None
    
    # Paso 1: Cargar archivo de Rurus
    st.subheader("Paso 1: Cargar archivo de Rurus")
    st.write("Carga el archivo Excel que contiene los datos de Rurus:")
    
    ruru_df, ruru_file_name, success = upload_excel_file(
        key="ruru_file_upload",
        label="Cargar archivo de Rurus (Excel)",
        help_text="Este archivo debe contener los datos de los Rurus que se emparejarán con Yakus"
    )
    
    if success and ruru_df is not None:
        # Mostrar estadísticas del DataFrame original
        st.subheader("Estadísticas del archivo original")
        show_column_statistics(
            ruru_df,
            show_stats=False,
            key="ruru_original_stats"
        )
        
        # Paso 2: Estandarizar columnas
        st.subheader("Paso 2: Estandarizar columnas")
        
        # Definir mapeo de columnas
        # El mapeo tiene el formato {"columna_original": "columna_nueva"}
        # Donde columna_original puede ser la posición (para Excel es 0-indexed, pero para usuario mostramos 1-indexed)
        column_mapping = {
            "H": "nombre",
            "I": "apellido",
            "J": "DNI",
            "K": "colegio",
            "L": "grado",
            "R": "idiomas",
            "AA": "nombre_apoderado",
            "AB": "apellido_apoderado",
            "AD": "celular",
            "BD": "arte_y_cultura",
            "BE": "bienestar_psicologico",
            "BF": "asesoria_a_colegios_nacionales",
            "BM": "taller_opcion1",
            "BN": "taller_opcion2",
            "BO": "taller_opcion3",
            "BP": "asignatura_opcion1",
            "BQ": "asignatura_opcion2",
            "BY": "celular_asesoria",
            "CH": "lunes_mañana",
            "CI": "lunes_tarde",
            "CJ": "lunes_noche",
            "CL": "martes_mañana",
            "CM": "martes_tarde",
            "CN": "martes_noche",
            "CP": "miercoles_mañana",
            "CQ": "miercoles_tarde",
            "CR": "miercoles_noche",
            "CT": "jueves_mañana",
            "CU": "jueves_tarde",
            "CV": "jueves_noche",
            "CX": "viernes_mañana",
            "CY": "viernes_tarde",
            "CZ": "viernes_noche",
            "DB": "sabado_mañana",
            "DC": "sabado_tarde",
            "DD": "sabado_noche",
            "DF": "domingo_mañana",
            "DG": "domingo_tarde",
            "DH": "domingo_noche",
        }
        
        # Mostrar mapeo de columnas
        with st.expander("Ver mapeo de columnas", expanded=False):
            # Crear un DataFrame para mostrar el mapeo
            mapping_data = []
            for col_orig, col_new in column_mapping.items():
                # Si es una letra, traducirla a índice (Excel es 0-indexed pero para usuario mostramos 1-indexed)
                if col_orig.isalpha():
                    col_idx = sum((ord(c.upper()) - ord('A') + 1) * 26**i for i, c in enumerate(reversed(col_orig))) - 1
                    col_name = f"Columna {col_orig} (índice {col_idx})"
                    
                    # Añadir nombre original si está disponible
                    if col_idx < len(ruru_df.columns):
                        orig_name = ruru_df.columns[col_idx]
                        col_name += f": {orig_name}"
                else:
                    col_name = col_orig
                
                mapping_data.append({
                    "Columna Original": col_name,
                    "Nuevo Nombre": col_new
                })
            
            # Mostrar DataFrame de mapeo
            st.dataframe(pd.DataFrame(mapping_data))
        
        # Botón para aplicar estandarización
        if st.button("Estandarizar columnas", key="standardize_columns_button"):
            # Procesar el DataFrame: renombrar columnas y eliminar no mencionadas
            processed_df = standardize_ruru_columns(ruru_df, column_mapping)
            
            # Guardar el DataFrame procesado en el estado de sesión
            save_data(processed_df, "ruru_standardized_df")
            
            if processed_df is not None:
                st.success(f"✅ Columnas estandarizadas correctamente. Se conservaron {len(processed_df.columns)} columnas.")
                
                # Mostrar vista previa
                st.subheader("Vista previa de datos estandarizados")
                preview_dataframe(
                    processed_df,
                    rows=10,
                    title="Vista previa de datos con columnas estandarizadas",
                    expanded=True,
                    key="preview_standardized"
                )
                
                # Guardar temporalmente
                if st.button("Guardar datos estandarizados temporalmente", key="save_temp_standardized"):
                    # Generar nombre base
                    base_name = "rurus_estandarizados"
                    if ruru_file_name:
                        base_name = f"{ruru_file_name.split('.')[0]}_estandarizado"
                    
                    # Guardar temporalmente
                    temp_file_path = save_temp_file(processed_df, base_name)
                    if temp_file_path:
                        st.success(f"✅ Datos guardados temporalmente para uso en otros tabs")
                
                # Mostrar botones de descarga
                st.subheader("Descargar resultados")
                
                # Generar nombre base para el archivo
                base_filename = "rurus_estandarizados"
                if ruru_file_name:
                    base_filename = f"{ruru_file_name.split('.')[0]}_estandarizado"
                
                # Mostrar botones de descarga
                show_download_buttons(processed_df, base_filename)
            else:
                st.error("❌ Ocurrió un error al estandarizar las columnas")
        
        # Cargar datos estandarizados del estado de sesión (si están disponibles)
        elif load_data("ruru_standardized_df") is not None:
            processed_df = load_data("ruru_standardized_df")
            
            st.info("ℹ️ Mostrando resultados de la última estandarización")
            
            # Mostrar vista previa
            st.subheader("Vista previa de datos estandarizados")
            preview_dataframe(
                processed_df,
                rows=10,
                title="Vista previa de datos con columnas estandarizadas",
                expanded=True,
                key="preview_standardized_cached"
            )
            
            # Mostrar botones de descarga
            base_filename = "rurus_estandarizados"
            if ruru_file_name:
                base_filename = f"{ruru_file_name.split('.')[0]}_estandarizado"
            
            show_download_buttons(processed_df, base_filename)
    
    # Mostrar instrucciones si no hay archivo cargado
    elif not success:
        st.info("👆 Carga un archivo de Rurus para comenzar el proceso de estandarización.")


def standardize_ruru_columns(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Estandariza las columnas de un DataFrame de Rurus según un mapeo.
    
    Args:
        df: DataFrame original
        column_mapping: Mapeo de columnas originales a nuevos nombres
    
    Returns:
        DataFrame con columnas estandarizadas
    """
    if df is None or df.empty:
        return None
    
    try:
        # Crear una copia del DataFrame para no modificar el original
        processed_df = df.copy()
        
        # Lista para almacenar las columnas que vamos a conservar
        columns_to_keep = []
        
        # Diccionario para mapear índices a nuevos nombres
        index_to_name = {}
        
        # Primero, procesamos el mapeo para convertir letras a índices
        for col_orig, col_new in column_mapping.items():
            if col_orig.isalpha():
                # Convertir letras de Excel (A, B, C..., AA, AB...) a índice (0, 1, 2...)
                col_idx = sum((ord(c.upper()) - ord('A') + 1) * 26**i for i, c in enumerate(reversed(col_orig))) - 1
                
                # Verificar que el índice está dentro del rango
                if col_idx < len(processed_df.columns):
                    index_to_name[col_idx] = col_new
            else:
                # Si no es letra, asumir que es nombre de columna
                if col_orig in processed_df.columns:
                    index_to_name[list(processed_df.columns).index(col_orig)] = col_new
        
        # Crear un nuevo DataFrame con solo las columnas seleccionadas
        new_df = pd.DataFrame()
        
        # Añadir columnas al nuevo DataFrame con los nombres nuevos
        for idx, new_name in index_to_name.items():
            if idx < len(processed_df.columns):
                new_df[new_name] = processed_df.iloc[:, idx]
        
        return new_df
    
    except Exception as e:
        st.error(f"Error al estandarizar columnas: {str(e)}")
        return None


if __name__ == "__main__":
    # Esto permite probar el tab individualmente
    ruru_standardization_tab() 