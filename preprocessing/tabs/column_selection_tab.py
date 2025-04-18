"""
Pestaña para selección de columnas.

Permite al usuario seleccionar las columnas relevantes del archivo 
y guardar el resultado.
"""

import streamlit as st
import pandas as pd
import os

from preprocessing.utils.file_handler import save_dataframe, get_temp_file_path
from preprocessing.utils.session_state import get_dataframe, set_dataframe, set_processing_step
from preprocessing.ui.uploader import file_uploader
from preprocessing.ui.selectors import select_columns
from preprocessing.ui.download import download_buttons


def column_selection_tab():
    """
    Muestra la pestaña para seleccionar columnas de un archivo.
    """
    st.header("Selección de Columnas")
    st.write("""
    En esta pestaña puedes cargar un archivo Excel o CSV y seleccionar 
    las columnas que deseas conservar.
    """)
    
    # Subir archivo
    uploaded_file = file_uploader(
        "Sube un archivo Excel o CSV",
        ["xlsx", "xls", "csv"],
        key="column_select_upload"
    )
    
    # Procesar archivo
    if uploaded_file is not None:
        try:
            # Leer archivo
            df = None
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(uploaded_file)
            elif file_ext == '.csv':
                df = pd.read_csv(uploaded_file)
            
            if df is not None and not df.empty:
                # Guardar DataFrame original en estado de sesión
                set_dataframe(df, "original_df")
                
                # Seleccionar columnas
                selected_columns, filtered_df = select_columns(
                    df,
                    key_prefix="col_select",
                    preselect_important=True
                )
                
                # Si se han seleccionado columnas
                if selected_columns and filtered_df is not None:
                    # Guardar DataFrame filtrado en estado de sesión
                    set_dataframe(filtered_df, "filtered_df")
                    
                    # Mostrar botones de descarga
                    if st.button("Guardar y continuar", key="save_continue_columns"):
                        # Guardar en archivo temporal
                        temp_file = save_dataframe(filtered_df, "columnas_seleccionadas")
                        
                        if temp_file:
                            st.success(f"✅ Archivo guardado correctamente: {os.path.basename(temp_file)}")
                            # Actualizar paso de procesamiento
                            set_processing_step("column_selection", True)
                        else:
                            st.error("❌ Error al guardar el archivo")
                    
                    # Mostrar botones de descarga
                    download_buttons(filtered_df, "columnas_seleccionadas")
                    
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")
    else:
        # Intentar recuperar DataFrame de estado de sesión
        df = get_dataframe("filtered_df")
        if df is not None:
            st.success("✅ Se ha cargado el último conjunto de datos procesado")
            
            # Mostrar DataFrame
            st.write("### Vista previa del último conjunto de datos")
            st.dataframe(df.head(), use_container_width=True)
            
            # Mostrar botones de descarga
            download_buttons(df, "columnas_seleccionadas")
        else:
            st.info("ℹ️ Sube un archivo para comenzar el procesamiento")


if __name__ == "__main__":
    # Esto permite probar el tab individualmente
    column_selection_tab() 