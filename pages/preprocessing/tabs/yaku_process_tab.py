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

def yaku_process_tab():
    """
    Tab para procesar y estandarizar los datos de yakus (mentores).
    """
    st.header("Preprocesamiento de Datos de Yakus")
    st.subheader("Carga y estandariza información de mentores")
    
    # Carga de archivo
    uploaded_file = st.file_uploader(
        "Carga el archivo con datos de yakus (.xlsx, .csv)",
        type=["xlsx", "csv"],
        key="yaku_file_uploader"
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
            
            # Procesamiento de datos
            if st.button("Procesar datos", key="process_yaku_button"):
                with st.spinner("Procesando datos de yakus..."):
                    processed_df = process_yaku_data(df)
                    
                    # Guardar datos procesados
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Opción para descargar como Excel
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            processed_df.to_excel(writer, index=False, sheet_name='Yakus')
                        excel_data = output.getvalue()
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Descargar como Excel",
                            data=excel_data,
                            file_name=f"yakus_procesados_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col2:
                        # Opción para descargar como CSV
                        csv = processed_df.to_csv(index=False)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Descargar como CSV",
                            data=csv,
                            file_name=f"yakus_procesados_{timestamp}.csv",
                            mime="text/csv"
                        )
                    
                    # Guardar en la carpeta temporal del sistema
                    save_data(processed_df, "yakus_processed.pkl")
                    st.success("✅ Datos procesados guardados en la memoria temporal del sistema")
                    
                    # Mostrar vista previa de los datos procesados
                    st.subheader("Vista previa de los datos procesados")
                    st.dataframe(processed_df.head())
                    
                    # Mostrar resumen de cambios realizados
                    st.subheader("Resumen del procesamiento")
                    st.write(f"- Número de filas: {processed_df.shape[0]}")
                    st.write(f"- Número de columnas: {processed_df.shape[1]}")
                    
                    # Estadísticas después del procesamiento
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
    else:
        st.info("Por favor, carga un archivo con datos de yakus para comenzar.")

