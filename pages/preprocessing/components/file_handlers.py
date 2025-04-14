import streamlit as st
import pandas as pd
import base64
from io import BytesIO

def export_dataframe(df, filename, format_type="Excel (.xlsx)"):
    """
    Exporta un DataFrame a un archivo Excel o CSV y proporciona un enlace de descarga.
    
    Args:
        df (pd.DataFrame): DataFrame a exportar
        filename (str): Nombre del archivo sin extensión
        format_type (str): Formato de exportación ("Excel (.xlsx)" o "CSV (.csv)")
        
    Returns:
        None: Muestra un enlace de descarga en Streamlit
    """
    # Asegurarnos que todas las columnas de texto sean de tipo string para evitar problemas con PyArrow
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str)
    
    # Exportar según formato
    if format_type == "Excel (.xlsx)":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Datos', index=False)
        
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">📥 Descargar archivo Excel</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    else:  # CSV
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:text/csv;base64,{b64}" download="{filename}.csv">📥 Descargar archivo CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    st.success(f"✅ Archivo '{filename}' listo para descargar") 