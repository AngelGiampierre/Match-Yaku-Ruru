import pandas as pd
import re

def limpiar_texto(texto):
    """
    Limpia un texto eliminando espacios extras, normalizando mayúsculas/minúsculas
    y eliminando caracteres especiales.
    
    Args:
        texto (str): Texto a limpiar
        
    Returns:
        str: Texto limpio
    """
    if pd.isna(texto) or texto is None:
        return ""
    
    # Convertir a string si no lo es
    texto = str(texto)
    
    # Eliminar espacios en blanco al inicio y final
    texto = texto.strip()
    
    # Normalizar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto

def formatear_lista(lista_texto, separador=","):
    """
    Convierte un texto con elementos separados por un separador en una lista limpia.
    
    Args:
        lista_texto (str): Texto con elementos separados
        separador (str): Separador de elementos (por defecto: coma)
        
    Returns:
        list: Lista de elementos limpios
    """
    if pd.isna(lista_texto) or lista_texto is None or lista_texto == "":
        return []
    
    # Convertir a string si no lo es
    lista_texto = str(lista_texto)
    
    # Dividir por el separador y limpiar cada elemento
    elementos = [limpiar_texto(elemento) for elemento in lista_texto.split(separador)]
    
    # Eliminar elementos vacíos
    elementos = [elemento for elemento in elementos if elemento]
    
    return elementos

def estandarizar_opciones(opcion, mapeo_opciones=None):
    """
    Estandariza los nombres de las opciones según un mapeo.
    
    Args:
        opcion (str): Nombre de la opción a estandarizar
        mapeo_opciones (dict): Diccionario de equivalencias {variante: nombre_estandar}
        
    Returns:
        str: Nombre estandarizado de la opción
    """
    if mapeo_opciones is None:
        # Diccionario de equivalencias por defecto
        mapeo_opciones = {
            # Arte y Cultura
            "musica": "Música",
            "música": "Música",
            "dibujo": "Dibujo y Pintura",
            "pintura": "Dibujo y Pintura",
            "dibujo y pintura": "Dibujo y Pintura",
            "cuenta": "Cuenta cuentos",
            "cuentos": "Cuenta cuentos",
            "cuenta cuentos": "Cuenta cuentos",
            "cuentacuentos": "Cuenta cuentos",
            "danza": "Danza",
            "baile": "Danza",
            "teatro": "Teatro",
            "actuación": "Teatro",
            "actuacion": "Teatro",
            
            # Asesoría a Colegios
            "mate": "Matemática",
            "matematica": "Matemática",
            "matemática": "Matemática",
            "comuni": "Comunicación",
            "comunicacion": "Comunicación",
            "comunicación": "Comunicación",
            "ingles": "Inglés",
            "inglés": "Inglés",
            "english": "Inglés",
            
            # Bienestar Psicológico
            "psico": "Facilitador psicoeducativo",
            "facilitador": "Facilitador psicoeducativo",
            "psicoeduca": "Facilitador psicoeducativo",
            "facilitador psicoeducativo": "Facilitador psicoeducativo"
        }
    
    if pd.isna(opcion) or opcion is None or opcion == "":
        return ""
    
    # Convertir a string si no lo es
    opcion = str(opcion).lower().strip()
    
    # Buscar la mejor coincidencia en el mapeo
    for variante, estandar in mapeo_opciones.items():
        if variante in opcion:
            return estandar
    
    # Si no hay coincidencia, devolver la opción original con primera letra en mayúscula
    return opcion.capitalize()

