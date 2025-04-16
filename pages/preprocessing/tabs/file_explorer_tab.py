import streamlit as st
import os
import pandas as pd
import sys

# Agregar la raíz del proyecto al path de Python para importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from utils import get_temp_dir

def file_explorer_tab():
    """
    Tab para explorar y gestionar los archivos temporales del sistema.
    """
    st.header("Explorador de Archivos")
    st.subheader("Gestiona los archivos temporales del sistema")
    
    # Obtener directorio temporal
    temp_dir = get_temp_dir()
    
    # Listar archivos en el directorio temporal
    archivos = []
    for archivo in os.listdir(temp_dir):
        ruta_completa = os.path.join(temp_dir, archivo)
        tamaño = os.path.getsize(ruta_completa)
        fecha_mod = os.path.getmtime(ruta_completa)
        archivos.append({
            "Nombre": archivo,
            "Tamaño (KB)": round(tamaño / 1024, 2),
            "Fecha de modificación": pd.to_datetime(fecha_mod, unit='s')
        })
    
    # Crear DataFrame con la información de los archivos
    if archivos:
        df_archivos = pd.DataFrame(archivos)
        
        # Mostrar información
        st.write(f"Directorio temporal: `{temp_dir}`")
        st.write(f"Total de archivos: {len(archivos)}")
        
        # Mostrar tabla de archivos
        st.dataframe(df_archivos.sort_values(by="Fecha de modificación", ascending=False))
        
        # Opciones para eliminar archivos
        st.subheader("Eliminar archivos")
        opcion_eliminar = st.radio(
            "Selecciona una opción:",
            ["No eliminar", "Eliminar archivo específico", "Eliminar todos los archivos"]
        )
        
        if opcion_eliminar == "Eliminar archivo específico":
            archivo_a_eliminar = st.selectbox(
                "Selecciona el archivo a eliminar:",
                options=[a["Nombre"] for a in archivos]
            )
            
            if st.button("Eliminar archivo seleccionado"):
                try:
                    os.remove(os.path.join(temp_dir, archivo_a_eliminar))
                    st.success(f"✅ Archivo '{archivo_a_eliminar}' eliminado correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al eliminar el archivo: {str(e)}")
        
        elif opcion_eliminar == "Eliminar todos los archivos":
            if st.button("Eliminar todos los archivos"):
                try:
                    for archivo in os.listdir(temp_dir):
                        ruta_completa = os.path.join(temp_dir, archivo)
                        if os.path.isfile(ruta_completa):
                            os.remove(ruta_completa)
                    st.success("✅ Todos los archivos han sido eliminados correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al eliminar los archivos: {str(e)}")
    else:
        st.info("No hay archivos en el directorio temporal.") 