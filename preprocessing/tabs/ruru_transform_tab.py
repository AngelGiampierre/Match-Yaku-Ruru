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
            "grado", "idiomas"
        ]
        
        # También necesitamos columnas de horarios
        dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
        turnos = ["mañana", "tarde", "noche"]
        
        horario_columns = [f"{dia}_{turno}" for dia in dias for turno in turnos]
        
        missing_columns = [col for col in required_columns if col not in ruru_df.columns]
        missing_horarios = [col for col in horario_columns if col not in ruru_df.columns]
        
        if missing_columns:
            st.error(f"❌ El archivo no contiene todas las columnas necesarias. Faltan: {', '.join(missing_columns)}")
            st.info("Por favor, primero estandariza las columnas del archivo en la pestaña 'Estandarización de Rurus'")
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
                    processed_df = standardize_grades(processed_df)
                    st.success("✅ Grados estandarizados correctamente")
                
                if "idioma" in selected_transformations:
                    processed_df = standardize_languages(processed_df)
                    st.success("✅ Idiomas estandarizados correctamente")
                
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
            st.success("✅ Archivo cargado correctamente con todas las columnas necesarias")
            
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
                    processed_df = standardize_grades(processed_df)
                    st.success("✅ Grados estandarizados correctamente")
                
                if "idioma" in selected_transformations:
                    processed_df = standardize_languages(processed_df)
                    st.success("✅ Idiomas estandarizados correctamente")
                
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
            
            # Procesar cada turno
            for turno_col in turnos_existentes:
                if turno_col in df.columns:
                    # Mostrar los valores únicos para debugging
                    # st.write(f"Valores únicos en {turno_col}: {df[turno_col].unique()}")
                    
                    # Convertir la columna a un formato que podamos procesar
                    # Primero asegurar que tenemos valores numéricos o strings comparables
                    df[turno_col] = df[turno_col].fillna(0)
                    
                    # Intentar convertir a numérico (para manejar strings, floats, ints, etc.)
                    try:
                        df[turno_col] = pd.to_numeric(df[turno_col], errors='coerce').fillna(0)
                    except:
                        # Si falla, asegurar que tenemos strings
                        df[turno_col] = df[turno_col].astype(str)
                    
                    # Ahora verificar si hay disponibilidad (valor 1 como número o string)
                    # Para valores numéricos
                    if pd.api.types.is_numeric_dtype(df[turno_col]):
                        disponible_mask = df[turno_col] == 1
                    else:
                        # Para strings, verificar "1" o valores que indiquen disponibilidad
                        disponible_mask = df[turno_col].isin(["1", "true", "True", "yes", "Yes", "disponible", "Disponible"])
                    
                    # Donde hay disponibilidad y no hay valor previo
                    mascara = disponible_mask & (df[col_horario] == "")
                    df.loc[mascara, col_horario] = formato_turnos.get(turno_col, "")
                    
                    # Si ya hay un valor, añadir con coma
                    mascara2 = disponible_mask & (df[col_horario] != "")
                    df.loc[mascara2, col_horario] = df.loc[mascara2, col_horario] + ", " + formato_turnos.get(turno_col, "")
            
            # Donde no haya disponibilidad, poner "No disponible"
            df.loc[df[col_horario] == "", col_horario] = "No disponible"
            
            # Eliminar columnas de turnos individuales
            df = df.drop(columns=turnos_existentes, errors='ignore')
    
    return df


