"""
Funciones para manipular columnas de datos.

Este módulo contiene funciones para modificar, actualizar y transformar
columnas en DataFrames.
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union


def update_value(
    df: pd.DataFrame,
    row_index: int,
    column_name: str,
    new_value: Any
) -> Tuple[pd.DataFrame, bool]:
    """
    Actualiza un valor específico en un DataFrame.
    
    Args:
        df: DataFrame a modificar
        row_index: Índice de la fila a modificar
        column_name: Nombre de la columna a modificar
        new_value: Nuevo valor a asignar
        
    Returns:
        Tupla de (DataFrame modificado, éxito)
    """
    # Verificar si el índice y la columna existen
    if df is None or row_index >= len(df) or column_name not in df.columns:
        return df, False
    
    # Crear una copia para no modificar el original
    df_copy = df.copy()
    
    try:
        # Actualizar el valor
        df_copy.at[row_index, column_name] = new_value
        return df_copy, True
    except Exception as e:
        print(f"Error al actualizar valor: {str(e)}")
        return df, False


def update_multiple_values(
    df: pd.DataFrame,
    updates: List[Dict[str, Any]]
) -> Tuple[pd.DataFrame, int]:
    """
    Actualiza múltiples valores en un DataFrame.
    
    Args:
        df: DataFrame a modificar
        updates: Lista de diccionarios con actualizaciones
                 Cada diccionario debe tener 'row_index', 'column_name' y 'new_value'
        
    Returns:
        Tupla de (DataFrame modificado, número de actualizaciones exitosas)
    """
    if df is None or not updates:
        return df, 0
    
    # Crear una copia para no modificar el original
    df_copy = df.copy()
    successful_updates = 0
    
    for update in updates:
        try:
            # Verificar que tenga los campos necesarios
            if 'row_index' not in update or 'column_name' not in update or 'new_value' not in update:
                continue
                
            row_index = update['row_index']
            column_name = update['column_name']
            new_value = update['new_value']
            
            # Verificar que el índice y la columna existan
            if row_index >= len(df_copy) or column_name not in df_copy.columns:
                continue
                
            # Actualizar el valor
            df_copy.at[row_index, column_name] = new_value
            successful_updates += 1
        except Exception as e:
            print(f"Error al actualizar valor: {str(e)}")
            continue
    
    return df_copy, successful_updates


def standardize_column_values(
    df: pd.DataFrame,
    column_name: str,
    standardize_function: callable
) -> Tuple[pd.DataFrame, int]:
    """
    Estandariza los valores de una columna aplicando una función.
    
    Args:
        df: DataFrame a modificar
        column_name: Nombre de la columna a estandarizar
        standardize_function: Función que recibe un valor y devuelve su versión estandarizada
        
    Returns:
        Tupla de (DataFrame modificado, número de modificaciones)
    """
    if df is None or column_name not in df.columns:
        return df, 0
        
    # Crear una copia para no modificar el original
    df_copy = df.copy()
    original_values = df_copy[column_name].copy()
    
    # Aplicar la función de estandarización
    df_copy[column_name] = df_copy[column_name].apply(standardize_function)
    
    # Contar cambios
    changes = (original_values != df_copy[column_name]).sum()
    
    return df_copy, changes


def standardize_dni(value: Any) -> str:
    """
    Estandariza un DNI: elimina espacios y caracteres especiales.
    
    Args:
        value: Valor a estandarizar
        
    Returns:
        DNI estandarizado
    """
    if pd.isna(value):
        return value
        
    # Convertir a string
    value_str = str(value).strip()
    
    # Eliminar espacios y caracteres especiales
    return re.sub(r'[^a-zA-Z0-9]', '', value_str)


def standardize_email(value: Any) -> str:
    """
    Estandariza un correo electrónico: convierte a minúsculas y elimina espacios.
    
    Args:
        value: Valor a estandarizar
        
    Returns:
        Correo estandarizado
    """
    if pd.isna(value):
        return value
        
    # Convertir a string, minúsculas y eliminar espacios
    value_str = str(value).strip().lower()
    
    return value_str


def filter_rows_by_column_values(
    df: pd.DataFrame,
    column_name: str,
    valid_values: List[Any]
) -> pd.DataFrame:
    """
    Filtra filas basado en valores válidos de una columna.
    
    Args:
        df: DataFrame a filtrar
        column_name: Nombre de la columna por la que filtrar
        valid_values: Lista de valores válidos
        
    Returns:
        DataFrame filtrado
    """
    if df is None or column_name not in df.columns:
        return df
        
    return df[df[column_name].isin(valid_values)].copy()


import re  # Añadir esta importación para la función standardize_dni 