import streamlit as st
import pandas as pd
import re
import sys
import os

# Importamos las funciones de utilidad
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from utils.data_processors import standardize_dni, validate_email, get_duplicated_dnis

def validate_dni_column(filtered_df, dni_column):
    """
    Valida el formato de DNI en una columna específica y muestra opciones para corrección.
    
    Args:
        filtered_df (pd.DataFrame): DataFrame a procesar
        dni_column (str): Nombre de la columna que contiene los DNIs
        
    Returns:
        pd.DataFrame: DataFrame actualizado
    """
    st.subheader("Limpieza de DNI/Pasaporte")
    
    if not dni_column:
        st.warning("⚠️ No se ha seleccionado una columna de DNI/Pasaporte.")
        return filtered_df
    
    # Convertir explícitamente a string la columna DNI para evitar problemas con PyArrow
    filtered_df[dni_column] = filtered_df[dni_column].astype(str)
    
    # Validar y estandarizar DNIs
    with st.spinner("Procesando DNIs..."):
        filtered_df['DNI_Validado'] = filtered_df[dni_column].apply(standardize_dni)
        
        # Detectar DNIs con problemas
        invalid_dnis = filtered_df[filtered_df['DNI_Validado'].str.contains('ERROR')]
        
        if not invalid_dnis.empty:
            st.warning(f"⚠️ Se encontraron {len(invalid_dnis)} DNIs con formato incorrecto:")
            
            # Mostrar tabla de DNIs inválidos
            st.dataframe(invalid_dnis[[dni_column, 'DNI_Validado']])
            
            # Ofrecer opciones al usuario
            dni_edit_option = st.radio(
                "¿Qué deseas hacer con los DNIs inválidos?",
                options=["Editar manualmente", "Conservar valores originales (pueden ser carnets de extranjería u otros documentos válidos)"],
                index=1,
                key="dni_edit_option_main"
            )
            
            if dni_edit_option == "Conservar valores originales (pueden ser carnets de extranjería u otros documentos válidos)":
                # Conservar los valores originales para carnets de extranjería y otros documentos
                st.info("ℹ️ Se conservarán los valores originales de los documentos de identidad")
                for idx in invalid_dnis.index:
                    # Usar el valor original del documento como valor validado
                    original_value = filtered_df.loc[idx, dni_column]
                    filtered_df.loc[idx, 'DNI_Validado'] = original_value
                
                # IMPORTANTE: Actualizar inmediatamente la sesión después de conservar valores
                st.session_state.processed_data = filtered_df.copy()
                # Marcar que se realizó esta acción
                st.session_state.last_action = "conservar_originales"
                st.success("✅ Todos los valores originales han sido conservados")
            else:
                # Ofrecer corrección manual
                st.subheader("Corrección Manual de DNI")
                
                # Seleccionar índice a corregir
                index_options = invalid_dnis.index.tolist()
                index_to_fix = st.selectbox(
                    "Selecciona el índice a corregir:", 
                    index_options,
                    key="dni_index_selector"
                )
                
                # Mostrar información del registro
                current_value = filtered_df.loc[index_to_fix, dni_column]
                st.info(f"DNI actual: {current_value}")
                
                # Si hay columnas de nombre, mostrar el nombre para mejor identificación
                name_cols = [col for col in filtered_df.columns if 'nombre' in col.lower() or 'apellido' in col.lower()]
                if name_cols:
                    name_values = [filtered_df.loc[index_to_fix, col] for col in name_cols]
                    st.info(f"Nombre: {' '.join(name_values)}")
                
                # Valor actual y nuevo valor
                new_value = st.text_input(
                    "Nuevo valor:", 
                    value=current_value,
                    key="dni_value_input"
                )
                
                # Ver una previsualización de la validación
                valid_preview = standardize_dni(new_value)
                if "ERROR" in valid_preview:
                    st.warning(f"⚠️ Validación: {valid_preview}")
                else:
                    st.success(f"✅ Validación: {valid_preview}")
                
                if st.button("Actualizar DNI", key="update_dni_btn"):
                    # Importar la función específica para actualizar DNIs
                    from pages.preprocessing.components.data_handlers import handle_dni_update
                    
                    # Usar la función específica para actualizar DNIs
                    filtered_df = handle_dni_update(filtered_df, index_to_fix, dni_column, new_value)
                    
                    # Actualizar la sesión (aunque ya lo hace la función handle_dni_update)
                    st.session_state.processed_data = filtered_df.copy()
                    
                    st.success(f"✅ DNI actualizado correctamente. El cambio se ha guardado en la sesión.")
                    
                    # Ofrecer continuar con otra edición o finalizar
                    if st.button("Continuar con otra edición", key="continue_edit"):
                        st.rerun()
                    
                    if st.button("Finalizar ediciones", key="finish_edit"):
                        # Marcamos explícitamente que se han terminado las ediciones
                        st.session_state.last_action = "ediciones_finalizadas"
                        st.success("✅ Ediciones completadas. Ahora puedes ordenar o exportar los datos.")
                else:
                    st.warning("⚠️ Por favor, selecciona una opción para continuar o finalizar la edición")
        else:
            st.success("✅ Todos los DNIs tienen un formato válido")
        
        # Verificar duplicados
        duplicates = get_duplicated_dnis(filtered_df, dni_column)
        
        if not duplicates.empty:
            st.warning(f"⚠️ Se encontraron {len(duplicates)} DNIs duplicados:")
            
            # Detectar columnas para mejor visualización
            display_columns = [dni_column, 'DNI_Validado']
            
            # Añadir columnas relevantes para verificar si es la misma persona
            nombre_cols = [col for col in filtered_df.columns if 'nombre' in col.lower() or 'apellido' in col.lower()]
            if nombre_cols:
                display_columns.extend(nombre_cols)
            
            # Añadir columna de email si existe
            email_cols = [col for col in filtered_df.columns if 'email' in col.lower() or 'correo' in col.lower()]
            if email_cols:
                display_columns.extend(email_cols)
            
            # Añadir columna de área si existe
            area_cols = [col for col in filtered_df.columns if 'área' in col.lower() or 'area' in col.lower()]
            if area_cols:
                display_columns.extend(area_cols)
            
            # Mostrar tabla de DNIs duplicados con información ampliada
            st.dataframe(duplicates[display_columns])
            
            st.info("ℹ️ Verifica si los duplicados corresponden a la misma persona aplicando a diferentes áreas o si son errores de datos.")
        else:
            st.success("✅ No se encontraron DNIs duplicados")
    
    return filtered_df

