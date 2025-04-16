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

def courses_process_tab():
    """
    Tab para procesar y estandarizar datos de cursos/talleres.
    Permite unificar nombres y categorizar cursos para el matching.
    """
    st.header("Preprocesamiento de Cursos/Talleres")
    st.subheader("Estandariza nombres y categorías de cursos para el matching")
    
    # Carga de archivo
    uploaded_file = st.file_uploader(
        "Carga el archivo con datos de cursos (.xlsx, .csv)",
        type=["xlsx", "csv"],
        key="courses_file_uploader"
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
            
            # Identificar posibles columnas de cursos
            course_cols = identificar_columnas_curso(df)
            area_cols = identificar_columnas_area(df)
            level_cols = identificar_columnas_nivel(df)
            
            st.write("### Columnas Identificadas")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Columnas de Cursos/Talleres:**")
                for col in course_cols:
                    st.write(f"- {col}")
                
                st.write("**Columnas de Área:**")
                for col in area_cols:
                    st.write(f"- {col}")
            
            with col2:
                st.write("**Columnas de Nivel Educativo:**")
                for col in level_cols:
                    st.write(f"- {col}")
            
            # Selección de columnas
            st.write("### Configuración del procesamiento")
            
            # Curso
            curso_column = st.selectbox(
                "Columna de Curso/Taller:",
                options=["Ninguna"] + course_cols,
                index=1 if course_cols else 0,
                help="Columna que contiene el nombre del curso o taller"
            )
            
            # Área
            area_column = st.selectbox(
                "Columna de Área:",
                options=["Ninguna"] + area_cols,
                index=1 if area_cols else 0,
                help="Columna que indica el área al que pertenece el curso (Arte & Cultura, Asesoría a Colegios, etc.)"
            )
            
            # Nivel educativo
            nivel_column = st.selectbox(
                "Columna de Nivel Educativo:",
                options=["Ninguna"] + level_cols,
                index=1 if level_cols else 0,
                help="Columna que indica los niveles educativos aplicables para el curso"
            )
            
            # Opciones de estandarización
            st.write("### Opciones de estandarización")
            
            # Estandarización de nombres de cursos
            estandarizar_nombres = st.checkbox("Estandarizar nombres de cursos/talleres", value=True)
            
            # Verificación de duplicados
            verificar_duplicados = st.checkbox("Verificar y eliminar duplicados", value=True)
            
            # Procesamiento de datos
            if st.button("Procesar datos", key="process_courses_button"):
                with st.spinner("Procesando datos de cursos..."):
                    processed_df = process_courses_data(
                        df, 
                        curso_column, 
                        area_column, 
                        nivel_column, 
                        estandarizar_nombres, 
                        verificar_duplicados
                    )
                    
                    # Guardar datos procesados
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Opción para descargar como Excel
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            processed_df.to_excel(writer, index=False, sheet_name='Cursos')
                        excel_data = output.getvalue()
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Descargar como Excel",
                            data=excel_data,
                            file_name=f"cursos_procesados_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col2:
                        # Opción para descargar como CSV
                        csv = processed_df.to_csv(index=False)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Descargar como CSV",
                            data=csv,
                            file_name=f"cursos_procesados_{timestamp}.csv",
                            mime="text/csv"
                        )
                    
                    # Guardar en la carpeta temporal del sistema
                    save_data(processed_df, "courses_processed.pkl")
                    st.success("✅ Datos procesados guardados en la memoria temporal del sistema")
                    
                    # Mostrar vista previa de los datos procesados
                    st.subheader("Vista previa de los datos procesados")
                    st.dataframe(processed_df.head())
                    
                    # Mostrar resumen de cambios realizados
                    st.subheader("Resumen del procesamiento")
                    st.write(f"- Número de cursos únicos: {processed_df.shape[0]}")
                    st.write(f"- Número de columnas: {processed_df.shape[1]}")
                    
                    # Mostrar distribución por área
                    if 'Area' in processed_df.columns:
                        st.write("### Distribución por área")
                        area_counts = processed_df['Area'].value_counts()
                        for area, count in area_counts.items():
                            st.write(f"- **{area}**: {count} cursos/talleres")
                    
                    # Mostrar lista de cursos estandarizados
                    if 'Nombre_Estandarizado' in processed_df.columns:
                        st.write("### Cursos estandarizados")
                        with st.expander("Ver lista de cursos estandarizados"):
                            for nombre in sorted(processed_df['Nombre_Estandarizado'].unique()):
                                st.write(f"- {nombre}")
        
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
    else:
        st.info("Por favor, carga un archivo con datos de cursos para comenzar.")

