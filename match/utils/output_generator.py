"""
Funciones para generar los archivos Excel de salida con los resultados del match.
"""
import pandas as pd
from io import BytesIO
from typing import Set, Optional, List

# Definir columnas deseadas y orden para el reporte final de asignaciones
ASSIGNED_OUTPUT_COLUMNS_ORDER = [
    'ID Ruru', 'ID Yaku', 'Nombre Ruru', 'Nombre Yaku', 'Area',
    'Asignatura/Taller Asignado', 'Grado Original Ruru', 'Score Match',
    # Horarios (mostrar todos para comparación manual si es necesario)
    'Horario Lunes Yaku', 'Horario Lunes Ruru',
    'Horario Martes Yaku', 'Horario Martes Ruru',
    'Horario Miercoles Yaku', 'Horario Miercoles Ruru',
    'Horario Jueves Yaku', 'Horario Jueves Ruru',
    'Horario Viernes Yaku', 'Horario Viernes Ruru',
    'Horario Sabado Yaku', 'Horario Sabado Ruru',
    'Horario Domingo Yaku', 'Horario Domingo Ruru',
    # Información adicional Ruru
    'Nombre Apoderado Ruru', 'Celular Apoderado Ruru', 'Celular Asesoria Ruru', 'DNI Ruru',
    # Información adicional Yaku
    'Correo Yaku', 'Celular Yaku', 'DNI Yaku', 'Quechua Yaku', 'Quechua Ruru'
]

# Columnas para reportes de no asignados
UNASSIGNED_YAKU_COLS = ['yaku_id', 'nombre', 'dni', 'correo', 'celular', 'area', 'grado', 'quechua', 'asignatura', 'taller', 'horario_lunes', 'horario_martes', 'horario_miercoles', 'horario_jueves', 'horario_viernes', 'horario_sabado', 'horario_domingo']
UNASSIGNED_RURU_COLS = ['ID del estudiante:', 'nombre', 'apellido', 'DNI', 'area', 'grado_original', 'quechua', 'asignatura_opcion1', 'asignatura_opcion2', 'taller_opcion1', 'taller_opcion2', 'taller_opcion3', 'horario_lunes', 'horario_martes', 'horario_miercoles', 'horario_jueves', 'horario_viernes', 'horario_sabado', 'horario_domingo']

# --- MOVER clean_str_number AQUÍ ---
def clean_str_number(val):
    """Limpia números leídos de Excel/pandas, convirtiéndolos a string limpio."""
    if pd.isna(val) or val == '':
        return ''
    try:
        # Intentar convertir a entero primero para eliminar decimales/notación científica
        # Luego a string
        cleaned_val = str(int(float(str(val))))
    except (ValueError, TypeError):
        # Si falla (ej. ya es un string con caracteres no numéricos), usar el string original
        cleaned_val = str(val).strip()
    # Eliminar '.0' residual por si acaso (aunque int() debería quitarlo)
    if cleaned_val.endswith('.0'):
        cleaned_val = cleaned_val[:-2]
    return cleaned_val
# --- FIN MOVER clean_str_number ---


