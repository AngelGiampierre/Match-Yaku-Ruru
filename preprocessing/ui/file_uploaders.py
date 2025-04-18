"""
Componentes de UI para subir archivos.

Contiene widgets reutilizables para la carga de archivos Excel y CSV.
"""

import streamlit as st
from typing import Tuple, Optional, Any, List
import pandas as pd
from ..utils.file_io import read_file


def upload_excel_file(
    key: str, 
    label: str = "Cargar archivo",
    help_text: str = "Formatos soportados: Excel (.xlsx, .xls) y CSV",
    types: List[str] = ["xlsx", "xls", "csv"]
) -> Tuple[Optional[pd.DataFrame], Optional[str], bool]:
    """
    Crea un componente para subir archivos Excel o CSV.
    
    Args:
        key: Clave única para el componente
        label: Texto del botón de carga
        help_text: Texto de ayuda
        types: Tipos de archivo permitidos
        
    Returns:
        Tupla con (DataFrame, nombre_archivo, éxito)
        Si no se sube archivo o hay error, DataFrame será None
    """
    # Contenedor para el uploader
    upload_container = st.container()
    
    with upload_container:
        # Mostrar el uploader
        uploaded_file = st.file_uploader(
            label=label,
            type=types,
            help=help_text,
            key=key
        )
        
        if uploaded_file is not None:
            # Leer el archivo
            df, file_type, error = read_file(uploaded_file)
            
            if error:
                st.error(f"Error: {error}")
                return None, uploaded_file.name, False
            
            # Mostrar información básica del archivo
            st.success(f"✅ Archivo cargado correctamente: {uploaded_file.name}")
            
            if df is not None:
                st.write(f"Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
                
                # Mostrar vista previa
                with st.expander("Vista previa del archivo", expanded=True):
                    st.dataframe(df.head(5))
                
                return df, uploaded_file.name, True
        
        return None, None, False


def show_download_buttons(
    df: pd.DataFrame,
    base_filename: str = "datos_procesados",
    excel_label: str = "📥 Descargar como Excel",
    csv_label: str = "📥 Descargar como CSV"
) -> None:
    """
    Muestra botones para descargar un DataFrame como Excel o CSV.
    
    Args:
        df: DataFrame a descargar
        base_filename: Nombre base del archivo (sin extensión)
        excel_label: Etiqueta para el botón de Excel
        csv_label: Etiqueta para el botón de CSV
    """
    from ..utils.file_io import save_excel, save_csv
    from datetime import datetime
    
    if df is None or df.empty:
        st.warning("No hay datos para descargar")
        return
    
    # Agregar timestamp al nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}"
    
    # Crear columnas para los botones
    col1, col2 = st.columns(2)
    
    # Botón para Excel
    with col1:
        success, excel_data, excel_filename = save_excel(df, filename)
        if success:
            st.download_button(
                label=excel_label,
                data=excel_data,
                file_name=excel_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Botón para CSV
    with col2:
        success, csv_data, csv_filename = save_csv(df, filename)
        if success:
            st.download_button(
                label=csv_label,
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv"
            ) 