def standardize_dni(dni_value):
    """
    Estandariza un valor de DNI/pasaporte para asegurar el formato correcto.
    
    Args:
        dni_value: Valor de DNI a estandarizar

    Returns:
        str: DNI estandarizado o mensaje de error
    """
    # Validar entrada
    if pd.isna(dni_value) or dni_value is None or dni_value == "":
        return "ERROR: DNI vacío"
    
    # Convertir siempre a string para evitar errores de PyArrow
    dni_str = str(dni_value).strip().upper()
    
    # Validar DNIs numéricos peruanos (exactamente 8 dígitos)
    if dni_str.isdigit():
        # Verificar que tenga exactamente 8 dígitos
        if len(dni_str) == 8:
            return dni_str
        else:
            return f"ERROR: DNI numérico debe tener 8 dígitos: {dni_str}"
    
    # Validar pasaportes (alfanuméricos, generalmente empiezan con letra)
    # Formato de pasaporte peruano: generalmente comienza con letra seguida de números
    # Otros pasaportes internacionales: variados formatos alfanuméricos
    elif re.match(r'^[A-Z][A-Z0-9]{7,14}$', dni_str):
        return dni_str
    else:
        return f"ERROR: Formato de DNI/pasaporte inválido: {dni_str}"

def validate_email(email):
    """
    Valida y estandariza un correo electrónico.
    
    Args:
        email (str): Correo electrónico a validar
        
    Returns:
        str: Correo electrónico estandarizado o mensaje de error
    """
    if pd.isna(email) or email is None or email == "":
        return "ERROR: Valor vacío"
    
    # Eliminar espacios y convertir a minúsculas
    email_str = str(email).strip().lower()
    
    # Patrón para validar correos
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email_str):
        return email_str
    else:
        return f"ERROR: Formato de correo inválido: {email_str}"

def standardize_phone_number(phone):
    """
    Estandariza y valida un número de teléfono.
    
    Args:
        phone (str): Número de teléfono a validar
        
    Returns:
        str: Número de teléfono estandarizado o mensaje de error
    """
    if pd.isna(phone) or phone is None or phone == "":
        return "ERROR: Valor vacío"
    
    # Convertir a string y eliminar caracteres no numéricos
    phone_str = str(phone)
    phone_clean = re.sub(r'[^\d]', '', phone_str)
    
    # Verificar si es un número de teléfono peruano válido (9 dígitos)
    if len(phone_clean) == 9 and phone_clean.startswith('9'):
        return phone_clean
    
    # Para números fijos u otros formatos (aceptamos entre 7 y 12 dígitos)
    elif 7 <= len(phone_clean) <= 12:
        return phone_clean
    
    else:
        return f"ERROR: Formato de teléfono inválido: {phone_str}"

def get_duplicated_dnis(dataframe, dni_column):
    """
    Identifica DNIs duplicados en un DataFrame.
    
    Args:
        dataframe (pd.DataFrame): DataFrame a analizar
        dni_column (str): Nombre de la columna de DNI
        
    Returns:
        pd.DataFrame: DataFrame con los DNIs duplicados
    """
    # Asegurar que el DNI sea string
    dataframe[dni_column] = dataframe[dni_column].astype(str)
    
    # Normalizar los DNIs aplicando la función standardize_dni a cada valor
    normalized_dnis = dataframe[dni_column].apply(standardize_dni)
    
    # Encontrar duplicados
    duplicated_dnis = normalized_dnis[normalized_dnis.duplicated(keep=False)]
    
    if duplicated_dnis.empty:
        return pd.DataFrame()
    
    # Devolver el DataFrame filtrado con los duplicados
    return dataframe[normalized_dnis.isin(duplicated_dnis)].copy()

