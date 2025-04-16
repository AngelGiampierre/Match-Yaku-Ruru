import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from datetime import datetime
import sys
import os

# Agregar la raíz del proyecto al path de Python para importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from utils import load_data, save_data

def ruru_process_tab():
    """
    Pestaña para procesar y estandarizar los datos de rurus (estudiantes).
    Permite cargar archivos CSV o Excel, identificar automáticamente columnas relevantes,
    estandarizar formatos y descargar los datos procesados.
    """
    st.header("Preprocesamiento de Datos de Rurus")
    st.subheader("Carga y estandariza información de estudiantes")
    
    # Carga de archivo
    uploaded_file = st.file_uploader(
        "Carga el archivo con datos de rurus (.xlsx, .csv)",
        type=["xlsx", "csv"],
        key="ruru_file_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Determinar el tipo de archivo y leer los datos
            file_extension = uploaded_file.name.split(".")[-1].lower()
            
            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension == "xlsx":
                df = pd.read_excel(uploaded_file)
            
            # Mostrar información básica del archivo
            st.success(f"✅ Archivo cargado correctamente: {uploaded_file.name}")
            st.write(f"Dimensiones del DataFrame: {df.shape[0]} filas x {df.shape[1]} columnas")
            
            # Vista previa de los datos
            with st.expander("Vista previa de los datos cargados", expanded=True):
                st.dataframe(df.head())
            
            # Mostrar estadísticas de valores faltantes
            with st.expander("Estadísticas de valores faltantes"):
                missing_data = pd.DataFrame({
                    'Columna': df.columns,
                    'Tipo de Dato': df.dtypes.values,
                    'Valores Nulos': df.isnull().sum().values,
                    'Porcentaje Nulos': (df.isnull().sum().values / len(df) * 100).round(2)
                })
                st.dataframe(missing_data.sort_values('Valores Nulos', ascending=False))
            
            # Añadir información para el usuario
            st.info("""
                ℹ️ **Información sobre el procesamiento:**
                - El sistema identificará automáticamente columnas relevantes.
                - Los datos se estandarizarán para ser compatibles con el formato de los yakus.
                - Puedes ajustar manualmente la selección de columnas si es necesario.
                - Los horarios se convertirán a un formato estándar (Mañana, Tarde, Noche).
                - Las preferencias de cursos/talleres se adaptarán según el área detectada.
            """)
            
            # Procesamiento de datos
            if st.button("Procesar datos", key="process_ruru_button"):
                with st.spinner("Procesando datos de rurus..."):
                    processed_df = process_ruru_data(df)
                    
                    # Guardar datos procesados
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Opción para descargar como Excel
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            processed_df.to_excel(writer, index=False, sheet_name='Rurus')
                        excel_data = output.getvalue()
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Descargar como Excel",
                            data=excel_data,
                            file_name=f"rurus_procesados_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col2:
                        # Opción para descargar como CSV
                        csv = processed_df.to_csv(index=False)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Descargar como CSV",
                            data=csv,
                            file_name=f"rurus_procesados_{timestamp}.csv",
                            mime="text/csv"
                        )
                    
                    # Guardar en la carpeta temporal del sistema
                    save_data(processed_df, "rurus_processed.pkl")
                    st.success("✅ Datos procesados guardados en la memoria temporal del sistema")
                    
                    # Mostrar vista previa de los datos procesados
                    st.subheader("Vista previa de los datos procesados")
                    st.dataframe(processed_df.head())
                    
                    # Mostrar resumen de cambios realizados
                    st.subheader("Resumen del procesamiento")
                    st.write(f"- Número de filas: {processed_df.shape[0]}")
                    st.write(f"- Número de columnas: {processed_df.shape[1]}")
                    
                    # Listar columnas estandarizadas
                    st.write("- Columnas estandarizadas:")
                    for col in processed_df.columns:
                        st.write(f"  • {col}")
                    
                    # Estadísticas de valores faltantes después del procesamiento
                    with st.expander("Estadísticas de valores faltantes después del procesamiento"):
                        missing_data_after = pd.DataFrame({
                            'Columna': processed_df.columns,
                            'Tipo de Dato': processed_df.dtypes.values,
                            'Valores Nulos': processed_df.isnull().sum().values,
                            'Porcentaje Nulos': (processed_df.isnull().sum().values / len(processed_df) * 100).round(2)
                        })
                        st.dataframe(missing_data_after.sort_values('Valores Nulos', ascending=False))
                
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
            st.error("Por favor, revisa el archivo e intenta nuevamente.")
    else:
        st.info("Por favor, carga un archivo con datos de rurus para comenzar.")

