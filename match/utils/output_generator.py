"""
Funciones para generar los archivos Excel de salida con los resultados del match.
"""
import pandas as pd
from io import BytesIO

def format_assigned_output(assigned_df, yakus_df, rurus_df):
    """Prepara el DataFrame de asignados con las columnas finales requeridas."""
    # Unir datos de Yakus/Rurus, seleccionar/renombrar columnas, incluir grado_original
    pass

def format_unassigned_output(unassigned_ids, original_df, id_column):
    """Prepara los DataFrames de no asignados."""
    pass

def generate_excel_output(assigned_df, unassigned_yakus_df, unassigned_rurus_df) -> BytesIO:
    """Genera un archivo Excel con múltiples hojas para los resultados."""
    # Crear un objeto BytesIO, usar pd.ExcelWriter, escribir DataFrames en hojas separadas
    pass 