def format_assigned_output(
    assigned_df: pd.DataFrame,
    yakus_df: pd.DataFrame,
    rurus_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Prepara el DataFrame de asignados con información detallada y columnas ordenadas.

    Args:
        assigned_df: DataFrame con ('yaku_id', 'ruru_id', 'score').
        yakus_df: DataFrame completo de Yakus para el área (con 'yaku_id').
        rurus_df: DataFrame filtrado de Rurus para el área (con 'ID del estudiante:').

    Returns:
        DataFrame formateado para el reporte de asignaciones.
    """
    if assigned_df is None or assigned_df.empty:
        return pd.DataFrame(columns=ASSIGNED_OUTPUT_COLUMNS_ORDER)

    # 1. Merge para añadir datos del Yaku
    # Seleccionar columnas Yaku relevantes antes del merge para evitar duplicados innecesarios
    yaku_cols_to_merge = [
        'yaku_id', 'nombre', 'dni', 'correo', 'celular', 'area', 'quechua',
        'asignatura', 'taller', # Incluir asignatura/taller
        'horario_lunes', 'horario_martes', 'horario_miercoles', 'horario_jueves',
        'horario_viernes', 'horario_sabado', 'horario_domingo'
    ]
    # Asegurarse de que solo existan las columnas presentes en yakus_df
    yaku_cols_present = [col for col in yaku_cols_to_merge if col in yakus_df.columns]
    merged_df = pd.merge(assigned_df, yakus_df[yaku_cols_present], on='yaku_id', how='left')

    # 2. Merge para añadir datos del Ruru
    ruru_id_col = 'ID del estudiante:'
    ruru_cols_to_merge = [
        ruru_id_col, 'nombre', 'apellido', 'DNI', 'grado_original', 'quechua',
        'nombre_apoderado', 'apellido_apoderado', 'celular', 'celular_asesoria',
        'horario_lunes', 'horario_martes', 'horario_miercoles', 'horario_jueves',
        'horario_viernes', 'horario_sabado', 'horario_domingo'
    ]
    # Asegurarse de que solo existan las columnas presentes en rurus_df
    ruru_cols_present = [col for col in ruru_cols_to_merge if col in rurus_df.columns]
    # Usar 'ruru_id' (el ID en assigned_df) y ruru_id_col (el ID en rurus_df)
    merged_df = pd.merge(merged_df, rurus_df[ruru_cols_present], left_on='ruru_id', right_on=ruru_id_col, how='left', suffixes=('_yaku', '_ruru'))

    # 3. Crear columnas combinadas y renombrar
    merged_df['Nombre Ruru'] = merged_df['nombre_ruru'].fillna('') + ' ' + merged_df['apellido'].fillna('')
    merged_df['Nombre Yaku'] = merged_df['nombre_yaku'] # Ya viene completo
    merged_df['Nombre Apoderado Ruru'] = merged_df['nombre_apoderado'].fillna('') + ' ' + merged_df['apellido_apoderado'].fillna('')
    merged_df['Grado Original Ruru'] = merged_df['grado_original']
    merged_df['Area'] = merged_df['area'] # Viene del Yaku
    merged_df['Score Match'] = merged_df['score']
    merged_df['ID Ruru'] = merged_df['ruru_id']
    merged_df['ID Yaku'] = merged_df['yaku_id']
    merged_df['DNI Ruru'] = merged_df.get('DNI', '').apply(clean_str_number)
    merged_df['DNI Yaku'] = merged_df.get('dni', '').apply(clean_str_number)
    merged_df['Celular Yaku'] = merged_df.get('celular_yaku', '').apply(clean_str_number)
    merged_df['Celular Apoderado Ruru'] = merged_df.get('celular_ruru', '').apply(clean_str_number)
    merged_df['Celular Asesoria Ruru'] = merged_df.get('celular_asesoria', '').apply(clean_str_number)
    merged_df['Correo Yaku'] = merged_df['correo']
    merged_df['Quechua Yaku'] = merged_df['quechua_yaku']
    merged_df['Quechua Ruru'] = merged_df['quechua_ruru']

    # Renombrar columnas de horarios para claridad
    for dia in ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]:
        merged_df[f'Horario {dia.capitalize()} Yaku'] = merged_df.get(f'horario_{dia}_yaku', pd.NA)
        merged_df[f'Horario {dia.capitalize()} Ruru'] = merged_df.get(f'horario_{dia}_ruru', pd.NA)

    # Crear columna Asignatura/Taller
    if 'asignatura' in merged_df.columns:
        merged_df['Asignatura/Taller Asignado'] = merged_df['asignatura']
    elif 'taller' in merged_df.columns:
        merged_df['Asignatura/Taller Asignado'] = merged_df['taller']
    else:
        merged_df['Asignatura/Taller Asignado'] = "N/A" # Para Bienestar


    # 4. Seleccionar y ordenar columnas finales
    final_columns_present = [col for col in ASSIGNED_OUTPUT_COLUMNS_ORDER if col in merged_df.columns]
    final_df = merged_df[final_columns_present].copy()

    return final_df

def format_unassigned_output(
    unassigned_ids: Set[str],
    original_df: pd.DataFrame,
    id_column: str,
    output_columns: List[str]
) -> pd.DataFrame:
    """Prepara el DataFrame de no asignados con columnas relevantes."""
    if not unassigned_ids or original_df is None or original_df.empty:
        return pd.DataFrame()

    # Filtrar el DF original por los IDs no asignados
    unassigned_df = original_df[original_df[id_column].isin(unassigned_ids)].copy()

    # Seleccionar solo las columnas relevantes para el output
    # Asegurarse de que solo seleccionamos columnas que existen en el DF
    final_columns = [col for col in output_columns if col in unassigned_df.columns]
    final_unassigned_df = unassigned_df[final_columns].copy()

    # --- FORZAR TIPO STRING y Limpiar para DNI/Celulares (Revisado) ---
    # Se usa la función definida a nivel de módulo
    cols_to_str = ['DNI', 'dni', 'celular', 'celular_asesoria']
    for col in cols_to_str:
        if col in final_unassigned_df.columns:
            final_unassigned_df[col] = final_unassigned_df[col].apply(clean_str_number)
    # --- FIN FORZAR TIPO ---

    return final_unassigned_df


def generate_excel_output(
    assigned_df: pd.DataFrame,
    unassigned_yakus_df: pd.DataFrame,
    unassigned_rurus_df: pd.DataFrame
) -> BytesIO:
    """
    Genera un archivo Excel en memoria con hojas separadas para los resultados.

    Args:
        assigned_df: DataFrame formateado de asignaciones.
        unassigned_yakus_df: DataFrame formateado de Yakus no asignados.
        unassigned_rurus_df: DataFrame formateado de Rurus no asignados.

    Returns:
        BytesIO object conteniendo el archivo Excel.
    """
    output_buffer = BytesIO()
    with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:
        if assigned_df is not None and not assigned_df.empty:
            assigned_df.to_excel(writer, sheet_name='Asignaciones', index=False)
        else:
             pd.DataFrame([{"Resultado": "No se realizaron asignaciones"}]).to_excel(writer, sheet_name='Asignaciones', index=False)

        if unassigned_yakus_df is not None and not unassigned_yakus_df.empty:
            unassigned_yakus_df.to_excel(writer, sheet_name='Yakus No Asignados', index=False)
        else:
            pd.DataFrame([{"Resultado": "Todos los Yakus fueron asignados o no había Yakus"}]).to_excel(writer, sheet_name='Yakus No Asignados', index=False)

        if unassigned_rurus_df is not None and not unassigned_rurus_df.empty:
            unassigned_rurus_df.to_excel(writer, sheet_name='Rurus No Asignados', index=False)
        else:
            pd.DataFrame([{"Resultado": "Todos los Rurus fueron asignados o no había Rurus compatibles"}]).to_excel(writer, sheet_name='Rurus No Asignados', index=False)

    # El writer guarda en el buffer al salir del 'with'
    output_buffer.seek(0) # Mover el cursor al inicio del buffer para lectura
    return output_buffer 