def process_yaku_data(df):
    """
    Procesa y estandariza el DataFrame de yakus.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de yakus cargados.
        
    Returns:
        pd.DataFrame: DataFrame con los datos procesados y estandarizados.
    """
    # Crear una copia para no modificar el original
    processed_df = df.copy()
    
    # UI para seleccionar columnas
    st.subheader("Selección de columnas")
    
    # Identificar automáticamente columnas relevantes
    area_cols = identificar_columnas_area(df)
    name_cols = identificar_columnas_nombre(df)
    dni_cols = identificar_columnas_dni(df)
    schedule_cols = identificar_columnas_horario(df)
    options_cols = identificar_columnas_opciones(df)
    level_cols = identificar_columnas_nivel(df)
    quechua_cols = identificar_columnas_quechua(df)
    contact_cols = identificar_columnas_contacto(df)
    
    st.write("Columnas identificadas automáticamente:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Área:**")
        for col in area_cols:
            st.write(f"- {col}")
        
        st.write("**Nombre:**")
        for col in name_cols:
            st.write(f"- {col}")
        
        st.write("**DNI:**")
        for col in dni_cols:
            st.write(f"- {col}")
        
        st.write("**Nivel Quechua:**")
        for col in quechua_cols:
            st.write(f"- {col}")
    
    with col2:
        st.write("**Nivel Educativo:**")
        for col in level_cols:
            st.write(f"- {col}")
        
        st.write("**Horarios:**")
        # Mostrar solo algunos ejemplos para no sobrecargar la interfaz
        schedule_examples = schedule_cols[:5] if len(schedule_cols) > 5 else schedule_cols
        for col in schedule_examples:
            st.write(f"- {col}")
        if len(schedule_cols) > 5:
            st.write(f"- ... y {len(schedule_cols) - 5} más")
        
        st.write("**Opciones/Cursos:**")
        for col in options_cols:
            st.write(f"- {col}")
    
    # Selección específica de columnas clave
    st.subheader("Mapeo de columnas esenciales")
    
    # Área
    area_column = st.selectbox(
        "Columna de Área:",
        options=["Ninguna"] + area_cols,
        index=1 if area_cols else 0,
        help="Columna que contiene el área de voluntariado del yaku"
    )
    
    # Nombre
    nombre_column = st.selectbox(
        "Columna de Nombre:",
        options=["Ninguna"] + name_cols,
        index=1 if name_cols else 0,
        help="Columna que contiene el nombre del yaku"
    )
    
    # DNI
    dni_column = st.selectbox(
        "Columna de DNI:",
        options=["Ninguna"] + dni_cols,
        index=1 if dni_cols else 0,
        help="Columna que contiene el DNI o documento de identidad del yaku"
    )
    
    # Nivel Quechua
    quechua_column = st.selectbox(
        "Columna de Nivel de Quechua:",
        options=["Ninguna"] + quechua_cols,
        index=1 if quechua_cols else 0,
        help="Columna que contiene el nivel de quechua del yaku"
    )
    
    # Nivel Educativo
    nivel_column = st.selectbox(
        "Columna de Niveles Educativos:",
        options=["Ninguna"] + level_cols,
        index=1 if level_cols else 0,
        help="Columna que contiene los niveles educativos que puede atender el yaku"
    )
    
    # Opciones (Taller o Asignatura)
    taller_column = st.selectbox(
        "Columna de Taller (Arte & Cultura):",
        options=["Ninguna"] + [col for col in options_cols if "taller" in col.lower()],
        index=1 if any("taller" in col.lower() for col in options_cols) else 0,
        help="Columna que contiene el taller de arte y cultura del yaku"
    )
    
    asignatura_column = st.selectbox(
        "Columna de Asignatura (Asesoría a Colegios):",
        options=["Ninguna"] + [col for col in options_cols if "asignatura" in col.lower() or "curso" in col.lower()],
        index=1 if any("asignatura" in col.lower() or "curso" in col.lower() for col in options_cols) else 0,
        help="Columna que contiene las asignaturas del yaku"
    )
    
    # Contacto
    contacto_column = st.selectbox(
        "Columna de Contacto:",
        options=["Ninguna"] + contact_cols,
        index=1 if contact_cols else 0,
        help="Columna que contiene el correo o teléfono de contacto del yaku"
    )
    
    # Opciones de estandarización
    st.subheader("Opciones de estandarización")
    
    # Estandarización de horarios
    estandarizar_horarios = st.checkbox("Estandarizar horarios", value=True)
    
    # Estandarización de nombres
    estandarizar_nombres = st.checkbox("Estandarizar formato de nombres", value=True)
    
    # Estandarización de opciones según área
    estandarizar_opciones = st.checkbox("Estandarizar opciones según área", value=True)
    
    # Ejecutar la estandarización según las opciones seleccionadas
    
    # Procesar ID (usamos DNI como ID)
    if dni_column != "Ninguna":
        processed_df['ID'] = processed_df[dni_column]
        processed_df['DNI'] = processed_df[dni_column]
    
    # Procesar nombre
    if nombre_column != "Ninguna":
        if estandarizar_nombres:
            processed_df['Nombre'] = processed_df[nombre_column].apply(lambda x: formatear_nombre_yaku(x))
        else:
            processed_df['Nombre'] = processed_df[nombre_column]
    
    # Procesar área
    if area_column != "Ninguna":
        processed_df['Area'] = processed_df[area_column].apply(estandarizar_area)
    
    # Procesar nivel de quechua
    if quechua_column != "Ninguna":
        processed_df['Nivel_Quechua'] = processed_df[quechua_column].apply(estandarizar_nivel_quechua)
    
    # Procesar niveles educativos
    if nivel_column != "Ninguna":
        processed_df['Grados'] = processed_df[nivel_column].apply(estandarizar_niveles_educativos)
    
    # Procesar opciones según área
    if estandarizar_opciones:
        processed_df['Opciones'] = procesar_opciones_por_area(
            processed_df, 
            area_column, 
            taller_column, 
            asignatura_column
        )
    
    # Procesar horarios
    if estandarizar_horarios:
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        for dia in dias_semana:
            processed_df[f'Horario_{dia}'] = procesar_horario_yaku(df, dia)
    
    # Procesar contacto
    if contacto_column != "Ninguna":
        processed_df['Contacto'] = processed_df[contacto_column]
    
    # Seleccionar solo las columnas estandarizadas
    columnas_estandar = [col for col in ['ID', 'Nombre', 'DNI', 'Area', 'Opciones',
                                         'Nivel_Quechua', 'Grados', 'Contacto'] 
                          if col in processed_df.columns]
    
    # Agregar columnas de horario
    columnas_estandar.extend([f'Horario_{dia}' for dia in dias_semana 
                              if f'Horario_{dia}' in processed_df.columns])
    
    # Filtrar por las columnas que realmente existen
    columnas_estandar = [col for col in columnas_estandar if col in processed_df.columns]
    
    # Devolver el dataframe final con las columnas estandarizadas
    return processed_df[columnas_estandar]

