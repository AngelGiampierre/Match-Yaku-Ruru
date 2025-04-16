import streamlit as st
import pandas as pd
import os
import sys
import time
from datetime import datetime

# Agregar la raíz del proyecto al path de Python para importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from utils import get_temp_dir, load_data

def file_explorer_tab():
    """
    Tab para explorar archivos temporales.
    Permite ver, cargar y eliminar archivos guardados en el directorio temporal.
    """
    st.header("Explorador de Archivos")
    st.subheader("Administra los archivos temporales generados durante el procesamiento")
    
    # Obtener directorio temporal
    temp_dir = get_temp_dir()
    
    # Verificar si el directorio existe
    if not os.path.exists(temp_dir):
        st.warning(f"⚠️ El directorio temporal '{temp_dir}' no existe.")
        if st.button("Crear directorio temporal"):
            try:
                os.makedirs(temp_dir, exist_ok=True)
                st.success(f"✅ Directorio temporal creado en '{temp_dir}'")
                time.sleep(1)  # Pequeña pausa para que el mensaje sea visible
                st.experimental_rerun()  # Recargar la página
            except Exception as e:
                st.error(f"❌ Error al crear el directorio: {str(e)}")
        return
    
    # Listar archivos en el directorio temporal
    files = os.listdir(temp_dir)
    
    if not files:
        st.info("📂 No hay archivos en el directorio temporal.")
        return
    
    # Filtrar archivos por tipo
    file_filter = st.selectbox(
        "Filtrar por tipo de archivo:",
        options=["Todos", "Excel (.xlsx)", "CSV (.csv)", "Pickle (.pkl)", "Otros"]
    )
    
    if file_filter == "Excel (.xlsx)":
        files = [f for f in files if f.endswith('.xlsx')]
    elif file_filter == "CSV (.csv)":
        files = [f for f in files if f.endswith('.csv')]
    elif file_filter == "Pickle (.pkl)":
        files = [f for f in files if f.endswith('.pkl')]
    elif file_filter == "Otros":
        files = [f for f in files if not (f.endswith('.xlsx') or f.endswith('.csv') or f.endswith('.pkl'))]
    
    # Buscar por nombre
    file_search = st.text_input("Buscar por nombre de archivo:")
    if file_search:
        files = [f for f in files if file_search.lower() in f.lower()]
    
    # Organizar archivos por categoría
    st.write("### Archivos disponibles")
    
    if not files:
        st.info(f"📂 No hay archivos que coincidan con los criterios de filtrado.")
        return
    
    # Obtener información de los archivos
    file_info = []
    for file in files:
        file_path = os.path.join(temp_dir, file)
        if os.path.isfile(file_path):
            # Obtener tamaño y fecha de modificación
            file_size = os.path.getsize(file_path)
            file_mtime = os.path.getmtime(file_path)
            modified_date = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # Categorizar el archivo
            category = "Otros"
            if "yaku" in file.lower():
                category = "Yakus"
            elif "ruru" in file.lower():
                category = "Rurus"
            elif "course" in file.lower() or "curso" in file.lower():
                category = "Cursos"
            elif "config" in file.lower():
                category = "Configuración"
            
            # Añadir a la lista
            file_info.append({
                "Archivo": file,
                "Categoría": category,
                "Tamaño (KB)": round(file_size / 1024, 2),
                "Fecha de modificación": modified_date
            })
    
    # Convertir a DataFrame y mostrar
    files_df = pd.DataFrame(file_info)
    
    # Opción para ordenar
    sort_by = st.selectbox(
        "Ordenar por:",
        options=["Fecha de modificación", "Archivo", "Tamaño (KB)", "Categoría"],
        index=0
    )
    
    sort_order = st.radio(
        "Orden:",
        options=["Descendente", "Ascendente"],
        horizontal=True,
        index=0
    )
    
    # Aplicar ordenamiento
    ascending = sort_order == "Ascendente"
    files_df = files_df.sort_values(by=sort_by, ascending=ascending)
    
    # Mostrar tabla de archivos
    st.dataframe(files_df, use_container_width=True)
    
    # Seleccionar archivo para previsualizar
    st.write("### Previsualizar archivo")
    preview_file = st.selectbox(
        "Selecciona un archivo para previsualizar:",
        options=[""] + files_df["Archivo"].tolist()
    )
    
    if preview_file:
        file_path = os.path.join(temp_dir, preview_file)
        
        # Mostrar información del archivo
        file_size = os.path.getsize(file_path)
        file_mtime = os.path.getmtime(file_path)
        modified_date = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        st.write(f"**Archivo:** {preview_file}")
        st.write(f"**Tamaño:** {round(file_size / 1024, 2)} KB")
        st.write(f"**Última modificación:** {modified_date}")
        
        # Previsualizar según el tipo de archivo
        if preview_file.endswith(".pkl"):
            if st.button("Cargar datos del archivo Pickle"):
                try:
                    data = load_data(preview_file)
                    if data is not None:
                        if isinstance(data, pd.DataFrame):
                            st.success(f"✅ DataFrame cargado: {data.shape[0]} filas x {data.shape[1]} columnas")
                            st.dataframe(data.head(10))
                        else:
                            st.success(f"✅ Datos cargados (tipo: {type(data)})")
                            st.write(data)
                    else:
                        st.warning("⚠️ El archivo no contiene datos válidos o está vacío.")
                except Exception as e:
                    st.error(f"❌ Error al cargar el archivo: {str(e)}")
        
        elif preview_file.endswith((".xlsx", ".csv")):
            try:
                if preview_file.endswith(".xlsx"):
                    data = pd.read_excel(file_path)
                else:  # .csv
                    data = pd.read_csv(file_path)
                
                st.success(f"✅ Archivo cargado: {data.shape[0]} filas x {data.shape[1]} columnas")
                st.dataframe(data.head(10))
            except Exception as e:
                st.error(f"❌ Error al leer el archivo: {str(e)}")
        
        else:
            st.info("Previsualización no disponible para este tipo de archivo.")
    
    # Opciones para eliminar archivos
    st.write("### Eliminar archivos")
    
    delete_options = st.radio(
        "Opciones de eliminación:",
        options=["Eliminar archivo específico", "Eliminar por categoría", "Eliminar todos"],
        horizontal=True
    )
    
    if delete_options == "Eliminar archivo específico":
        delete_file = st.selectbox(
            "Selecciona un archivo para eliminar:",
            options=files_df["Archivo"].tolist()
        )
        
        if delete_file and st.button(f"Eliminar '{delete_file}'"):
            try:
                os.remove(os.path.join(temp_dir, delete_file))
                st.success(f"✅ Archivo '{delete_file}' eliminado correctamente.")
                time.sleep(1)  # Pequeña pausa para que el mensaje sea visible
                st.experimental_rerun()  # Recargar la página
            except Exception as e:
                st.error(f"❌ Error al eliminar el archivo: {str(e)}")
    
    elif delete_options == "Eliminar por categoría":
        delete_category = st.selectbox(
            "Selecciona categoría para eliminar:",
            options=["Yakus", "Rurus", "Cursos", "Configuración", "Otros"]
        )
        
        files_to_delete = files_df[files_df["Categoría"] == delete_category]["Archivo"].tolist()
        
        if files_to_delete:
            st.write(f"Se eliminarán {len(files_to_delete)} archivos:")
            for file in files_to_delete[:5]:  # Mostrar solo los primeros 5
                st.write(f"- {file}")
            if len(files_to_delete) > 5:
                st.write(f"- ... y {len(files_to_delete) - 5} más")
            
            if st.button(f"Eliminar todos los archivos de '{delete_category}'"):
                try:
                    deleted_count = 0
                    for file in files_to_delete:
                        os.remove(os.path.join(temp_dir, file))
                        deleted_count += 1
                    
                    st.success(f"✅ {deleted_count} archivos eliminados correctamente.")
                    time.sleep(1)  # Pequeña pausa para que el mensaje sea visible
                    st.experimental_rerun()  # Recargar la página
                except Exception as e:
                    st.error(f"❌ Error al eliminar archivos: {str(e)}")
        else:
            st.info(f"No hay archivos en la categoría '{delete_category}'.")
    
    elif delete_options == "Eliminar todos":
        if st.button("Eliminar todos los archivos", help="Elimina todos los archivos del directorio temporal"):
            try:
                deleted_count = 0
                for file in files:
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                
                st.success(f"✅ {deleted_count} archivos eliminados correctamente.")
                time.sleep(1)  # Pequeña pausa para que el mensaje sea visible
                st.experimental_rerun()  # Recargar la página
            except Exception as e:
                st.error(f"❌ Error al eliminar archivos: {str(e)}")
    
    # Información sobre el directorio temporal
    with st.expander("Información del directorio temporal"):
        st.write(f"**Ruta del directorio temporal:** {temp_dir}")
        st.write(f"**Número total de archivos:** {len(files)}")
        
        # Calcular espacio total utilizado
        total_size = sum(os.path.getsize(os.path.join(temp_dir, file)) for file in files if os.path.isfile(os.path.join(temp_dir, file)))
        st.write(f"**Espacio total utilizado:** {round(total_size / (1024 * 1024), 2)} MB")
        
        # Distribucion por categoría
        category_counts = files_df["Categoría"].value_counts()
        st.write("**Distribución por categoría:**")
        for category, count in category_counts.items():
            st.write(f"- {category}: {count} archivos")
        
        # Tipos de archivo
        extensions = [os.path.splitext(file)[1] for file in files]
        extension_counts = pd.Series(extensions).value_counts()
        st.write("**Distribución por tipo de archivo:**")
        for ext, count in extension_counts.items():
            if ext:
                st.write(f"- {ext}: {count} archivos")
            else:
                st.write(f"- Sin extensión: {count} archivos") 