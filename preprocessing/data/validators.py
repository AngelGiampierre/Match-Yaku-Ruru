"""
Funciones para validar datos.

Este módulo contiene funciones para validar diferentes tipos de datos
como DNIs, correos electrónicos, nombres, etc.
"""

import re
import pandas as pd
from typing import List, Dict, Tuple, Any, Optional
import numpy as np


def validate_dni(value: Any) -> Tuple[bool, Optional[str]]:
    """
    Valida si un valor tiene formato de DNI peruano (8 dígitos) o pasaporte/CE.
    
    Args:
        value: Valor a validar
        
    Returns:
        Tupla de (es_válido, mensaje_error)
    """
    # Si es NaN, no es válido
    if pd.isna(value):
        return False, "Valor vacío"
    
    # Convertir a string
    value_str = str(value).strip()
    
    # DNI peruano: 8 dígitos
    if re.match(r'^\d{8}$', value_str):
        return True, None
    
    # Carnet de extranjería: formato común CE + números
    if re.match(r'^[cC][eE]\d+$', value_str) or re.match(r'^[0-9]{9}$', value_str):
        return True, None
    
    # Pasaporte: alfanumérico, normalmente entre 6-12 caracteres
    if re.match(r'^[a-zA-Z0-9]{6,12}$', value_str):
        return True, None
    
    # Si no cumple con ningún formato, consideramos inválido
    return False, "Formato no reconocido"


def validate_email(value: Any) -> Tuple[bool, Optional[str]]:
    """
    Valida si un valor tiene formato de correo electrónico.
    
    Args:
        value: Valor a validar
        
    Returns:
        Tupla de (es_válido, mensaje_error)
    """
    # Si es NaN, no es válido
    if pd.isna(value):
        return False, "Valor vacío"
    
    # Convertir a string
    value_str = str(value).strip()
    
    # Validar usando expresión regular simple para emails
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value_str):
        return True, None
    
    return False, "Formato de correo electrónico inválido"


def validate_column(
    df: pd.DataFrame, 
    column_name: str, 
    validator_function: callable
) -> List[Dict[str, Any]]:
    """
    Valida todos los valores en una columna y devuelve los resultados.
    
    Args:
        df: DataFrame que contiene la columna
        column_name: Nombre de la columna a validar
        validator_function: Función de validación a aplicar
        
    Returns:
        Lista de diccionarios con resultados de validación por fila
    """
    if column_name not in df.columns:
        return []
    
    results = []
    
    for idx, value in enumerate(df[column_name]):
        is_valid, error_message = validator_function(value)
        
        # Crear diccionario con resultados de validación
        result = {
            'row_index': idx,
            'value': value,
            'is_valid': is_valid,
            'error_message': error_message
        }
        
        results.append(result)
    
    return results


def get_validation_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Genera un resumen de los resultados de validación.
    
    Args:
        results: Lista de resultados de validación
        
    Returns:
        Diccionario con estadísticas de validación
    """
    total_records = len(results)
    valid_records = sum(1 for r in results if r['is_valid'])
    invalid_records = total_records - valid_records
    
    # Calcular porcentajes
    valid_percent = (valid_records / total_records * 100) if total_records > 0 else 0
    invalid_percent = (invalid_records / total_records * 100) if total_records > 0 else 0
    
    # Agrupar por tipo de error
    error_counts = {}
    for result in results:
        if not result['is_valid'] and result['error_message']:
            error_counts[result['error_message']] = error_counts.get(result['error_message'], 0) + 1
    
    return {
        'total_records': total_records,
        'valid_records': valid_records,
        'invalid_records': invalid_records,
        'valid_percent': valid_percent,
        'invalid_percent': invalid_percent,
        'error_counts': error_counts
    }


def identify_potential_dni_columns(df: pd.DataFrame) -> List[str]:
    """
    Identifica columnas que probablemente contengan DNIs.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Lista de nombres de columnas que probablemente contienen DNIs
    """
    potential_columns = []
    
    for col in df.columns:
        # Verificar por nombre de columna
        if any(term in col.lower() for term in ['dni', 'documento', 'document', 'identidad', 'identificación']):
            potential_columns.append(col)
            continue
        
        # Si no encontramos por nombre, verificar contenido
        # Tomamos una muestra de valores no nulos
        sample = df[col].dropna().astype(str).head(10).tolist()
        
        if not sample:
            continue
        
        # Contar cuántos valores parecen DNIs (8 dígitos)
        dni_count = sum(1 for val in sample if re.match(r'^\d{8}$', val))
        
        # Si al menos el 50% parecen DNIs, consideramos que es una columna de DNI
        if dni_count >= len(sample) * 0.5:
            potential_columns.append(col)
    
    return potential_columns


def identify_potential_email_columns(df: pd.DataFrame) -> List[str]:
    """
    Identifica columnas que probablemente contengan correos electrónicos.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Lista de nombres de columnas que probablemente contienen correos
    """
    potential_columns = []
    
    for col in df.columns:
        # Verificar por nombre de columna
        if any(term in col.lower() for term in ['correo', 'email', 'mail', 'e-mail']):
            potential_columns.append(col)
            continue
        
        # Si no encontramos por nombre, verificar contenido
        # Tomamos una muestra de valores no nulos
        sample = df[col].dropna().astype(str).head(10).tolist()
        
        if not sample:
            continue
        
        # Contar cuántos valores parecen correos (contienen @ y .)
        email_count = sum(1 for val in sample if '@' in val and '.' in val)
        
        # Si al menos el 50% parecen correos, consideramos que es una columna de correo
        if email_count >= len(sample) * 0.5:
            potential_columns.append(col)
    
    return potential_columns 