# Funciones auxiliares para identificación de columnas
def identificar_columnas_area(df):
    """Identifica columnas que probablemente contengan el área de voluntariado."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['área', 'area', 'voluntariado', 'volunteer'])]

def identificar_columnas_nombre(df):
    """Identifica columnas que probablemente contengan nombres de yakus."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['nombre', 'name', 'completo'])]

def identificar_columnas_dni(df):
    """Identifica columnas que probablemente contengan DNIs o documentos de identidad."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['dni', 'documento', 'document', 'identidad', 'identity', 'pasaporte'])]

def identificar_columnas_horario(df):
    """Identifica columnas que probablemente contengan información de horarios."""
    dias = ['lunes', 'martes', 'miércoles', 'miercoles', 'jueves', 'viernes', 'sábado', 'sabado', 'domingo']
    horarios = ['horario', 'schedule', 'disponibilidad', 'availability']
    
    return [col for col in df.columns if 
            any(dia in col.lower() for dia in dias) or 
            any(horario in col.lower() for horario in horarios)]

def identificar_columnas_opciones(df):
    """Identifica columnas que probablemente contengan opciones de talleres o asignaturas."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['taller', 'asignatura', 'curso', 'materia', 'workshop', 'course', 'subject'])]

def identificar_columnas_nivel(df):
    """Identifica columnas que probablemente contengan niveles educativos."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['nivel', 'grado', 'level', 'grade', 'educativo'])]

def identificar_columnas_quechua(df):
    """Identifica columnas que probablemente contengan el nivel de quechua."""
    return [col for col in df.columns if 'quechua' in col.lower()]

def identificar_columnas_contacto(df):
    """Identifica columnas que probablemente contengan información de contacto."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['correo', 'email', 'mail', 'teléfono', 'telefono', 'celular', 'móvil', 'movil', 'phone'])]

def formatear_nombre_yaku(nombre):
    """
    Estandariza formato de nombre para yakus.
    
    Args:
        nombre (str): Nombre completo del yaku
        
    Returns:
        str: Nombre formateado
    """
    if pd.isna(nombre):
        return ""
    
    # Eliminar espacios extras
    nombre = ' '.join(str(nombre).split())
    
    # Convertir a título (primera letra mayúscula)
    nombre = nombre.title()
    
    # Obtener las iniciales de apellidos (si es posible inferirlos)
    nombres = nombre.split()
    
    if len(nombres) >= 3:
        # Asumimos que el último o los dos últimos términos son apellidos
        if len(nombres) >= 4:  # Posiblemente nombre compuesto y dos apellidos
            resultado = f"{nombres[0]} {nombres[1]} {nombres[2][0]}. {nombres[3][0]}."
        else:  # Un nombre y dos apellidos o dos nombres y un apellido
            resultado = f"{nombres[0]} {nombres[1]} {nombres[2][0]}."
    else:
        # Si solo hay 1 o 2 términos, devolvemos el nombre completo
        resultado = nombre
    
    return resultado

def estandarizar_area(area_texto):
    """
    Estandariza el nombre del área de voluntariado.
    
    Args:
        area_texto (str): Texto que describe el área
        
    Returns:
        str: Área estandarizada
    """
    if pd.isna(area_texto):
        return ""
    
    area_texto = str(area_texto).lower()
    
    if 'arte' in area_texto and 'cultura' in area_texto:
        return 'Arte & Cultura'
    elif 'asesor' in area_texto and ('colegio' in area_texto or 'nacional' in area_texto):
        return 'Asesoría a Colegios Nacionales'
    elif 'bienestar' in area_texto or 'psico' in area_texto:
        return 'Bienestar Psicológico'
    else:
        return area_texto.title()  # Devolver con primera letra mayúscula si no coincide

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

