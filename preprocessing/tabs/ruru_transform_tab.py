"""
Pestaña para transformación avanzada de datos de Rurus.

Este módulo permite transformar un archivo de Rurus que ya tiene columnas estandarizadas:
- Crear una columna única de área
- Estandarizar formato de horarios
- Estandarizar grados e idiomas
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import re

# Importamos componentes de UI
from ..ui.file_uploaders import upload_excel_file, show_download_buttons
from ..ui.displays import preview_dataframe, show_column_statistics

# Importamos utilidades
from ..utils.file_io import save_temp_file
from ..utils.temp_storage import save_data, load_data


def ruru_transform_tab():
    """
    Tab para transformar datos de Rurus.
    """
    st.header("Transformación de Datos de Rurus")
    st.write("""
    Esta sección te permite transformar un archivo de Rurus que ya tiene columnas estandarizadas,
    creando una columna única de área, estandarizando horarios y estandarizando grados e idiomas.
    """)
    
    # Inicializar variables
    ruru_df = None
    ruru_file_name = None
    processed_df = None
    
    # Paso 1: Cargar archivo de Rurus estandarizado
    st.subheader("Paso 1: Cargar archivo de Rurus estandarizado")
    st.write("Carga el archivo Excel que contiene los datos de Rurus con columnas estandarizadas:")
    
    ruru_df, ruru_file_name, success = upload_excel_file(
        key="ruru_transform_upload",
        label="Cargar archivo de Rurus estandarizado (Excel)",
        help_text="Este archivo debe contener los datos de Rurus con columnas ya renombradas"
    )
    
    if success and ruru_df is not None:
        # Verificar que el archivo tiene las columnas necesarias
        required_columns = [
            "arte_y_cultura", "bienestar_psicologico", "asesoria_a_colegios_nacionales",
            "Grado del estudiante:",
            "idiomas",
            "ID del estudiante:"
        ]
        
        # También necesitamos columnas de horarios
        dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
        turnos = ["mañana", "tarde", "noche"]
        
        horario_columns = [f"{dia}_{turno}" for dia in dias for turno in turnos]
        
        missing_columns = [col for col in required_columns if col not in ruru_df.columns]
        missing_horarios = [col for col in horario_columns if col not in ruru_df.columns]
        
        if missing_columns:
            st.error(f"❌ El archivo no contiene todas las columnas necesarias. Faltan: {', '.join(missing_columns)}")
            st.info("Asegúrate de que el archivo haya sido procesado correctamente en la pestaña 'Estandarización de Rurus' y que incluya las columnas requeridas (como 'Grado del estudiante:', 'ID del estudiante:', etc.).")
        elif missing_horarios:
            st.warning(f"⚠️ Algunas columnas de horarios no se encontraron: {', '.join(missing_horarios[:5])}...")
            st.info("Es posible que algunos horarios no estén disponibles o tengan nombres diferentes")
            
            # Continuar aún con la advertencia
            st.subheader("Vista previa de datos cargados")
            preview_dataframe(
                ruru_df,
                rows=5,
                title="Vista previa de datos cargados",
                expanded=True,
                key="preview_loaded"
            )
            
            # Mostrar opciones de transformación
            st.subheader("Paso 2: Transformar datos")
            
            # Opciones de transformación
            transformations = {
                "area": "Crear columna única de 'area'",
                "horarios": "Estandarizar formato de horarios",
                "grado": "Estandarizar grados",
                "idioma": "Estandarizar idiomas"
            }
            
            selected_transformations = []
            for key, label in transformations.items():
                if st.checkbox(label, value=True, key=f"check_{key}"):
                    selected_transformations.append(key)
            
            # Botón para aplicar transformaciones
            if selected_transformations and st.button("Aplicar transformaciones", key="apply_transforms"):
                # Copiar DataFrame original
                processed_df = ruru_df.copy()
                
                # Aplicar transformaciones seleccionadas
                if "area" in selected_transformations:
                    processed_df = create_area_column(processed_df)
                    st.success("✅ Columna única de 'area' creada correctamente")
                
                if "horarios" in selected_transformations:
                    processed_df = standardize_schedules(processed_df)
                    st.success("✅ Formato de horarios estandarizado correctamente")
                
                if "grado" in selected_transformations:
                    # Nombres exactos de las columnas requeridas
                    id_col = "ID del estudiante:"
                    original_grade_col_name = "Grado del estudiante:"

                    # Verificar existencia de columnas necesarias antes de llamar a la función
                    if id_col not in processed_df.columns:
                        st.error(f"Error: Falta la columna de ID requerida '{id_col}'.")
                        processed_df = None
                    elif original_grade_col_name not in processed_df.columns:
                         st.error(f"Error: Falta la columna de grado original requerida '{original_grade_col_name}'.")
                         processed_df = None

                    if processed_df is not None:
                        processed_df = standardize_grades(
                            processed_df,
                            id_column_name=id_col,
                            original_grade_col=original_grade_col_name
                        )
                        # Verificar si las columnas esperadas ('grado' y 'grado_original') se crearon
                        if 'grado' in processed_df.columns and 'grado_original' in processed_df.columns:
                            st.success(f"✅ Grados de '{original_grade_col_name}' estandarizados en columna 'grado' (y conservados en 'grado_original')")
                        else:
                            # Esto podría pasar si la función tuvo un error interno y devolvió el df original
                            st.warning("⚠️ Hubo un problema al estandarizar los grados. Verifica las columnas de salida.")
                            # Podríamos considerar `processed_df = None` si esto es un error crítico

                if "idioma" in selected_transformations and processed_df is not None:
                    processed_df = standardize_languages(processed_df)
                    st.success("✅ Idiomas estandarizados correctamente")

                # Guardar y mostrar resultados (solo si processed_df no es None)
                if processed_df is not None:
                    # Guardar resultado en estado de sesión
                    save_data(processed_df, "ruru_transformed_df")

                    # Mostrar resultado
                    st.subheader("Resultado de la transformación")
                    preview_dataframe(
                        processed_df,
                        rows=10,
                        title="Vista previa de datos transformados",
                        expanded=True,
                        key="preview_transformed"
                    )

                    # Botones de descarga
                    st.subheader("Descargar resultados")
                    base_filename = "rurus_transformados"
                    if ruru_file_name:
                        base_filename = f"{ruru_file_name.split('.')[0]}_transformado"
                    
                    show_download_buttons(processed_df, base_filename)
        else:
            # Archivo tiene todas las columnas necesarias
            st.success("✅ Archivo cargado correctamente con todas las columnas necesarias (incluyendo 'Grado del estudiante:' y 'ID del estudiante:')")
            
            # Mostrar vista previa
            st.subheader("Vista previa de datos cargados")
            preview_dataframe(
                ruru_df,
                rows=5,
                title="Vista previa de datos cargados",
                expanded=True,
                key="preview_loaded"
            )
            
            # Mostrar opciones de transformación
            st.subheader("Paso 2: Transformar datos")
            
            # Opciones de transformación
            transformations = {
                "area": "Crear columna única de 'area'",
                "horarios": "Estandarizar formato de horarios",
                "grado": "Estandarizar grados",
                "idioma": "Estandarizar idiomas"
            }
            
            selected_transformations = []
            for key, label in transformations.items():
                if st.checkbox(label, value=True, key=f"check_{key}"):
                    selected_transformations.append(key)
            
            # Botón para aplicar transformaciones
            if selected_transformations and st.button("Aplicar transformaciones", key="apply_transforms_alt"):
                processed_df = ruru_df.copy()
                
                # Aplicar transformaciones seleccionadas
                if "area" in selected_transformations:
                    processed_df = create_area_column(processed_df)
                    st.success("✅ Columna única de 'area' creada correctamente")
                
                if "horarios" in selected_transformations:
                    processed_df = standardize_schedules(processed_df)
                    st.success("✅ Formato de horarios estandarizado correctamente")
                
                if "grado" in selected_transformations:
                    id_col = "ID del estudiante:"
                    original_grade_col_name = "Grado del estudiante:"
                    if id_col not in processed_df.columns:
                        st.error(f"Error: Falta la columna de ID requerida '{id_col}'.")
                        processed_df = None
                    elif original_grade_col_name not in processed_df.columns:
                         st.error(f"Error: Falta la columna de grado original requerida '{original_grade_col_name}'.")
                         processed_df = None

                    if processed_df is not None:
                        processed_df = standardize_grades(
                            processed_df,
                            id_column_name=id_col,
                            original_grade_col=original_grade_col_name
                        )
                        if 'grado' in processed_df.columns and 'grado_original' in processed_df.columns:
                            st.success(f"✅ Grados estandarizados (conservando original)")
                        else:
                            st.warning("⚠️ Problema al estandarizar grados.")

                if "idioma" in selected_transformations and processed_df is not None:
                    processed_df = standardize_languages(processed_df)
                    st.success("✅ Idiomas estandarizados correctamente")

                # Guardar y mostrar resultados (solo si processed_df no es None)
                if processed_df is not None:
                    # Guardar resultado en estado de sesión
                    save_data(processed_df, "ruru_transformed_df")

                    # Mostrar resultado
                    st.subheader("Resultado de la transformación")
                    preview_dataframe(
                        processed_df,
                        rows=10,
                        title="Vista previa de datos transformados",
                        expanded=True,
                        key="preview_transformed"
                    )

                    # Botones de descarga
                    st.subheader("Descargar resultados")
                    base_filename = "rurus_transformados"
                    if ruru_file_name:
                        base_filename = f"{ruru_file_name.split('.')[0]}_transformado"
                    
                    show_download_buttons(processed_df, base_filename)
        
        # Cargar datos transformados del estado de sesión (si están disponibles)
    elif load_data("ruru_transformed_df") is not None:
        processed_df = load_data("ruru_transformed_df")
        
        st.info("ℹ️ Mostrando resultados de la última transformación")
        
        # Mostrar vista previa
        st.subheader("Vista previa de datos transformados")
        preview_dataframe(
            processed_df,
            rows=10,
            title="Vista previa de datos transformados",
            expanded=True,
            key="preview_transformed_cached"
        )
        
        # Mostrar botones de descarga
        base_filename = "rurus_transformados"
        if ruru_file_name:
            base_filename = f"{ruru_file_name.split('.')[0]}_transformado"
        
        show_download_buttons(processed_df, base_filename)
    
    # Mostrar instrucciones si no hay archivo cargado
    elif not success:
        st.info("👆 Carga un archivo de Rurus estandarizado para comenzar la transformación.")


def create_area_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea una columna única de "area" basada en las columnas de área específicas.
    
    Args:
        df: DataFrame con columnas de áreas
        
    Returns:
        DataFrame con nueva columna "area"
    """
    # Verificar que las columnas necesarias existen
    area_columns = ["arte_y_cultura", "bienestar_psicologico", "asesoria_a_colegios_nacionales"]
    
    # Crear columna "area" vacía
    df["area"] = ""
    
    # Condición para cada área
    for area_col in area_columns:
        if area_col in df.columns:
            # Reemplazar valores vacíos con 0 y convertir a entero
            df[area_col] = df[area_col].fillna(0).astype(str)
            
            # Donde el valor es "1", asignar el nombre del área correspondiente
            area_name = area_col.replace("_", " ").title()
            
            # Las áreas tienen estas correspondencias:
            area_map = {
                "arte_y_cultura": "Arte & Cultura",
                "bienestar_psicologico": "Bienestar Psicológico",
                "asesoria_a_colegios_nacionales": "Asesoría a Colegios Nacionales"
            }
            
            # Asignar nombre de área estandarizado donde hay 1
            df.loc[df[area_col] == "1", "area"] = area_map.get(area_col, area_name)
    
    return df


