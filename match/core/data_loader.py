"""
Funciones para cargar y preparar los datos de Yakus y Rurus para el match.
"""
import pandas as pd
import streamlit as st # Para mensajes de error/advertencia

# Placeholder para las funciones
def load_yaku_data(uploaded_file, expected_area):
    """Carga, valida y prepara datos de Yakus."""
    # Leer excel, verificar columnas, validar área, generar ID Yaku
    pass

def load_ruru_data(uploaded_file):
    """Carga y valida datos de Rurus preprocesados."""
    # Leer excel, verificar columnas necesarias
    pass

def filter_rurus_by_area(ruru_df, area):
    """Filtra el DataFrame de Rurus por el área seleccionada."""
    pass

def generate_yaku_ids(yaku_df, start_id=25001):
    """Genera IDs secuenciales para los Yakus."""
    pass 