def process_courses_data(df, curso_column, area_column, nivel_column, estandarizar_nombres, verificar_duplicados):
    """
    Procesa y estandariza los datos de cursos.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de cursos cargados.
        curso_column (str): Nombre de la columna que contiene los nombres de los cursos.
        area_column (str): Nombre de la columna que contiene el área del curso.
        nivel_column (str): Nombre de la columna que contiene el nivel educativo del curso.
        estandarizar_nombres (bool): Si se deben estandarizar los nombres de los cursos.
        verificar_duplicados (bool): Si se deben verificar y eliminar duplicados.
        
    Returns:
        pd.DataFrame: DataFrame con los datos procesados y estandarizados.
    """
    # Crear una copia para no modificar el original
    processed_df = df.copy()
    
    # Inicializar nuevo DataFrame para cursos procesados
    courses_data = []
    
    # Procesar según las columnas seleccionadas
    if curso_column != "Ninguna":
        # Obtener valores únicos de la columna de cursos
        cursos = processed_df[curso_column].dropna().unique()
        
        for curso in cursos:
            # Información base del curso
            course_info = {"Nombre_Original": curso}
            
            # Estandarizar nombre si es necesario
            if estandarizar_nombres:
                course_info["Nombre_Estandarizado"] = estandarizar_nombre_curso(curso)
            else:
                course_info["Nombre_Estandarizado"] = curso
            
            # Determinar el área si está disponible
            if area_column != "Ninguna":
                # Encontrar el área para este curso
                curso_rows = processed_df[processed_df[curso_column] == curso]
                if not curso_rows.empty and area_column in curso_rows.columns:
                    areas = curso_rows[area_column].dropna().unique()
                    if len(areas) > 0:
                        # Usar la primera área encontrada o combinar si hay múltiples
                        area = areas[0] if len(areas) == 1 else ", ".join(areas)
                        course_info["Area"] = estandarizar_area(area)
            
            # Determinar nivel educativo si está disponible
            if nivel_column != "Ninguna":
                # Encontrar el nivel para este curso
                curso_rows = processed_df[processed_df[curso_column] == curso]
                if not curso_rows.empty and nivel_column in curso_rows.columns:
                    niveles = curso_rows[nivel_column].dropna().unique()
                    if len(niveles) > 0:
                        # Usar el primer nivel encontrado o combinar si hay múltiples
                        nivel = niveles[0] if len(niveles) == 1 else ", ".join(niveles)
                        course_info["Nivel_Educativo"] = estandarizar_nivel_educativo(nivel)
            
            # Agregar a la lista de cursos
            courses_data.append(course_info)
    
    # Crear nuevo DataFrame con los datos procesados
    result_df = pd.DataFrame(courses_data)
    
    # Eliminación de duplicados si es necesario
    if verificar_duplicados and not result_df.empty:
        # Verificar duplicados basados en el nombre estandarizado
        initial_rows = len(result_df)
        result_df = result_df.drop_duplicates(subset=['Nombre_Estandarizado'])
        removed_rows = initial_rows - len(result_df)
        st.write(f"- Se eliminaron {removed_rows} cursos duplicados.")
    
    # Deducir área si no se especificó
    if 'Area' not in result_df.columns and 'Nombre_Estandarizado' in result_df.columns:
        result_df['Area'] = result_df['Nombre_Estandarizado'].apply(deducir_area_desde_nombre)
    
    return result_df

# Funciones auxiliares para la identificación de columnas
def identificar_columnas_curso(df):
    """Identifica columnas que probablemente contengan nombres de cursos."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['curso', 'course', 'taller', 'workshop', 'asignatura', 'subject', 'materia'])]

def identificar_columnas_area(df):
    """Identifica columnas que probablemente contengan el área del curso."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['área', 'area', 'categoría', 'categoria', 'category', 'tipo', 'type'])]

def identificar_columnas_nivel(df):
    """Identifica columnas que probablemente contengan el nivel educativo."""
    return [col for col in df.columns if any(term in col.lower() for term in 
                                            ['nivel', 'level', 'grado', 'grade', 'educativo', 'educational'])]

def estandarizar_nombre_curso(nombre):
    """
    Estandariza el nombre del curso/taller.
    
    Args:
        nombre (str): Nombre original del curso
        
    Returns:
        str: Nombre estandarizado
    """
    if pd.isna(nombre):
        return ""
    
    # Convertir a string y eliminar espacios extras
    nombre = ' '.join(str(nombre).split())
    
    # Convertir a título (primera letra mayúscula)
    nombre = nombre.title()
    
    # Correcciones específicas
    nombre_estandarizado = nombre
    
    # Standardizar "Matematica" y sus variantes
    if re.search(r'Matem[aá]ticas?', nombre, re.IGNORECASE) or re.search(r'Math', nombre, re.IGNORECASE):
        nombre_estandarizado = "Matemática"
    
    # Standardizar "Comunicacion" y sus variantes
    elif re.search(r'Comunicaci[oó]n', nombre, re.IGNORECASE) or re.search(r'Lenguaje', nombre, re.IGNORECASE):
        nombre_estandarizado = "Comunicación"
    
    # Standardizar "Ingles" y sus variantes
    elif re.search(r'Ingl[eé]s', nombre, re.IGNORECASE) or re.search(r'English', nombre, re.IGNORECASE):
        nombre_estandarizado = "Inglés"
    
    # Standardizar "Dibujo y Pintura" y sus variantes
    elif re.search(r'Dibujo', nombre, re.IGNORECASE) or re.search(r'Pintura', nombre, re.IGNORECASE):
        nombre_estandarizado = "Dibujo y Pintura"
    
    # Standardizar "Musica" y sus variantes
    elif re.search(r'M[uú]sica', nombre, re.IGNORECASE) or re.search(r'Music', nombre, re.IGNORECASE):
        nombre_estandarizado = "Música"
    
    # Standardizar "Teatro" y sus variantes
    elif re.search(r'Teatro', nombre, re.IGNORECASE) or re.search(r'Drama', nombre, re.IGNORECASE):
        nombre_estandarizado = "Teatro"
    
    # Standardizar "Danza" y sus variantes
    elif re.search(r'Danza', nombre, re.IGNORECASE) or re.search(r'Baile', nombre, re.IGNORECASE):
        nombre_estandarizado = "Danza"
    
    # Standardizar "Cuenta cuentos" y sus variantes
    elif re.search(r'Cuenta', nombre, re.IGNORECASE) and re.search(r'Cuento', nombre, re.IGNORECASE):
        nombre_estandarizado = "Cuenta cuentos"
    
    # Standardizar "Oratoria" y sus variantes
    elif re.search(r'Oratoria', nombre, re.IGNORECASE) or re.search(r'Debate', nombre, re.IGNORECASE):
        nombre_estandarizado = "Oratoria"
    
    return nombre_estandarizado

