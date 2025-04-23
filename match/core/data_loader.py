"""
Funciones para cargar y preparar los datos de Yakus y Rurus para el match.
"""
import pandas as pd
import streamlit as st
from typing import List, Tuple, Optional

# --- Columnas Esperadas ---
# (Basado en los datos CSV proporcionados y preprocesamiento)

BASE_YAKU_COLS = [
    'area', 'correo', 'horario_lunes', 'horario_martes', 'horario_miercoles',
    'horario_jueves', 'horario_viernes', 'horario_sabado', 'horario_domingo',
    'grado', 'nombre', 'dni', 'quechua', 'celular'
]
ACN_YAKU_COLS = BASE_YAKU_COLS + ['asignatura']
ARTE_YAKU_COLS = BASE_YAKU_COLS + ['taller']
BIENESTAR_YAKU_COLS = BASE_YAKU_COLS # Sin columnas adicionales específicas

# Columnas Rurus (resultado del preprocesamiento)
RURU_COLS = [
    "ID del estudiante:", 'nombre', 'apellido', 'DNI', 'colegio',
    'Grado del estudiante:', 'idiomas', 'nombre_apoderado', 'apellido_apoderado',
    'celular', 'arte_y_cultura', 'bienestar_psicologico', 'asesoria_a_colegios_nacionales',
    'taller_opcion1', 'taller_opcion2', 'taller_opcion3', 'asignatura_opcion1',
    'asignatura_opcion2', 'celular_asesoria', 'area', 'horario_lunes',
    'horario_martes', 'horario_miercoles', 'horario_jueves', 'horario_viernes',
    'horario_sabado', 'horario_domingo', 'grado', 'grado_original', 'quechua'
]

# Mapeo de áreas a listas de columnas requeridas para Yakus
YAKU_COLS_MAP = {
    "Asesoría a Colegios Nacionales": ACN_YAKU_COLS,
    "Arte & Cultura": ARTE_YAKU_COLS,
    "Bienestar Psicológico": BIENESTAR_YAKU_COLS
}

# --- Funciones de Carga y Validación ---

def _validate_columns(df: pd.DataFrame, required_cols: List[str], file_type: str) -> bool:
    """Valida si un DataFrame contiene las columnas requeridas."""
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Error en archivo {file_type}: Faltan las siguientes columnas requeridas: {', '.join(missing_cols)}")
        return False
    return True

def generate_yaku_ids(yaku_df: pd.DataFrame, area: str) -> pd.DataFrame:
    """
    Genera IDs secuenciales para los Yakus en una nueva columna 'yaku_id',
    con un prefijo numérico basado en el área.
    """
    if yaku_df is None:
        return None

    # --- Lógica de ID inicial por Área ---
    start_offset = 0 # Default para Bienestar Psicológico
    if area == "Arte & Cultura":
        start_offset = 100
    elif area == "Asesoría a Colegios Nacionales":
        start_offset = 200

    base_start_id = 25000 # Mantenemos el prefijo 25
    start_id = base_start_id + start_offset + 1 # ID inicial para esta área (ej: 25001, 25101, 25201)
    # --- Fin Lógica ID ---

    # Crear IDs secuenciales con el prefijo YA
    yaku_df['yaku_id'] = [f"YA{start_id + i}" for i in range(len(yaku_df))]

    # Asegurarse de que la columna ID esté al principio
    cols = ['yaku_id'] + [col for col in yaku_df.columns if col != 'yaku_id']
    return yaku_df[cols]

def load_yaku_data(uploaded_file, expected_area: str) -> Optional[pd.DataFrame]:
    """Carga, valida y prepara datos de Yakus desde un archivo Excel."""
    if not uploaded_file:
        return None
    try:
        df = pd.read_excel(uploaded_file)

        # Limpiar nombres de columnas (quitar espacios extra)
        df.columns = df.columns.str.strip()

        # Obtener columnas requeridas para el área esperada
        required_cols = YAKU_COLS_MAP.get(expected_area)
        if not required_cols:
            st.error(f"❌ Error interno: Área '{expected_area}' no reconocida para definir columnas de Yakus.")
            return None

        # Validar columnas
        if not _validate_columns(df, required_cols, f"Yakus ({expected_area})"):
            return None

        # Validar que la columna 'area' coincide con la esperada
        if not df['area'].dropna().empty and not (df['area'].str.strip() == expected_area).all():
            areas_encontradas = df['area'].unique()
            st.warning(f"⚠️ Advertencia en archivo Yakus: Se esperaba el área '{expected_area}', pero se encontraron también: {areas_encontradas}. Se procederá, pero verifica el archivo.")
            # Opcional: filtrar estrictamente por área esperada
            # df = df[df['area'].str.strip() == expected_area].copy()

        # --- MODIFICADO: Pasar 'expected_area' a generate_yaku_ids ---
        df_with_ids = generate_yaku_ids(df, expected_area) # Pasar el área aquí
        # --- FIN MODIFICADO ---

        st.success(f"✅ Datos de Yakus ({expected_area}) cargados y validados correctamente.")
        return df_with_ids

    except Exception as e:
        st.error(f"❌ Error al leer el archivo Excel de Yakus: {e}")
        return None

def load_ruru_data(uploaded_file) -> Optional[pd.DataFrame]:
    """Carga y valida datos de Rurus preprocesados desde un archivo Excel."""
    if not uploaded_file:
        return None
    try:
        df = pd.read_excel(uploaded_file)

        # Limpiar nombres de columnas (quitar espacios extra)
        df.columns = df.columns.str.strip()

        # Validar columnas requeridas de Rurus
        if not _validate_columns(df, RURU_COLS, "Rurus"):
            return None

        st.success("✅ Datos de Rurus preprocesados cargados y validados correctamente.")
        return df

    except Exception as e:
        st.error(f"❌ Error al leer el archivo Excel de Rurus: {e}")
        return None

def filter_rurus_by_area(ruru_df: pd.DataFrame, area: str) -> pd.DataFrame:
    """Filtra el DataFrame de Rurus por el área seleccionada."""
    if ruru_df is None or 'area' not in ruru_df.columns:
        return pd.DataFrame() # Devuelve DataFrame vacío si hay error

    filtered_df = ruru_df[ruru_df['area'].str.strip() == area].copy()
    st.info(f"Filtrando Rurus por área '{area}'. Se encontraron {len(filtered_df)} Rurus.")
    return filtered_df 