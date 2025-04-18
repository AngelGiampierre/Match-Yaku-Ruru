"""
Componentes de UI para mostrar información sobre los datos.

Contiene widgets reutilizables para visualizar estadísticas, vistas previas, etc.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


def preview_dataframe(
    df: pd.DataFrame,
    rows: int = 5,
    title: str = "Vista previa de los datos",
    expanded: bool = True,
    key: str = "preview"
) -> None:
    """
    Muestra una vista previa de un DataFrame.
    
    Args:
        df: DataFrame a mostrar
        rows: Número de filas a mostrar
        title: Título del expander
        expanded: Si el expander debe estar expandido por defecto
        key: Clave única para el componente
    """
    if df is None or df.empty:
        st.warning("No hay datos para mostrar")
        return
    
    with st.expander(title, expanded=expanded):
        st.dataframe(df.head(rows))


def show_column_statistics(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    show_missing: bool = True,
    show_unique: bool = True,
    show_stats: bool = True,
    key: str = "stats"
) -> None:
    """
    Muestra estadísticas sobre las columnas de un DataFrame.
    
    Args:
        df: DataFrame a analizar
        columns: Lista de columnas a analizar (None para todas)
        show_missing: Si debe mostrar valores faltantes
        show_unique: Si debe mostrar valores únicos
        show_stats: Si debe mostrar estadísticas numéricas
        key: Clave única para el componente
    """
    if df is None or df.empty:
        st.warning("No hay datos para analizar")
        return
    
    # Si no se especifican columnas, usar todas
    if columns is None:
        columns = df.columns.tolist()
    
    with st.expander("Estadísticas de las columnas", expanded=True):
        # Calcular estadísticas
        total_rows = len(df)
        
        if show_missing:
            st.write("#### Valores faltantes")
            missing_data = []
            
            for col in columns:
                missing_count = df[col].isna().sum()
                missing_percent = (missing_count / total_rows) * 100
                
                missing_data.append({
                    "Columna": col,
                    "Valores faltantes": missing_count,
                    "% faltantes": f"{missing_percent:.2f}%"
                })
            
            # Mostrar tabla de valores faltantes
            missing_df = pd.DataFrame(missing_data)
            st.dataframe(missing_df)
        
        if show_unique:
            st.write("#### Valores únicos")
            unique_data = []
            
            for col in columns:
                unique_count = df[col].nunique()
                unique_percent = (unique_count / total_rows) * 100
                
                unique_data.append({
                    "Columna": col,
                    "Valores únicos": unique_count,
                    "% únicos": f"{unique_percent:.2f}%"
                })
            
            # Mostrar tabla de valores únicos
            unique_df = pd.DataFrame(unique_data)
            st.dataframe(unique_df)
        
        if show_stats:
            st.write("#### Estadísticas numéricas")
            
            # Filtrar solo columnas numéricas
            numeric_cols = df[columns].select_dtypes(include=np.number).columns.tolist()
            
            if numeric_cols:
                # Calcular estadísticas básicas
                stats_df = df[numeric_cols].describe().T
                st.dataframe(stats_df)
            else:
                st.info("No hay columnas numéricas para mostrar estadísticas")


def show_editing_interface(
    df: pd.DataFrame, 
    row_index: int,
    column_name: str,
    key_prefix: str = "edit"
) -> Any:
    """
    Muestra una interfaz para editar un valor específico en un DataFrame.
    
    Args:
        df: DataFrame que contiene el valor a editar
        row_index: Índice de la fila a editar
        column_name: Nombre de la columna a editar
        key_prefix: Prefijo para las claves de los componentes
        
    Returns:
        Nuevo valor ingresado por el usuario
    """
    if df is None or row_index >= len(df) or column_name not in df.columns:
        st.error("No se puede editar: datos incorrectos")
        return None
    
    # Obtener el valor actual
    current_value = df.at[row_index, column_name]
    
    # Mostrar información de contexto
    st.write(f"**Fila:** {row_index + 1}")
    
    # Mostrar el resto de la fila para contexto
    context_data = {}
    for col in df.columns:
        context_data[col] = df.at[row_index, col]
    
    # Crear un DataFrame de una sola fila para mostrar el contexto
    context_df = pd.DataFrame([context_data])
    st.dataframe(context_df)
    
    # Determinar el tipo de entrada según el tipo de datos
    value_type = df[column_name].dtype
    
    st.write(f"**Columna a editar:** {column_name}")
    st.write(f"**Valor actual:** {current_value}")
    
    # Crear el input adecuado según el tipo de datos
    if pd.api.types.is_numeric_dtype(value_type):
        # Input numérico
        if pd.api.types.is_integer_dtype(value_type):
            new_value = st.number_input(
                "Nuevo valor:",
                value=int(current_value) if pd.notna(current_value) else 0,
                key=f"{key_prefix}_{row_index}_{column_name}"
            )
        else:
            new_value = st.number_input(
                "Nuevo valor:",
                value=float(current_value) if pd.notna(current_value) else 0.0,
                key=f"{key_prefix}_{row_index}_{column_name}"
            )
    elif pd.api.types.is_bool_dtype(value_type):
        # Checkbox para booleanos
        new_value = st.checkbox(
            "Nuevo valor:",
            value=bool(current_value) if pd.notna(current_value) else False,
            key=f"{key_prefix}_{row_index}_{column_name}"
        )
    else:
        # Input de texto para strings y otros tipos
        new_value = st.text_input(
            "Nuevo valor:",
            value=str(current_value) if pd.notna(current_value) else "",
            key=f"{key_prefix}_{row_index}_{column_name}"
        )
    
    return new_value 