import streamlit as st
import pandas as pd
import sys
import os

# Importamos las funciones de utilidad
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from utils.data_processors import standardize_dni

def handle_dni_update(filtered_df, index_to_fix, dni_column, new_value):
    """
    Función específica para manejar la actualización de DNIs y asegurar que se guarde en la sesión.
    
    Args:
        filtered_df (pd.DataFrame): DataFrame con los datos
        index_to_fix (int): Índice del registro a modificar
        dni_column (str): Nombre de la columna de DNI
        new_value (str): Nuevo valor de DNI
        
    Returns:
        pd.DataFrame: DataFrame actualizado
    """
    # Guardar el valor actual para mostrar el cambio
    current_value = filtered_df.loc[index_to_fix, dni_column]
    
    # Aplicar la estandarización solo si es necesario
    new_valid_value = standardize_dni(new_value)
    if "ERROR" in new_valid_value:
        new_valid_value = new_value  # Si sigue siendo inválido, usar el valor ingresado
    
    # Actualizar tanto la columna original como la validada
    filtered_df.loc[index_to_fix, dni_column] = new_valid_value
    filtered_df.loc[index_to_fix, 'DNI_Validado'] = new_valid_value
    
    # Guardar cambios en la sesión inmediatamente
    st.session_state.processed_data = filtered_df.copy()
    
    # Guardar una marca de que se ha realizado una edición
    st.session_state.last_action = f"edit_dni_{index_to_fix}"
    
    # Mostrar información del cambio
    st.info(f"🔄 DNI actualizado: '{current_value}' → '{new_valid_value}'")
    
    return filtered_df

def handle_sort_dataframe(df, sort_column, ascending=True, sort_name=""):
    """
    Función específica para manejar el ordenamiento y asegurar que se guarde en la sesión.
    
    Args:
        df (pd.DataFrame): DataFrame a ordenar
        sort_column (str): Columna por la que ordenar
        ascending (bool): Si el orden es ascendente o descendente
        sort_name (str): Nombre descriptivo del tipo de ordenamiento
        
    Returns:
        pd.DataFrame: DataFrame ordenado
    """
    # Ordenar el DataFrame
    df_sorted = df.sort_values(by=sort_column, ascending=ascending)
    
    # Guardar inmediatamente en la sesión
    st.session_state.processed_data = df_sorted.copy()
    
    # Guardar una marca de que se ha realizado un ordenamiento
    st.session_state.last_action = f"sort_{sort_column}"
    
    # Información descriptiva
    direction = "ascendente" if ascending else "descendente"
    st.info(f"📊 Ordenando {len(df)} registros por '{sort_column}' ({direction})")
    
    return df_sorted 