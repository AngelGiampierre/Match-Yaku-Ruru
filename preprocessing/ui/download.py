"""
Componentes de UI para descarga de archivos.

Contiene widgets reutilizables para descargar archivos procesados.
"""

import streamlit as st
import pandas as pd
import io


def get_excel_download_link(df, filename="datos_procesados"):
    """
    Genera un enlace de descarga para un DataFrame en formato Excel.
    
    Args:
        df (pd.DataFrame): DataFrame a descargar
        filename (str): Nombre del archivo sin extensión
        
    Returns:
        bytes: Datos binarios del archivo Excel
    """
    if df is None or df.empty:
        return None
        
    # Convertir a Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
    
    # Obtener bytes
    excel_data = output.getvalue()
    return excel_data


def get_csv_download_link(df, filename="datos_procesados"):
    """
    Genera un enlace de descarga para un DataFrame en formato CSV.
    
    Args:
        df (pd.DataFrame): DataFrame a descargar
        filename (str): Nombre del archivo sin extensión
        
    Returns:
        str: Datos en formato CSV
    """
    if df is None or df.empty:
        return None
        
    # Convertir a CSV
    return df.to_csv(index=False).encode('utf-8')


def download_buttons(df, filename_prefix="datos"):
    """
    Muestra botones para descargar un DataFrame en diferentes formatos.
    
    Args:
        df (pd.DataFrame): DataFrame a descargar
        filename_prefix (str): Prefijo para el nombre del archivo
    """
    if df is None or df.empty:
        st.warning("No hay datos para descargar")
        return
    
    st.write("### Descargar datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Botón para Excel
        excel_data = get_excel_download_link(df, filename_prefix)
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_data,
            file_name=f"{filename_prefix}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_excel_{filename_prefix}"
        )
    
    with col2:
        # Botón para CSV
        csv_data = get_csv_download_link(df, filename_prefix)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv_data,
            file_name=f"{filename_prefix}.csv",
            mime="text/csv",
            key=f"download_csv_{filename_prefix}"
        ) 