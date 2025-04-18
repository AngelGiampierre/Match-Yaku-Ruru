"""
Funciones para filtrar datos.

Este módulo contiene funciones para filtrar DataFrames por diferentes criterios
como área, DNI, correo electrónico, etc.
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
import re


def identify_area_column(df: pd.DataFrame) -> Optional[str]:
    """
    Identifica la columna que probablemente contiene información de área.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Nombre de la columna de área o None si no se encuentra
    """
    if df is None or df.empty:
        return None
    
    # Patrones comunes para nombres de columnas de área
    area_patterns = [
        r'área', r'area', r'especialidad', r'campo', 
        r'sector', r'departamento', r'división', r'division'
    ]
    
    # Buscar en nombres de columnas
    for pattern in area_patterns:
        for col in df.columns:
            if re.search(pattern, col.lower()):
                return col
    
    return None


def get_unique_areas(df: pd.DataFrame, area_column: str) -> List[str]:
    """
    Obtiene las áreas únicas presentes en el DataFrame.
    
    Args:
        df: DataFrame a analizar
        area_column: Nombre de la columna que contiene las áreas
        
    Returns:
        Lista de áreas únicas ordenadas alfabéticamente
    """
    if df is None or df.empty or area_column not in df.columns:
        return []
    
    # Obtener valores únicos no nulos y ordenar
    areas = sorted(df[area_column].dropna().unique().tolist())
    return areas


def filter_by_area(df: pd.DataFrame, area_column: str, selected_area: str) -> pd.DataFrame:
    """
    Filtra el DataFrame por un área específica.
    
    Args:
        df: DataFrame a filtrar
        area_column: Nombre de la columna que contiene las áreas
        selected_area: Área seleccionada para filtrar
        
    Returns:
        DataFrame filtrado
    """
    if df is None or df.empty or area_column not in df.columns:
        return df
    
    # Si selected_area es None o está vacío, devolver todo el DataFrame
    if not selected_area:
        return df
        
    # Filtrar por área
    return df[df[area_column] == selected_area].reset_index(drop=True)


def identify_id_column(df: pd.DataFrame, id_type: str = "dni") -> Optional[str]:
    """
    Identifica la columna que probablemente contiene el tipo de ID especificado.
    
    Args:
        df: DataFrame a analizar
        id_type: Tipo de ID a buscar ('dni', 'email', 'nombre')
        
    Returns:
        Nombre de la columna o None si no se encuentra
    """
    if df is None or df.empty:
        return None
    
    # Patrones según el tipo de ID
    patterns = {
        'dni': [r'dni', r'documento', r'document', r'identificación', r'identificacion', r'id'],
        'email': [r'correo', r'email', r'e-mail', r'mail'],
        'nombre': [r'nombre', r'name', r'apellido', r'apel', r'nombres']
    }
    
    # Obtener patrones para el tipo de ID especificado
    id_patterns = patterns.get(id_type.lower(), [])
    
    # Buscar en nombres de columnas
    for pattern in id_patterns:
        for col in df.columns:
            if re.search(pattern, col.lower()):
                return col
    
    return None


def load_and_parse_selection_list(
    selection_df: pd.DataFrame, 
    id_column: str
) -> List[str]:
    """
    Carga y procesa una lista de selección de un DataFrame.
    
    Args:
        selection_df: DataFrame que contiene la lista de selección
        id_column: Nombre de la columna que contiene los IDs
        
    Returns:
        Lista de IDs únicos
    """
    if selection_df is None or selection_df.empty or id_column not in selection_df.columns:
        return []
    
    # Extraer valores únicos no nulos
    ids = selection_df[id_column].dropna().astype(str).unique().tolist()
    
    # Limpiar IDs (eliminar espacios y caracteres especiales)
    cleaned_ids = [re.sub(r'\s+', '', id_val) for id_val in ids]
    
    return cleaned_ids


def filter_by_ids(df: pd.DataFrame, id_column: str, id_list: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """
    Filtra el DataFrame por una lista de IDs.
    
    Args:
        df: DataFrame a filtrar
        id_column: Nombre de la columna que contiene los IDs
        id_list: Lista de IDs para filtrar
        
    Returns:
        Tupla de (DataFrame filtrado, IDs no encontrados)
    """
    if df is None or df.empty or id_column not in df.columns or not id_list:
        return df, id_list
    
    # Convertir columna a string para comparación
    df_copy = df.copy()
    df_copy[id_column] = df_copy[id_column].astype(str)
    
    # Limpiar IDs en el DataFrame (eliminar espacios)
    df_copy[id_column] = df_copy[id_column].apply(lambda x: re.sub(r'\s+', '', x) if pd.notna(x) else x)
    
    # Filtrar por IDs
    filtered_df = df_copy[df_copy[id_column].isin(id_list)]
    
    # Identificar IDs no encontrados
    found_ids = filtered_df[id_column].unique().tolist()
    not_found_ids = [id_val for id_val in id_list if id_val not in found_ids]
    
    return filtered_df.reset_index(drop=True), not_found_ids


def combine_filters(
    df: pd.DataFrame, 
    area_column: Optional[str], 
    selected_area: Optional[str],
    id_column: Optional[str], 
    id_list: Optional[List[str]]
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Aplica filtros combinados por área y lista de IDs.
    
    Args:
        df: DataFrame a filtrar
        area_column: Nombre de la columna de área (None para no filtrar por área)
        selected_area: Área seleccionada (None para no filtrar por área)
        id_column: Nombre de la columna de ID (None para no filtrar por ID)
        id_list: Lista de IDs (None para no filtrar por ID)
        
    Returns:
        Tupla de (DataFrame filtrado, IDs no encontrados)
    """
    if df is None or df.empty:
        return df, []
    
    filtered_df = df.copy()
    not_found_ids = []
    
    # Filtrar por área si se especifica
    if area_column and selected_area and selected_area != "Todas las áreas":
        filtered_df = filter_by_area(filtered_df, area_column, selected_area)
    
    # Filtrar por IDs si se especifica
    if id_column and id_list:
        filtered_df, not_found_ids = filter_by_ids(filtered_df, id_column, id_list)
    
    return filtered_df, not_found_ids 