def filter_by_area_and_selection(main_df, selection_df, area_column, dni_column, area_value):
    """
    Filtra un DataFrame principal para mantener solo las filas de una área específica
    que están presentes en un DataFrame de selección según el DNI.
    
    Args:
        main_df (pd.DataFrame): DataFrame principal con todos los datos
        selection_df (pd.DataFrame): DataFrame con los DNIs seleccionados
        area_column (str): Nombre de la columna de área en el DataFrame principal
        dni_column (str): Nombre de la columna de DNI en el DataFrame de selección
        area_value (str): Valor del área a filtrar
        
    Returns:
        tuple: (DataFrame filtrado, lista de DNIs no encontrados)
    """
    # Crear copias para no modificar los originales
    main_df = main_df.copy()
    selection_df = selection_df.copy()
    
    # Determinar la columna de DNI en el DataFrame principal
    main_dni_column = None
    if 'DNI_Validado' in main_df.columns:
        main_dni_column = 'DNI_Validado'
    else:
        # Buscar columna de DNI con detección automática
        for col in main_df.columns:
            col_norm = col.strip().lower()
            if 'dni' in col_norm or 'pasaporte' in col_norm or 'documento' in col_norm or 'doc' in col_norm:
                main_dni_column = col
                break
    
    if main_dni_column is None:
        raise ValueError("No se pudo encontrar una columna de DNI en el DataFrame principal")
    
    # Asegurar que el DNI sea string en ambos DataFrames
    main_df[main_dni_column] = main_df[main_dni_column].astype(str)
    selection_df[dni_column] = selection_df[dni_column].astype(str)
    
    # Normalizamos los DNIs en ambos DataFrames
    main_df['DNI_Normalizado'] = main_df[main_dni_column].apply(standardize_dni)
    selection_df['DNI_Normalizado'] = selection_df[dni_column].apply(standardize_dni)
    
    # ----- NUEVA PARTE: Verificar validez de DNIs en la lista de seleccionados -----
    # Filtrar DNIs inválidos (aquellos que contienen 'ERROR')
    invalid_dnis_mask = selection_df['DNI_Normalizado'].str.contains('ERROR', na=False)
    if invalid_dnis_mask.any():
        print(f"⚠️ Se encontraron {invalid_dnis_mask.sum()} DNIs inválidos en la lista de seleccionados.")
        # Eliminar los DNIs inválidos
        selection_df = selection_df[~invalid_dnis_mask]
        if selection_df.empty:
            raise ValueError("Todos los DNIs en la lista de seleccionados son inválidos")
    
    # Lista de DNIs seleccionados normalizados y válidos
    selected_dnis = selection_df['DNI_Normalizado'].unique().tolist()
    
    # ----- NUEVA PARTE: Actualizar cursos de Arte y Cultura si es necesario -----
    # Verificar si estamos trabajando con el área de Arte y Cultura
    is_arte_cultura = False
    arte_cultura_values = ['arte y cultura', 'arte', 'cultura', 'talleres artísticos']
    
    for ac_value in arte_cultura_values:
        if ac_value in area_value.lower():
            is_arte_cultura = True
            break
    
    if is_arte_cultura:
        print(f"🎨 Procesando área de Arte y Cultura: {area_value}")
        
        # Buscar columnas de curso/taller en ambos DataFrames
        course_cols_main = []
        for col in main_df.columns:
            col_lower = col.lower()
            if 'curso' in col_lower or 'taller' in col_lower or 'especialidad' in col_lower or 'asignatura' in col_lower:
                course_cols_main.append(col)
        
        course_cols_selection = []
        for col in selection_df.columns:
            col_lower = col.lower()
            if 'curso' in col_lower or 'taller' in col_lower or 'especialidad' in col_lower or 'asignatura' in col_lower:
                course_cols_selection.append(col)
        
        # Si encontramos columnas de curso en ambos DataFrames, procedemos a actualizar
        if course_cols_main and course_cols_selection:
            main_course_col = course_cols_main[0]
            selection_course_col = course_cols_selection[0]
            
            print(f"📚 Columna de curso en datos principales: {main_course_col}")
            print(f"📚 Columna de curso en lista de seleccionados: {selection_course_col}")
            
            # Iterar sobre los DNIs seleccionados para actualizar sus cursos
            for dni in selected_dnis:
                # Encontrar el curso en la lista de seleccionados
                selection_rows = selection_df[selection_df['DNI_Normalizado'] == dni]
                if not selection_rows.empty and selection_course_col in selection_rows.columns:
                    updated_course = selection_rows[selection_course_col].iloc[0]
                    
                    # Actualizar el curso en el DataFrame principal
                    main_rows = main_df[main_df['DNI_Normalizado'] == dni]
                    if not main_rows.empty:
                        for idx in main_rows.index:
                            # Solo actualizar si hay un cambio
                            current_course = main_df.loc[idx, main_course_col]
                            if current_course != updated_course and pd.notna(updated_course) and updated_course.strip() != "":
                                print(f"🔄 Actualizando curso para DNI {dni}: {current_course} → {updated_course}")
                                main_df.loc[idx, main_course_col] = updated_course
    
    # Filtramos: si es del área especificada, solo mantenemos si está en la lista de seleccionados
    mask_to_remove = (main_df[area_column] == area_value) & (~main_df['DNI_Normalizado'].isin(selected_dnis))
    
    # Identificar DNIs no encontrados (solo para los del área especificada)
    area_dnis = set(main_df[main_df[area_column] == area_value]['DNI_Normalizado'])
    selection_area_dnis = set(selected_dnis)
    not_found_dnis = selection_area_dnis - area_dnis
    
    # Eliminar las filas que cumplen la condición de eliminación
    filtered_df = main_df[~mask_to_remove].copy()
    
    # Eliminamos la columna temporal de DNI normalizado
    filtered_df.drop('DNI_Normalizado', axis=1, inplace=True)
    
    return filtered_df, list(not_found_dnis)