def estandarizar_area(area_texto):
    """
    Estandariza el nombre del área.
    
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
    elif 'bienest' in area_texto or 'psico' in area_texto:
        return 'Bienestar Psicológico'
    else:
        return area_texto.title()  # Devolver con primera letra mayúscula si no coincide

def estandarizar_nivel_educativo(nivel_texto):
    """
    Estandariza el nivel educativo.
    
    Args:
        nivel_texto (str): Texto que describe el nivel educativo
        
    Returns:
        str: Nivel educativo estandarizado
    """
    if pd.isna(nivel_texto):
        return ""
    
    nivel_texto = str(nivel_texto).lower()
    
    niveles = []
    
    # Primaria
    if '1' in nivel_texto and 'primaria' in nivel_texto or '2' in nivel_texto and 'primaria' in nivel_texto:
        niveles.append("Primaria (1° y 2° grado)")
    
    if '3' in nivel_texto and 'primaria' in nivel_texto or '4' in nivel_texto and 'primaria' in nivel_texto:
        niveles.append("Primaria (3° y 4° grado)")
    
    if '5' in nivel_texto and 'primaria' in nivel_texto or '6' in nivel_texto and 'primaria' in nivel_texto:
        niveles.append("Primaria (5° y 6° grado)")
    
    # Si solo dice "primaria" sin especificar grados, incluir todos
    if 'primaria' in nivel_texto and not any(str(i) in nivel_texto for i in range(1, 7)):
        niveles.extend([
            "Primaria (1° y 2° grado)",
            "Primaria (3° y 4° grado)",
            "Primaria (5° y 6° grado)"
        ])
    
    # Secundaria
    if ('1' in nivel_texto and 'secundaria' in nivel_texto or 
        '2' in nivel_texto and 'secundaria' in nivel_texto or 
        '3' in nivel_texto and 'secundaria' in nivel_texto):
        niveles.append("Secundaria (1°, 2° y 3° grado)")
    
    if ('4' in nivel_texto and 'secundaria' in nivel_texto or 
        '5' in nivel_texto and 'secundaria' in nivel_texto):
        niveles.append("Secundaria (4° y 5° grado)")
    
    # Si solo dice "secundaria" sin especificar grados, incluir todos
    if 'secundaria' in nivel_texto and not any(str(i) in nivel_texto for i in range(1, 6)):
        niveles.extend([
            "Secundaria (1°, 2° y 3° grado)",
            "Secundaria (4° y 5° grado)"
        ])
    
    # Si no se pudo detectar, devolver el texto original
    if not niveles:
        return nivel_texto
    
    return ", ".join(niveles)

def deducir_area_desde_nombre(nombre_curso):
    """
    Deduce el área a la que pertenece un curso basado en su nombre.
    
    Args:
        nombre_curso (str): Nombre estandarizado del curso
        
    Returns:
        str: Área deducida
    """
    if pd.isna(nombre_curso):
        return ""
    
    nombre_curso = str(nombre_curso).lower()
    
    # Cursos típicos de Arte & Cultura
    arte_cultura_cursos = ['dibujo', 'pintura', 'música', 'musica', 'danza', 'teatro', 'cuenta cuentos', 'oratoria']
    
    # Cursos típicos de Asesoría a Colegios Nacionales
    asesoria_cursos = ['matemática', 'matematica', 'comunicación', 'comunicacion', 'inglés', 'ingles']
    
    # Verificar si el nombre del curso contiene alguno de los términos
    if any(curso in nombre_curso for curso in arte_cultura_cursos):
        return 'Arte & Cultura'
    elif any(curso in nombre_curso for curso in asesoria_cursos):
        return 'Asesoría a Colegios Nacionales'
    elif 'psico' in nombre_curso or 'emocional' in nombre_curso:
        return 'Bienestar Psicológico'
    else:
        return 'No definido' 