def validate_email_column(filtered_df, email_column):
    """
    Valida el formato de correo electrónico en una columna específica y muestra opciones para corrección.
    
    Args:
        filtered_df (pd.DataFrame): DataFrame a procesar
        email_column (str): Nombre de la columna que contiene los correos
        
    Returns:
        pd.DataFrame: DataFrame actualizado
    """
    st.subheader("Validación de Correo Electrónico")
    
    if not email_column:
        st.warning("⚠️ No se ha seleccionado una columna de correo electrónico.")
        return filtered_df
    
    # Validar y estandarizar emails
    with st.spinner("Procesando correos electrónicos..."):
        filtered_df['Email_Validado'] = filtered_df[email_column].apply(validate_email)
        
        # Detectar emails con problemas
        invalid_emails = filtered_df[filtered_df['Email_Validado'].str.contains('ERROR')]
        
        if not invalid_emails.empty:
            st.warning(f"⚠️ Se encontraron {len(invalid_emails)} correos con formato incorrecto:")
            
            # Mostrar tabla de emails inválidos
            st.dataframe(invalid_emails[[email_column, 'Email_Validado']])
            
            # Ofrecer corrección manual
            st.subheader("Corrección Manual de Correo")
            
            # Seleccionar índice a corregir
            index_options = invalid_emails.index.tolist()
            index_to_fix = st.selectbox(
                "Selecciona el índice a corregir:", 
                index_options,
                key="email_index_selector"
            )
            
            # Valor actual y nuevo valor
            current_value = filtered_df.loc[index_to_fix, email_column]
            new_value = st.text_input(
                "Nuevo valor:", 
                value=current_value,
                key="email_value_input"
            )
            
            if st.button("Actualizar Correo", key="update_email_btn"):
                filtered_df.loc[index_to_fix, email_column] = new_value
                filtered_df.loc[index_to_fix, 'Email_Validado'] = validate_email(new_value)
                st.session_state.processed_data = filtered_df.copy()
                st.success(f"✅ Correo actualizado correctamente")
        else:
            st.success("✅ Todos los correos tienen un formato válido")
        
        # Verificar duplicados
        email_duplicates = filtered_df[filtered_df.duplicated(subset=[email_column], keep=False)]
        
        if not email_duplicates.empty:
            st.warning(f"⚠️ Se encontraron {len(email_duplicates)} correos duplicados:")
            st.dataframe(email_duplicates[[email_column, 'Email_Validado']])
        else:
            st.success("✅ No se encontraron correos duplicados")
    
    return filtered_df 