def validate_data(df, dni_column=None, email_column=None):
    """
    Valida los datos del DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos
        dni_column (str, optional): Nombre de la columna que contiene los DNI
        email_column (str, optional): Nombre de la columna que contiene los correos electrónicos

    Returns:
        tuple: (DataFrame con errores, DataFrame limpio)
    """
    df = df.copy()
    
    # Asegurar que el DataFrame no esté vacío
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # Forzar tipos de datos para evitar errores de conversión
    if dni_column and dni_column in df.columns:
        # Convertir DNI a string explícitamente
        df[dni_column] = df[dni_column].astype(str)
    
    if email_column and email_column in df.columns:
        # Convertir email a string explícitamente
        df[email_column] = df[email_column].astype(str)
    
    # Inicializar columnas de validación
    df['errores'] = ''
    df['es_valido'] = True
    
    # Validar DNI si existe la columna
    if dni_column and dni_column in df.columns:
        # Verificar formato de DNI (8 dígitos para peruanos, o formato de pasaporte para extranjeros)
        # Para DNI peruano: exactamente 8 dígitos
        # Para pasaportes u otros: permitir alfanuméricos
        is_valid_dni = df[dni_column].str.match(r'^[A-Z0-9]{8,15}$')
        
        # Marcar errores en DNI
        mask = ~is_valid_dni
        df.loc[mask, 'errores'] += f'Formato de {dni_column} inválido; '
        df.loc[mask, 'es_valido'] = False
    
    # Validar email si existe la columna
    if email_column and email_column in df.columns:
        # Verificar formato de correo electrónico
        is_valid_email = df[email_column].str.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Marcar errores en Email
        mask = ~is_valid_email
        df.loc[mask, 'errores'] += f'Formato de {email_column} inválido; '
        df.loc[mask, 'es_valido'] = False
    
    # Identificar duplicados en DNI si existe la columna
    if dni_column and dni_column in df.columns:
        duplicated_dni = df.duplicated(subset=[dni_column], keep=False)
        df.loc[duplicated_dni, 'errores'] += f'{dni_column} duplicado; '
        df.loc[duplicated_dni, 'es_valido'] = False
    
    # Eliminar el punto y coma final en los errores
    df['errores'] = df['errores'].str.rstrip('; ')
    
    # Separar filas con errores y filas limpias
    errores_df = df[~df['es_valido']].copy()
    clean_df = df[df['es_valido']].copy()
    
    # Eliminar columnas de validación en el DataFrame limpio
    if not clean_df.empty:
        clean_df = clean_df.drop(columns=['errores', 'es_valido'])
    
    return errores_df, clean_df 