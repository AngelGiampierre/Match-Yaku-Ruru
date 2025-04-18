"""
Componentes de UI para selección de elementos.

Contiene widgets reutilizables para la selección de columnas, filtros, etc.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
import re


def detect_important_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Detecta automáticamente columnas importantes en un DataFrame.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con categorías de columnas y sus nombres detectados
    """
    if df is None or df.empty:
        return {}
    
    # Convertir nombres de columnas a minúsculas para comparación
    cols_lower = {col.lower(): col for col in df.columns}
    
    # Patrones para diferentes tipos de columnas
    patterns = {
        "id": [r'\bid\b', r'código', r'codigo', r'number'],
        "nombre": [r'nombre', r'name', r'apellido', r'\bnom\b'],
        "dni": [r'dni', r'documento', r'document', r'identificacion', r'identificación', r'cedula'],
        "email": [r'email', r'correo', r'e-mail', r'mail'],
        "telefono": [r'tel[eé]fono', r'phone', r'celular', r'movil', r'móvil'],
        "area": [r'[aá]rea', r'campo', r'especialidad', r'sector'],
        "grado": [r'grado', r'nivel', r'grade', r'level', r'curso', r'ciclo'],
        "horario": [r'horario', r'hora', r'time', r'disponibilidad', r'schedule'],
        "curso": [r'curso', r'materia', r'asignatura', r'taller', r'course', r'subject'],
        "preferencia": [r'preferencia', r'preference', r'interes', r'interés', r'eleccion', r'elección']
    }
    
    # Buscar coincidencias
    detected = {category: [] for category in patterns.keys()}
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            for col_lower, original_col in cols_lower.items():
                if re.search(pattern, col_lower):
                    if original_col not in detected[category]:
                        detected[category].append(original_col)
    
    # Filtrar categorías vacías
    return {k: v for k, v in detected.items() if v}


def select_columns(
    df, 
    key_prefix="", 
    preselect_important=False,
    max_rows_to_show=10
):
    """
    Permite al usuario seleccionar columnas de un DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos.
        key_prefix (str): Prefijo para las claves de Streamlit.
        preselect_important (bool): Si se deben preseleccionar columnas importantes.
        max_rows_to_show (int): Número máximo de filas a mostrar en la vista previa.
        
    Returns:
        tuple: (columnas seleccionadas, DataFrame filtrado)
    """
    if df is None or df.empty:
        st.warning("No hay datos para seleccionar columnas")
        return None, None
    
    st.write("### Selección de columnas")
    
    # Verificar columnas duplicadas
    duplicated_cols = df.columns[df.columns.duplicated()].tolist()
    if duplicated_cols:
        st.warning(f"⚠️ Se encontraron columnas duplicadas en el archivo: {', '.join(duplicated_cols)}")
        st.info("Las columnas duplicadas serán renombradas para evitar problemas.")
        
        # Renombrar columnas duplicadas
        new_columns = []
        column_counts = {}
        
        for col in df.columns:
            if col in column_counts:
                column_counts[col] += 1
                new_col = f"{col}_{column_counts[col]}"
                new_columns.append(new_col)
            else:
                column_counts[col] = 0
                new_columns.append(col)
        
        df.columns = new_columns
    
    # Mostrar vista previa del DataFrame
    st.write("#### Vista previa de los datos:")
    st.dataframe(df.head(max_rows_to_show), use_container_width=True)
    
    # Seleccionar columnas
    all_columns = df.columns.tolist()
    
    # Preseleccionar columnas importantes si se solicita
    default_selected = []
    if preselect_important:
        important_patterns = [
            'dni', 'nombre', 'apellido', 'email', 'correo', 'teléfono', 'telefono', 
            'celular', 'grado', 'nivel', 'curso', 'taller', 'area', 'área', 'carrera',
            'disponibilidad', 'horario'
        ]
        
        for col in all_columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in important_patterns):
                default_selected.append(col)
    
    # Checkbox para seleccionar todas las columnas
    select_all = st.checkbox(
        "Seleccionar todas las columnas", 
        value=False, 
        key=f"{key_prefix}_select_all"
    )
    
    if select_all:
        selected_columns = all_columns
    else:
        # Dividir las columnas en columnas para facilitar la selección
        num_cols = 3
        col_lists = [[] for _ in range(num_cols)]
        
        for i, col in enumerate(all_columns):
            col_lists[i % num_cols].append(col)
        
        st.write("#### Selecciona las columnas que deseas conservar:")
        cols = st.columns(num_cols)
        
        selected_columns = []
        for i, col_list in enumerate(col_lists):
            with cols[i]:
                for col in col_list:
                    is_selected = st.checkbox(
                        col, 
                        value=col in default_selected if default_selected else False,
                        key=f"{key_prefix}_{col}"
                    )
                    if is_selected:
                        selected_columns.append(col)
    
    # Filtrar DataFrame
    if selected_columns:
        filtered_df = df[selected_columns].copy()
        
        st.write("#### Vista previa de las columnas seleccionadas:")
        st.dataframe(filtered_df.head(max_rows_to_show), use_container_width=True)
        
        st.success(f"✅ Se han seleccionado {len(selected_columns)} columnas de {len(all_columns)}")
        
        return selected_columns, filtered_df
    else:
        st.warning("No se ha seleccionado ninguna columna")
        return None, None


def select_id_column(
    df: pd.DataFrame,
    column_type: str = "DNI/Documento",
    key: str = "id_column"
) -> str:
    """
    Crea una interfaz para seleccionar una columna de identificación.
    
    Args:
        df: DataFrame del cual seleccionar la columna
        column_type: Tipo de columna a seleccionar (DNI, Email, etc.)
        key: Clave única para el componente
        
    Returns:
        Nombre de la columna seleccionada o None
    """
    if df is None or df.empty:
        return None
    
    # Detectar posibles columnas según el tipo
    potential_cols = []
    
    if column_type == "DNI/Documento":
        # Detectar columnas de DNI/documento
        important_cols = detect_important_columns(df)
        if "dni" in important_cols:
            potential_cols = important_cols["dni"]
    
    elif column_type == "Email":
        # Detectar columnas de email
        important_cols = detect_important_columns(df)
        if "email" in important_cols:
            potential_cols = important_cols["email"]
    
    elif column_type == "Nombre":
        # Detectar columnas de nombre
        important_cols = detect_important_columns(df)
        if "nombre" in important_cols:
            potential_cols = important_cols["nombre"]
    
    # Si no se detectaron columnas, mostrar todas
    if not potential_cols:
        potential_cols = df.columns.tolist()
    
    # Selector de columna
    selected_column = st.selectbox(
        f"Selecciona la columna de {column_type}:",
        options=potential_cols,
        key=key
    )
    
    return selected_column 