def estandarizar_niveles_educativos(niveles_texto):
    """
    Estandariza los niveles educativos.
    
    Args:
        niveles_texto (str): Texto que describe los niveles educativos
        
    Returns:
        str: Niveles educativos estandarizados
    """
    if pd.isna(niveles_texto):
        return ""
    
    niveles_texto = str(niveles_texto).lower()
    
    niveles = []
    
    # Primaria
    if '1' in niveles_texto and 'primaria' in niveles_texto or '2' in niveles_texto and 'primaria' in niveles_texto:
        niveles.append("Primaria (1° y 2° grado)")
    
    if '3' in niveles_texto and 'primaria' in niveles_texto or '4' in niveles_texto and 'primaria' in niveles_texto:
        niveles.append("Primaria (3° y 4° grado)")
    
    if '5' in niveles_texto and 'primaria' in niveles_texto or '6' in niveles_texto and 'primaria' in niveles_texto:
        niveles.append("Primaria (5° y 6° grado)")
    
    # Secundaria
    if ('1' in niveles_texto and 'secundaria' in niveles_texto or 
        '2' in niveles_texto and 'secundaria' in niveles_texto or 
        '3' in niveles_texto and 'secundaria' in niveles_texto):
        niveles.append("Secundaria (1°, 2° y 3° grado)")
    
    if ('4' in niveles_texto and 'secundaria' in niveles_texto or 
        '5' in niveles_texto and 'secundaria' in niveles_texto):
        niveles.append("Secundaria (4° y 5° grado)")
    
    # Si no se pudo detectar, devolver el texto original
    if not niveles:
        return niveles_texto
    
    return ", ".join(niveles)

def procesar_opciones_por_area(df, area_column, taller_column, asignatura_column):
    """
    Procesa las opciones (talleres o asignaturas) según el área del yaku.
    
    Args:
        df (pd.DataFrame): DataFrame de yakus
        area_column (str): Nombre de la columna de área
        taller_column (str): Nombre de la columna de taller
        asignatura_column (str): Nombre de la columna de asignatura
        
    Returns:
        pd.Series: Serie con las opciones estandarizadas
    """
    # Crear una serie temporal para almacenar los resultados
    result = pd.Series(index=df.index, data="")
    
    for idx in df.index:
        area = df.at[idx, area_column] if pd.notna(df.at[idx, area_column]) else ""
        area = str(area).lower()
        
        if 'arte' in area and 'cultura' in area:
            if taller_column != "Ninguna" and taller_column in df.columns:
                result.at[idx] = df.at[idx, taller_column] if pd.notna(df.at[idx, taller_column]) else ""
        
        elif 'asesor' in area and ('colegio' in area or 'nacional' in area):
            if asignatura_column != "Ninguna" and asignatura_column in df.columns:
                result.at[idx] = df.at[idx, asignatura_column] if pd.notna(df.at[idx, asignatura_column]) else ""
        
        elif 'bienestar' in area or 'psico' in area:
            result.at[idx] = "Facilitador psicoeducativo"
    
    return result

def procesar_horario_yaku(df, dia):
    """
    Procesa las columnas de horario para un día específico y retorna la disponibilidad en formato estándar.
    
    Args:
        df (pd.DataFrame): DataFrame de yakus
        dia (str): Día de la semana (Lunes, Martes, etc.)
        
    Returns:
        pd.Series: Serie con la disponibilidad estandarizada
    """
    # Buscar columna relacionada con el día
    dia_col = next((col for col in df.columns if dia in col and 'Horarios' in col), None)
    
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
    if "mañana" in texto or "8am" in texto or "8 am" in texto:
        periodos.append("Mañana")
    if "tarde" in texto or "2pm" in texto or "2 pm" in texto:
        periodos.append("Tarde")
    if "noche" in texto or "6pm" in texto or "6 pm" in texto:
        periodos.append("Noche")
    
    if periodos:
        return ", ".join(periodos)
    else:
        return "No disponible" 