def process_ruru_data(df):
    """
    Procesa y estandariza el DataFrame de rurus.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de rurus cargados.
        
    Returns:
        pd.DataFrame: DataFrame con los datos procesados y estandarizados.
    """
    # Crear una copia para no modificar el original
    processed_df = df.copy()
    
    # UI para seleccionar columnas
    st.subheader("Selección de columnas")
    
    # Identificar columnas automáticamente basadas en patrones comunes
    id_cols = identificar_columnas_id(df)
    name_cols = identificar_columnas_nombre(df)
    dni_cols = identificar_columnas_dni(df)
    grade_cols = identificar_columnas_grado(df)
    schedule_cols = identificar_columnas_horario(df)
    preference_cols = identificar_columnas_preferencia(df)
    quechua_cols = identificar_columnas_quechua(df)
    parent_cols = identificar_columnas_apoderado(df)
    contact_cols = identificar_columnas_contacto(df)
    
    st.write("Columnas identificadas automáticamente:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Identificación:**")
        for col in id_cols:
            st.write(f"- {col}")
        
        st.write("**Nombre:**")
        for col in name_cols:
            st.write(f"- {col}")
        
        st.write("**DNI:**")
        for col in dni_cols:
            st.write(f"- {col}")
        
        st.write("**Apoderado:**")
        for col in parent_cols:
            st.write(f"- {col}")
        
        st.write("**Nivel Quechua:**")
        for col in quechua_cols:
            st.write(f"- {col}")
    
    with col2:
        st.write("**Grado:**")
        for col in grade_cols:
            st.write(f"- {col}")
        
        st.write("**Contacto:**")
        for col in contact_cols:
            st.write(f"- {col}")
        
        st.write("**Horarios:**")
        # Mostrar solo algunos ejemplos para no sobrecargar la interfaz
        schedule_examples = schedule_cols[:5] if len(schedule_cols) > 5 else schedule_cols
        for col in schedule_examples:
            st.write(f"- {col}")
        if len(schedule_cols) > 5:
            st.write(f"- ... y {len(schedule_cols) - 5} más")
        
        st.write("**Preferencias:**")
        for col in preference_cols:
            st.write(f"- {col}")
    
    # Selección específica de columnas clave
    st.subheader("Mapeo de columnas esenciales")
    
    # ID
    id_column = st.selectbox(
        "Columna de ID:",
        options=["Ninguna"] + id_cols,
        index=1 if id_cols else 0,
        help="Columna que contiene el identificador único del ruru"
    )
    
    # Nombre
    nombre_column = st.selectbox(
        "Columna de Nombres:",
        options=["Ninguna"] + name_cols,
        index=1 if name_cols else 0,
        help="Columna que contiene el nombre del ruru"
    )
    
    apellido_column = st.selectbox(
        "Columna de Apellidos:",
        options=["Ninguna"] + [col for col in df.columns if "apellido" in col.lower()],
        index=1 if any("apellido" in col.lower() for col in df.columns) else 0,
        help="Columna que contiene los apellidos del ruru"
    )
    
    # DNI
    dni_column = st.selectbox(
        "Columna de DNI:",
        options=["Ninguna"] + dni_cols,
        index=1 if dni_cols else 0,
        help="Columna que contiene el DNI o documento de identidad del ruru"
    )
    
    # Grado
    grado_column = st.selectbox(
        "Columna de Grado:",
        options=["Ninguna"] + grade_cols,
        index=1 if grade_cols else 0,
        help="Columna que contiene el grado educativo del ruru"
    )
    
    # Nivel de Quechua
    quechua_column = st.selectbox(
        "Columna de Nivel de Quechua:",
        options=["Ninguna"] + quechua_cols,
        index=1 if quechua_cols else 0,
        help="Columna que contiene el nivel de quechua del ruru"
    )
    
    # Preferencias
    st.write("**Columnas de Preferencia de Cursos/Talleres:**")
    pref1_column = st.selectbox(
        "Primera preferencia:",
        options=["Ninguna"] + preference_cols,
        index=1 if preference_cols and len(preference_cols) > 0 else 0
    )
    
    pref2_column = st.selectbox(
        "Segunda preferencia:",
        options=["Ninguna"] + preference_cols,
        index=2 if preference_cols and len(preference_cols) > 1 else 0
    )
    
    pref3_column = st.selectbox(
        "Tercera preferencia:",
        options=["Ninguna"] + preference_cols,
        index=3 if preference_cols and len(preference_cols) > 2 else 0
    )
    
    # Apoderado
    apoderado_column = st.selectbox(
        "Columna de Apoderado:",
        options=["Ninguna"] + parent_cols,
        index=1 if parent_cols else 0,
        help="Columna que contiene el nombre del apoderado del ruru"
    )
    
    # Contacto
    contacto_column = st.selectbox(
        "Columna de Contacto:",
        options=["Ninguna"] + contact_cols,
        index=1 if contact_cols else 0,
        help="Columna que contiene el correo o teléfono de contacto"
    )
    
    # Columna de área
    area_columns = [col for col in df.columns if "area" in col.lower() or "área" in col.lower()]
    area_column = st.selectbox(
        "Columna de Área:",
        options=["Ninguna"] + area_columns + ["Detectar automáticamente"],
        index=len(area_columns) + 1 if area_columns else 0
    )
    
    # Detección automática de área si es necesario
    if area_column == "Detectar automáticamente":
        area_detected = detectar_area_automaticamente(df, preference_cols)
        st.write(f"Área detectada: **{area_detected}**")
    
    # Opciones de estandarización
    st.subheader("Opciones de estandarización")
    
    # Estandarización de horarios
    estandarizar_horarios = st.checkbox("Estandarizar horarios", value=True)
    
    # Estandarización de grado
    estandarizar_grado = st.checkbox("Estandarizar formato de grado", value=True)
    
    # Estandarización de nombres
    estandarizar_nombres = st.checkbox("Estandarizar formato de nombres", value=True)
    
    # Estandarización de preferencias
    estandarizar_preferencias = st.checkbox("Estandarizar preferencias por área", value=True)
    
    # Ejecutar la estandarización según las opciones seleccionadas
    if id_column != "Ninguna":
        processed_df['ID'] = processed_df[id_column]
    
    # Procesar nombre
    if nombre_column != "Ninguna" and apellido_column != "Ninguna":
        if estandarizar_nombres:
            processed_df['Nombre'] = processed_df.apply(
                lambda row: formatear_nombre(row[nombre_column], row[apellido_column]), 
                axis=1
            )
        else:
            processed_df['Nombre'] = processed_df[nombre_column] + " " + processed_df[apellido_column]
    
    # Procesar DNI
    if dni_column != "Ninguna":
        processed_df['DNI'] = processed_df[dni_column]
    
    # Procesar grado
    if grado_column != "Ninguna" and estandarizar_grado:
        processed_df['Grado'] = processed_df[grado_column].apply(estandarizar_formato_grado)
    elif grado_column != "Ninguna":
        processed_df['Grado'] = processed_df[grado_column]
    
    # Procesar nivel de quechua
    if quechua_column != "Ninguna":
        processed_df['Nivel_Quechua'] = processed_df[quechua_column].apply(estandarizar_nivel_quechua)
    
    # Procesar horarios
    if estandarizar_horarios:
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        for dia in dias_semana:
            processed_df[f'Horario_{dia}'] = procesar_horario_ruru(df, dia)
    
    # Determinar área
    if area_column == "Detectar automáticamente":
        area_detected = detectar_area_automaticamente(df, preference_cols)
        processed_df['Area'] = area_detected
    elif area_column != "Ninguna":
        processed_df['Area'] = processed_df[area_column]
    
    # Procesar preferencias
    if estandarizar_preferencias and 'Area' in processed_df.columns:
        # Procesar según el área detectada o seleccionada
        processed_df['Opciones'] = procesar_preferencias_por_area(
            processed_df,
            pref1_column if pref1_column != "Ninguna" else None,
            pref2_column if pref2_column != "Ninguna" else None, 
            pref3_column if pref3_column != "Ninguna" else None
        )
    else:
        # Almacenar preferencias individuales si no se estandarizan
        if pref1_column != "Ninguna":
            processed_df['Preferencia_1'] = processed_df[pref1_column]
        
        if pref2_column != "Ninguna":
            processed_df['Preferencia_2'] = processed_df[pref2_column]
        
        if pref3_column != "Ninguna":
            processed_df['Preferencia_3'] = processed_df[pref3_column]
    
    # Procesar contacto y apoderado
    if contacto_column != "Ninguna":
        processed_df['Contacto'] = processed_df[contacto_column]
    
    if apoderado_column != "Ninguna":
        processed_df['Apoderado'] = processed_df[apoderado_column]
    
    # Seleccionar solo las columnas estandarizadas
    columnas_estandar = [col for col in ['ID', 'Nombre', 'DNI', 'Grado', 'Area', 
                                         'Opciones', 'Nivel_Quechua', 'Apoderado', 'Contacto'] 
                          if col in processed_df.columns]
    
    # Agregar columnas de horario
    columnas_estandar.extend([f'Horario_{dia}' for dia in dias_semana 
                              if f'Horario_{dia}' in processed_df.columns])
    
    # Agregar preferencias individuales si existen
    for pref in ['Preferencia_1', 'Preferencia_2', 'Preferencia_3']:
        if pref in processed_df.columns:
            columnas_estandar.append(pref)
    
    # Filtrar por las columnas que realmente existen
    columnas_estandar = [col for col in columnas_estandar if col in processed_df.columns]
    
    # Devolver el dataframe final con las columnas estandarizadas
    return processed_df[columnas_estandar]