def standardize_grades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estandariza los grados escolares para coincidir con el formato de Yakus.
    
    Args:
        df: DataFrame con columna de grados
        
    Returns:
        DataFrame con grados estandarizados
    """
    if "grado" not in df.columns:
        return df
    
    # Mapa de estandarización para grados
    # Cada patrón se mapea a un formato estandarizado
    grado_map = {
        # Tercero de primaria (todas las variantes)
        r"(?i)terc[eoa]r[oa]?\s*(?:grado)?(?:\s*de)?\s*primaria": "Primaria (3° y 4° grado)",
        r"(?i)3\s*(?:ro|°)?\s*(?:de)?\s*primaria": "Primaria (3° y 4° grado)",
        r"(?i)3\s*(?:p|primaria)": "Primaria (3° y 4° grado)",
        r"^3$|^3ro$": "Primaria (3° y 4° grado)",
        
        # Cuarto de primaria
        r"(?i)cuart[oa]\s*(?:grado)?(?:\s*de)?\s*primaria": "Primaria (3° y 4° grado)",
        r"(?i)4\s*(?:to|°)?\s*(?:de)?\s*primaria": "Primaria (3° y 4° grado)",
        r"(?i)4\s*(?:p|primaria)": "Primaria (3° y 4° grado)",
        r"^4$|^4to$": "Primaria (3° y 4° grado)",
        
        # Quinto de primaria
        r"(?i)quint[oa]\s*(?:grado)?(?:\s*de)?\s*primaria": "Primaria (5° y 6° grado)",
        r"(?i)5\s*(?:to|°)?\s*(?:de)?\s*primaria": "Primaria (5° y 6° grado)",
        r"(?i)5\s*(?:p|primaria)": "Primaria (5° y 6° grado)",
        r"^5$|^5to$|^5P$": "Primaria (5° y 6° grado)",
        
        # Sexto de primaria
        r"(?i)sext[oa]\s*(?:grado)?(?:\s*de)?\s*primaria": "Primaria (5° y 6° grado)",
        r"(?i)6\s*(?:to|°)?\s*(?:de)?\s*primaria": "Primaria (5° y 6° grado)",
        r"(?i)6\s*(?:p|primaria)": "Primaria (5° y 6° grado)",
        r"^6$|^6to$|^6TO$|^6p$": "Primaria (5° y 6° grado)",
        
        # Primero de secundaria
        r"(?i)primer[oa]\s*(?:grado)?(?:\s*de)?\s*secundaria": "Secundaria (1°, 2° y 3° grado)",
        r"(?i)1\s*(?:ro|°)?\s*(?:de)?\s*secundaria": "Secundaria (1°, 2° y 3° grado)",
        r"^1$|^1ro$": "Secundaria (1°, 2° y 3° grado)",
        
        # Segundo de secundaria
        r"(?i)segund[oa]\s*(?:grado)?(?:\s*de)?\s*secundaria": "Secundaria (1°, 2° y 3° grado)",
        r"(?i)2\s*(?:do|°)?\s*(?:de)?\s*secundaria": "Secundaria (1°, 2° y 3° grado)",
        r"^2$|^2do$": "Secundaria (1°, 2° y 3° grado)",
        
        # Tercero de secundaria
        r"(?i)tercer[oa]\s*(?:grado)?(?:\s*de)?\s*secundaria": "Secundaria (1°, 2° y 3° grado)",
        r"(?i)3\s*(?:ro|°)?\s*(?:de)?\s*secundaria": "Secundaria (1°, 2° y 3° grado)",
        
        # Primero y segundo de primaria (no tan común, pero por si acaso)
        r"(?i)primer[oa]\s*(?:grado)?(?:\s*de)?\s*primaria": "Primaria (1° y 2° grado)",
        r"(?i)1\s*(?:ro|°)?\s*(?:de)?\s*primaria": "Primaria (1° y 2° grado)",
        r"(?i)segund[oa]\s*(?:grado)?(?:\s*de)?\s*primaria": "Primaria (1° y 2° grado)",
        r"(?i)2\s*(?:do|°)?\s*(?:de)?\s*primaria": "Primaria (1° y 2° grado)"
    }
    
    # Función para aplicar la estandarización
    def standardize_grade(grade_str):
        if pd.isna(grade_str) or not isinstance(grade_str, str):
            return "No especificado"
            
        # Intentar con cada patrón
        for pattern, standard_grade in grado_map.items():
            if re.search(pattern, grade_str.strip()):
                return standard_grade
                
        # Si no coincide con ningún patrón
        return grade_str
    
    # Aplicar estandarización
    df["grado"] = df["grado"].apply(standardize_grade)
    
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