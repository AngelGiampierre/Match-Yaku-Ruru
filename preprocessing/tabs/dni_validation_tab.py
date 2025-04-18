"""
Tab para la validación y edición de DNIs y correos electrónicos.

Este tab permite cargar un archivo, seleccionar una columna de DNI o correo,
validar los valores y corregir los que sean inválidos.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

# Importamos componentes de UI
from ..ui.file_uploaders import upload_excel_file, show_download_buttons
from ..ui.selectors import select_id_column
from ..ui.displays import preview_dataframe, show_editing_interface

# Importamos funciones de validación
from ..data.validators import (
    validate_dni, 
    validate_email, 
    validate_column, 
    get_validation_summary,
    identify_potential_dni_columns,
    identify_potential_email_columns
)

# Importamos funciones para manipular columnas
from ..data.column_handlers import (
    update_value,
    update_multiple_values,
    standardize_column_values,
    standardize_dni,
    standardize_email
)

# Importamos utilidades
from ..utils.file_io import save_temp_file
from ..utils import save_data, load_data


def dni_validation_tab():
    """
    Tab para validar y corregir DNIs o correos electrónicos.
    """
    st.header("Validación de DNIs / Correos")
    st.write("""
    Esta sección te permite cargar un archivo Excel o CSV, seleccionar una columna 
    de DNI o correo electrónico, validar los valores y corregir los que sean inválidos.
    """)
    
    # Inicializar variables
    df = None
    file_name = None
    validation_results = None
    column_name = None
    
    # Paso 1: Cargar archivo
    st.subheader("Paso 1: Cargar archivo")
    st.write("Carga un archivo Excel o CSV con los datos a validar:")
    
    df, file_name, success = upload_excel_file(
        key="dni_validation_upload",
        label="Cargar archivo Excel o CSV",
        help_text="Selecciona un archivo en formato Excel (.xlsx, .xls) o CSV"
    )
    
    if success and df is not None:
        # Paso 2: Seleccionar tipo de validación y columna
        st.subheader("Paso 2: Seleccionar tipo de validación")
        
        # Tipo de validación
        validation_type = st.radio(
            "¿Qué tipo de datos deseas validar?",
            options=["DNI/Documento", "Correo electrónico"],
            horizontal=True,
            key="validation_type"
        )
        
        # Detectar automáticamente columnas potenciales
        potential_columns = []
        
        if validation_type == "DNI/Documento":
            potential_columns = identify_potential_dni_columns(df)
            validator_function = validate_dni
            standardize_function = standardize_dni
        else:  # Correo electrónico
            potential_columns = identify_potential_email_columns(df)
            validator_function = validate_email
            standardize_function = standardize_email
        
        # Mensaje con columnas detectadas
        if potential_columns:
            st.success(f"✅ Se detectaron automáticamente columnas de {validation_type}: {', '.join(potential_columns)}")
        
        # Seleccionar columna
        column_name = select_id_column(
            df,
            column_type=validation_type,
            key="validation_column"
        )
        
        if column_name:
            # Opción para estandarizar automáticamente
            st.subheader("Paso 3: Estandarizar valores (opcional)")
            
            standardize = st.checkbox(
                f"Estandarizar valores automáticamente",
                value=True,
                help=f"Elimina espacios y caracteres especiales para {validation_type}",
                key="standardize_values"
            )
            
            if standardize:
                # Estandarizar valores
                df_standardized, changes = standardize_column_values(
                    df,
                    column_name,
                    standardize_function
                )
                
                if changes > 0:
                    st.success(f"✅ Se estandarizaron {changes} valores en la columna '{column_name}'")
                    df = df_standardized
                else:
                    st.info(f"ℹ️ Todos los valores ya estaban en formato estándar")
            
            # Paso 4: Validar valores
            st.subheader("Paso 4: Validar valores")
            
            if st.button("Validar valores", key="validate_button"):
                # Validar columna
                validation_results = validate_column(df, column_name, validator_function)
                
                # Guardar resultados en el estado de sesión
                save_data(validation_results, f"validation_results_{column_name}")
                
                # Mostrar resumen de validación
                summary = get_validation_summary(validation_results)
                
                st.write("#### Resumen de validación")
                
                # Mostrar métricas principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        label="Total de registros",
                        value=summary['total_records']
                    )
                with col2:
                    st.metric(
                        label="Registros válidos",
                        value=f"{summary['valid_records']} ({summary['valid_percent']:.1f}%)"
                    )
                with col3:
                    st.metric(
                        label="Registros inválidos",
                        value=f"{summary['invalid_records']} ({summary['invalid_percent']:.1f}%)"
                    )
                
                # Mostrar detalles de errores
                if summary['invalid_records'] > 0:
                    st.write("#### Tipos de errores encontrados")
                    for error, count in summary['error_counts'].items():
                        st.write(f"- **{error}**: {count} registros")
                    
                    # Mostrar registros inválidos
                    invalid_results = [r for r in validation_results if not r['is_valid']]
                    
                    st.write("#### Registros inválidos")
                    
                    # Crear DataFrame para mostrar los inválidos
                    invalid_data = []
                    for result in invalid_results:
                        row_data = df.iloc[result['row_index']].to_dict()
                        row_data['_index'] = result['row_index']
                        row_data['_error'] = result['error_message']
                        invalid_data.append(row_data)
                    
                    invalid_df = pd.DataFrame(invalid_data)
                    
                    # Reorganizar columnas para mostrar primero índice, error y columna validada
                    columns_order = ['_index', '_error', column_name]
                    remaining_cols = [col for col in invalid_df.columns if col not in columns_order]
                    invalid_df = invalid_df[columns_order + remaining_cols]
                    
                    # Mostrar DataFrame de inválidos
                    st.dataframe(invalid_df)
                    
                    # Paso 5: Corregir valores inválidos
                    st.subheader("Paso 5: Corregir valores inválidos")
                    
                    # Opción para editar valores individuales
                    st.write("#### Editar valores individuales")
                    
                    # Permitir seleccionar una fila para editar
                    row_indices = [r['row_index'] for r in invalid_results]
                    
                    if row_indices:
                        selected_index = st.selectbox(
                            "Selecciona una fila para editar:",
                            options=row_indices,
                            format_func=lambda x: f"Fila {x+1}: {df.iloc[x][column_name]}",
                            key="edit_row_index"
                        )
                        
                        # Interfaz para editar el valor
                        st.write("#### Editar valor")
                        new_value = show_editing_interface(
                            df,
                            selected_index,
                            column_name,
                            key_prefix="edit_dni"
                        )
                        
                        # Botón para actualizar
                        if st.button("Actualizar valor", key="update_value_button"):
                            # Actualizar el valor
                            df_updated, success = update_value(
                                df,
                                selected_index,
                                column_name,
                                new_value
                            )
                            
                            if success:
                                st.success(f"✅ Valor actualizado correctamente")
                                df = df_updated
                                
                                # Actualizar validación
                                validation_results = validate_column(df, column_name, validator_function)
                                save_data(validation_results, f"validation_results_{column_name}")
                            else:
                                st.error("❌ Error al actualizar el valor")
                else:
                    st.success("✅ Todos los valores son válidos. No se requieren correcciones.")
            
            # Si ya hay resultados de validación, cargarlos
            else:
                validation_results = load_data(f"validation_results_{column_name}")
            
            # Paso 6: Guardar datos corregidos
            if df is not None:
                st.subheader("Paso 6: Guardar resultados")
                
                # Opción para guardar temporalmente
                if st.button("Guardar datos corregidos temporalmente", key="save_temp_button"):
                    if file_name:
                        base_name = file_name.split('.')[0]  # Quitar extensión
                        temp_file_path = save_temp_file(df, f"{base_name}_corregido")
                        if temp_file_path:
                            st.success(f"✅ Datos guardados temporalmente para uso en otros tabs")
                
                # Botones para descargar
                st.write("#### Descargar archivo con datos corregidos")
                
                # Generar nombre base para el archivo
                base_filename = "datos_corregidos"
                if file_name:
                    base_name = file_name.split('.')[0]  # Quitar extensión
                    base_filename = f"{base_name}_corregidos"
                
                # Mostrar botones de descarga
                show_download_buttons(df, base_filename)
    
    # Mostrar instrucciones si no hay archivo cargado
    elif not success:
        st.info("👆 Carga un archivo para comenzar el proceso de validación.")


if __name__ == "__main__":
    # Esto permite probar el tab individualmente
    dni_validation_tab() 