# Funciones auxiliares para identificación de columnas
def identificar_columnas_id(df):
    """Identifica columnas que probablemente contengan IDs de rurus."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['id', 'identificador', 'código', 'code'])]

def identificar_columnas_nombre(df):
    """Identifica columnas que probablemente contengan nombres de rurus."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['nombre', 'name', 'estudiante'])]

def identificar_columnas_dni(df):
    """Identifica columnas que probablemente contengan DNIs o documentos de identidad."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['dni', 'documento', 'document', 'identidad', 'identity'])]

def identificar_columnas_grado(df):
    """Identifica columnas que probablemente contengan el grado educativo."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['grado', 'grade', 'nivel', 'level'])]

def identificar_columnas_horario(df):
    """Identifica columnas que probablemente contengan información de horarios."""
    dias = ['lunes', 'martes', 'miércoles', 'miercoles', 'jueves', 'viernes', 'sábado', 'sabado', 'domingo']
    horarios = ['horario', 'schedule', 'disponibilidad', 'availability', 'mañana', 'tarde', 'noche']
    
    return [col for col in df.columns if 
            any(dia in col.lower() for dia in dias) or 
            any(horario in col.lower() for horario in horarios)]

def identificar_columnas_preferencia(df):
    """Identifica columnas que probablemente contengan preferencias de cursos o talleres."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['prefer', 'curso', 'course', 'taller', 'workshop', 'asignatura'])]

def detectar_area_automaticamente(df, preference_cols):
    """
    Detecta automáticamente el área basada en las columnas de preferencias.
    
    Args:
        df (pd.DataFrame): DataFrame de rurus
        preference_cols (list): Lista de columnas de preferencias
        
    Returns:
        str: Área detectada ('Arte & Cultura', 'Asesoría a Colegios Nacionales' o 'Bienestar Psicológico')
    """
    # Buscar columnas que contengan indicadores específicos
    arte_cultura_count = 0
    academico_count = 0
    
    # Términos relacionados con cada área
    arte_terms = ['arte', 'cultura', 'pintura', 'dibujo', 'música', 'musica', 'danza', 'teatro', 'cuenta']
    academico_terms = ['matemática', 'matematica', 'comunicación', 'comunicacion', 'inglés', 'ingles']
    
    # Buscar en todas las columnas de preferencias
    for col in preference_cols:
        if col in df.columns:
            # Verificar términos en los nombres de las columnas
            if any(term in col.lower() for term in arte_terms):
                arte_cultura_count += 1
            if any(term in col.lower() for term in academico_terms):
                academico_count += 1
            
            # Verificar términos en los valores únicos de las columnas
            unique_values = df[col].dropna().astype(str).unique()
            for value in unique_values:
                if any(term in value.lower() for term in arte_terms):
                    arte_cultura_count += 1
                if any(term in value.lower() for term in academico_terms):
                    academico_count += 1
    
    # Verificar también columnas explícitas de área
    area_cols = [col for col in df.columns if 'area' in col.lower() or 'área' in col.lower()]
    for col in area_cols:
        unique_values = df[col].dropna().astype(str).unique()
        for value in unique_values:
            value = value.lower()
            if 'arte' in value or 'cultura' in value:
                return 'Arte & Cultura'
            if 'asesor' in value or 'colegio' in value or 'nacional' in value:
                return 'Asesoría a Colegios Nacionales'
            if 'bienestar' in value or 'psico' in value:
                return 'Bienestar Psicológico'
    
    # Determinar área basada en el conteo
    if arte_cultura_count > academico_count:
        return 'Arte & Cultura'
    elif academico_count > arte_cultura_count:
        return 'Asesoría a Colegios Nacionales'
    else:
        # Si no hay suficiente información, retornar valor por defecto
        return 'Asesoría a Colegios Nacionales'  # Valor más común por defecto

def formatear_nombre(nombre, apellido):
    """
    Estandariza formato de nombre y apellido.
    
    Args:
        nombre (str): Nombre del estudiante
        apellido (str): Apellido del estudiante
        
    Returns:
        str: Nombre formateado
    """
    if pd.isna(nombre) or pd.isna(apellido):
        return ""
    
    # Eliminar espacios extras
    nombre = ' '.join(nombre.split())
    apellido = ' '.join(apellido.split())
    
    # Convertir a título (primera letra mayúscula)
    nombre = nombre.title()
    apellido = apellido.title()
    
    # Abreviar apellido para formato estándar
    apellido_abreviado = ' '.join([p[0] + '.' for p in apellido.split()])
    
    return f"{nombre} {apellido_abreviado}"

def estandarizar_formato_grado(grado_texto):
    """
    Estandariza el formato de grado para que sea compatible con el algoritmo de matching.
    
    Args:
        grado_texto (str): Texto que describe el grado
        
    Returns:
        str: Grado estandarizado
    """
    if pd.isna(grado_texto):
        return ""
    
    grado_texto = str(grado_texto).lower()
    
    # Mapeo de grados
    if "primero" in grado_texto or "1" in grado_texto:
        if "primaria" in grado_texto:
            return "Primaria (1° y 2° grado)"
        elif "secundaria" in grado_texto:
            return "Secundaria (1°, 2° y 3° grado)"
    
    elif "segundo" in grado_texto or "2" in grado_texto:
        if "primaria" in grado_texto:
            return "Primaria (1° y 2° grado)"
        elif "secundaria" in grado_texto:
            return "Secundaria (1°, 2° y 3° grado)"
    
    elif "tercero" in grado_texto or "3" in grado_texto:
        if "primaria" in grado_texto:
            return "Primaria (3° y 4° grado)"
        elif "secundaria" in grado_texto:
            return "Secundaria (1°, 2° y 3° grado)"
    
    elif "cuarto" in grado_texto or "4" in grado_texto:
        if "primaria" in grado_texto:
            return "Primaria (3° y 4° grado)"
        else:
            return "Secundaria (4° y 5° grado)"
    
    elif "quinto" in grado_texto or "5" in grado_texto:
        if "primaria" in grado_texto:
            return "Primaria (5° y 6° grado)"
        else:
            return "Secundaria (4° y 5° grado)"
    
    elif "sexto" in grado_texto or "6" in grado_texto:
        return "Primaria (5° y 6° grado)"
    
    # Si no se puede mapear, devolver el texto original
    return grado_texto

def procesar_horario_ruru(df, dia):
    """
    Procesa las columnas de horario para un día específico y retorna la disponibilidad en formato estándar.
    
    Args:
        df (pd.DataFrame): DataFrame de rurus
        dia (str): Día de la semana (Lunes, Martes, etc.)
        
    Returns:
        pd.Series: Serie con la disponibilidad estandarizada
    """
    # Verificar si hay columnas específicas para mañana, tarde, noche
    manana_col = f"{dia}/Mañana (8 am - 12 pm)"
    tarde_col = f"{dia}/Tarde (2pm -6 pm)"
    noche_col = f"{dia}/Noche (6pm -10 pm)"
    
    # Si existen las columnas específicas
    if manana_col in df.columns and tarde_col in df.columns and noche_col in df.columns:
        # Crear una serie temporal para almacenar los resultados
        result = pd.Series(index=df.index, data="No disponible")
        
        # Procesar cada registro
        for idx in df.index:
            periodos = []
            
            # Verificar disponibilidad en cada periodo
            if manana_col in df.columns and pd.notna(df.at[idx, manana_col]) and df.at[idx, manana_col] == 1:
                periodos.append("Mañana")
            
            if tarde_col in df.columns and pd.notna(df.at[idx, tarde_col]) and df.at[idx, tarde_col] == 1:
                periodos.append("Tarde")
            
            if noche_col in df.columns and pd.notna(df.at[idx, noche_col]) and df.at[idx, noche_col] == 1:
                periodos.append("Noche")
            
            # Asignar el resultado
            if periodos:
                result.at[idx] = ", ".join(periodos)
        
        return result
    
    # Verificar si hay una columna general para el día
    dia_col = next((col for col in df.columns if dia.lower() in col.lower() and "horario" in col.lower()), None)
    
    if dia_col:
        # Aplicar función de mapeo para extraer información de disponibilidad
        return df[dia_col].apply(lambda x: extraer_disponibilidad_texto(x))
    
    # Si no se encuentra ninguna columna, devolver "No disponible" para todos
    return pd.Series(index=df.index, data="No disponible")

def extraer_disponibilidad_texto(texto):
    """
    Extrae información de disponibilidad a partir de texto.
    
    Args:
        texto (str): Texto que describe disponibilidad
        
    Returns:
        str: Disponibilidad estandarizada
    """
    if pd.isna(texto):
        return "No disponible"
    
    texto = str(texto).lower()
    
    periodos = []
    if "mañana" in texto:
        periodos.append("Mañana")
    if "tarde" in texto:
        periodos.append("Tarde")
    if "noche" in texto:
        periodos.append("Noche")
    
    if periodos:
        return ", ".join(periodos)
    else:
        return "No disponible"

def identificar_columnas_quechua(df):
    """Identifica columnas que probablemente contengan el nivel de quechua."""
    return [col for col in df.columns if 'quechua' in col.lower()]

def identificar_columnas_apoderado(df):
    """Identifica columnas que probablemente contengan información del apoderado."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                          ['apoderado', 'padre', 'madre', 'tutor', 'encargado', 'responsable', 'parent'])]