def standardize_schedules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estandariza el formato de horarios para coincidir con el formato de Yakus.
    
    Args:
        df: DataFrame con columnas de horarios
        
    Returns:
        DataFrame con horarios estandarizados
    """
    # Obtener todas las columnas de horarios
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    turnos = ["mañana", "tarde", "noche"]
    
    horario_columns = [f"{dia}_{turno}" for dia in dias for turno in turnos]
    
    # Crear las columnas de horario unificadas para cada día
    for dia in dias:
        # Verificar si existen las columnas de turnos para este día
        turnos_dia = [f"{dia}_{turno}" for turno in turnos]
        turnos_existentes = [col for col in turnos_dia if col in df.columns]
        
        if turnos_existentes:
            # Crear columna unificada para este día
            col_horario = f"horario_{dia}"
            df[col_horario] = ""
            
            # Formato para cada turno, similar al formato de Yakus
            formato_turnos = {
                f"{dia}_mañana": "Mañana (8am -12 m)",
                f"{dia}_tarde": "Tarde (2pm -6 pm)",
                f"{dia}_noche": "Noche (6pm -10 pm)"
            }
            
            # Crear un diccionario para seguir los turnos ya añadidos para cada fila
            turnos_añadidos = {i: set() for i in range(len(df))}
            
            # Procesar cada turno
            for turno_col in turnos_existentes:
                if turno_col in df.columns:
                    # Convertir la columna a un formato que podamos procesar
                    df[turno_col] = df[turno_col].fillna(0)
                    
                    # Intentar convertir a numérico (para manejar strings, floats, ints, etc.)
                    try:
                        df[turno_col] = pd.to_numeric(df[turno_col], errors='coerce').fillna(0)
                    except:
                        # Si falla, asegurar que tenemos strings
                        df[turno_col] = df[turno_col].astype(str)
                    
                    # Ahora verificar si hay disponibilidad (valor 1 como número o string)
                    if pd.api.types.is_numeric_dtype(df[turno_col]):
                        disponible_mask = df[turno_col] == 1
                    else:
                        # Para strings, verificar "1" o valores que indiquen disponibilidad
                        disponible_mask = df[turno_col].isin(["1", "true", "True", "yes", "Yes", "disponible", "Disponible"])
                    
                    # Obtener el formato de turno correspondiente
                    formato_turno = formato_turnos.get(turno_col, "")
                    
                    # Iterar sobre cada fila que tiene disponibilidad
                    for idx in df.index[disponible_mask]:
                        # Verificar si el turno ya fue añadido para esta fila
                        if formato_turno not in turnos_añadidos[idx]:
                            # Si la columna está vacía, simplemente asignar el formato
                            if df.loc[idx, col_horario] == "":
                                df.loc[idx, col_horario] = formato_turno
                            else:
                                # Si ya hay otros valores, añadir con coma
                                df.loc[idx, col_horario] += f", {formato_turno}"
                            
                            # Marcar este turno como añadido para esta fila
                            turnos_añadidos[idx].add(formato_turno)
            
            # Donde no haya disponibilidad, poner "No disponible"
            df.loc[df[col_horario] == "", col_horario] = "No disponible"
            
            # Eliminar columnas de turnos individuales
            df = df.drop(columns=turnos_existentes, errors='ignore')
    
    return df


def standardize_grades(df: pd.DataFrame, id_column_name: str = "ID del estudiante:", original_grade_col: str = "Grado del estudiante:") -> pd.DataFrame:
    """
    Estandariza los grados escolares usando búsqueda de palabras clave.
    """
    # Verificar columna de grado original
    if original_grade_col not in df.columns:
        st.warning(f"⚠️ La columna de grado original '{original_grade_col}' no se encontró. No se puede estandarizar.")
        return df

    # Verificar si existe la columna de ID
    if id_column_name not in df.columns:
        st.warning(f"⚠️ La columna de ID '{id_column_name}' no se encontró. Asegúrate de que exista para el reporte final.")
        # Considerar manejo de error si el ID es absolutamente crucial

    # Conservar el grado original
    df['grado_original'] = df[original_grade_col].astype(str)

    # Función interna para aplicar la estandarización con palabras clave
    def standardize_grade_value(grade_str):
        if pd.isna(grade_str):
            return "No especificado"

        # Limpiar, convertir a minúsculas
        lower_grade = str(grade_str).strip().lower()

        if not lower_grade:
             return "No especificado"

        # --- Lógica de Palabras Clave ---
        # ** Añadir caso especial para "2 primaria" **
        if "2" in lower_grade and "primaria" in lower_grade and "segundo" not in lower_grade: # Evitar conflicto con "segundo" si existe
            return "Primaria (3° y 4° grado)" # Mapeo especial solicitado

        # Primaria (Continuar con las demás reglas)
        elif "tercero" in lower_grade and "primaria" in lower_grade:
            return "Primaria (3° y 4° grado)"
        elif "cuarto" in lower_grade and "primaria" in lower_grade:
            return "Primaria (3° y 4° grado)"
        elif "quinto" in lower_grade and "primaria" in lower_grade:
            return "Primaria (5° y 6° grado)"
        elif "sexto" in lower_grade and "primaria" in lower_grade:
            return "Primaria (5° y 6° grado)"
        elif "primero" in lower_grade and "primaria" in lower_grade:
             return "Primaria (1° y 2° grado)"
        elif "segundo" in lower_grade and "primaria" in lower_grade:
             # Esta regla ahora no se aplicará si "2 primaria" ya coincidió antes
             return "Primaria (1° y 2° grado)"
        # Secundaria
        elif "primero" in lower_grade and "secundaria" in lower_grade:
            return "Secundaria (1°, 2° y 3° grado)"
        elif "segundo" in lower_grade and "secundaria" in lower_grade:
            return "Secundaria (1°, 2° y 3° grado)"
        elif "tercero" in lower_grade and "secundaria" in lower_grade:
            return "Secundaria (1°, 2° y 3° grado)"

        # Fallback: Si ninguna combinación coincide, devolver el original limpiado
        return str(grade_str).strip() # Devolver el original (sin convertir a minúscula)

    # Aplicar estandarización para crear la nueva columna 'grado'
    df["grado"] = df['grado_original'].apply(standardize_grade_value)

    # Añadir registro estadístico
    standard_grades_list = [
        "Primaria (1° y 2° grado)",
        "Primaria (3° y 4° grado)",
        "Primaria (5° y 6° grado)",
        "Secundaria (1°, 2° y 3° grado)",
        "No especificado"
    ]
    valores_no_estandarizados = df["grado"][
        ~df["grado"].isin(standard_grades_list) & (df["grado"] != "No especificado")
    ].unique()

    if len(valores_no_estandarizados) > 0:
        st.warning(f"⚠️ Algunos valores de grado ('{original_grade_col}') no pudieron ser estandarizados a un formato conocido y se mantuvieron como están en la columna 'grado': {list(valores_no_estandarizados)}")

    # Reordenar columnas (opcional, para poner grado_original cerca de grado)
    cols = df.columns.tolist()
    if 'grado' in cols and 'grado_original' in cols:
        try:
            # Mover 'grado_original' justo después de 'grado'
            cols.insert(cols.index('grado') + 1, cols.pop(cols.index('grado_original')))
            df = df[cols]
        except ValueError: # En caso de que 'grado' no esté presente por algún error
            pass

    return df


def standardize_languages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estandariza los idiomas, creando una columna para nivel de quechua.
    
    Args:
        df: DataFrame con columna de idiomas
        
    Returns:
        DataFrame con idiomas estandarizados
    """
    if "idiomas" not in df.columns:
        return df
    
    # Crear columna para nivel de quechua
    df["quechua"] = "No lo hablo"
    
    # Función para detectar nivel de quechua
    def detect_quechua(idioms_str):
        if pd.isna(idioms_str) or not isinstance(idioms_str, str):
            return "No lo hablo"
            
        idioms_lower = idioms_str.lower()
        
        # Detectar si habla quechua y posible nivel
        if "quechua" in idioms_lower or "kichwa" in idioms_lower or "qheswa" in idioms_lower:
            # Intentar detectar nivel
            if any(nivel in idioms_lower for nivel in ["avanzado", "fluido", "nativo"]):
                return "Nivel avanzado"
            elif any(nivel in idioms_lower for nivel in ["intermedio", "regular"]):
                return "Nivel intermedio"
            elif any(nivel in idioms_lower for nivel in ["básico", "basico", "poco"]):
                return "Nivel básico"
            else:
                # Si solo menciona quechua sin nivel, asumir nivel básico
                return "Nivel básico"
                
        return "No lo hablo"
    
    # Aplicar estandarización
    df["quechua"] = df["idiomas"].apply(detect_quechua)
    
    return df


if __name__ == "__main__":
    # Esto permite probar el tab individualmente
    ruru_transform_tab() 