def identificar_columnas_contacto(df):
    """Identifica columnas que probablemente contengan información de contacto."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                          ['correo', 'email', 'mail', 'teléfono', 'telefono', 'celular', 'móvil', 'movil', 'phone'])]

def estandarizar_nivel_quechua(nivel_texto):
    """
    Estandariza el nivel de quechua.
    
    Args:
        nivel_texto (str): Texto que describe el nivel de quechua
        
    Returns:
        str: Nivel de quechua estandarizado
    """
    if pd.isna(nivel_texto):
        return "No lo hablo"
    
    nivel_texto = str(nivel_texto).lower()
    
    if 'no' in nivel_texto or 'ninguno' in nivel_texto or 'ningún' in nivel_texto:
        return 'No lo hablo'
    elif 'básico' in nivel_texto or 'basico' in nivel_texto:
        return 'Nivel básico'
    elif 'intermedio' in nivel_texto:
        return 'Nivel intermedio'
    elif 'avanzado' in nivel_texto:
        return 'Nivel avanzado'
    elif 'nativo' in nivel_texto:
        return 'Nativo'
    else:
        return 'No lo hablo'  # Valor por defecto

def procesar_preferencias_por_area(df, pref1_col=None, pref2_col=None, pref3_col=None):
    """
    Procesa las preferencias según el área detectada.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de rurus
        pref1_col (str): Nombre de la columna de primera preferencia
        pref2_col (str): Nombre de la columna de segunda preferencia
        pref3_col (str): Nombre de la columna de tercera preferencia
        
    Returns:
        pd.Series: Serie con las preferencias estandarizadas
    """
    # Crear una serie temporal para almacenar los resultados
    result = pd.Series(index=df.index, data="")
    
    for idx in df.index:
        area = df.at[idx, 'Area'] if 'Area' in df.columns and pd.notna(df.at[idx, 'Area']) else ""
        area = str(area).lower()
        
        preferencias = []
        
        # Recopilar preferencias no nulas
        if pref1_col and pref1_col in df.columns and pd.notna(df.at[idx, pref1_col]):
            preferencias.append(str(df.at[idx, pref1_col]))
        if pref2_col and pref2_col in df.columns and pd.notna(df.at[idx, pref2_col]):
            preferencias.append(str(df.at[idx, pref2_col]))
        if pref3_col and pref3_col in df.columns and pd.notna(df.at[idx, pref3_col]):
            preferencias.append(str(df.at[idx, pref3_col]))
        
        # Estandarizar según el área
        if 'arte' in area and 'cultura' in area:
            # Para Arte & Cultura, usamos la primera preferencia de taller
            if preferencias:
                result.at[idx] = preferencias[0]
        
        elif 'asesor' in area and ('colegio' in area or 'nacional' in area):
            # Para Asesoría a Colegios, usamos la primera preferencia de asignatura
            if preferencias:
                result.at[idx] = preferencias[0]
        
        # Bienestar Psicológico no requiere preferencias específicas
        
        # Si no tenemos un área definida o preferencias, dejamos vacío
    
    return result 