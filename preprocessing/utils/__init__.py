"""
Utilidades para el preprocesamiento de datos.
"""

from preprocessing.utils.file_handler import (
    save_dataframe,
    get_temp_file_path,
    load_dataframe
)

from preprocessing.utils.session_state import (
    get_dataframe,
    set_dataframe,
    get_processing_step,
    set_processing_step
)

# Importamos funciones de almacenamiento temporal para exponerlas
from .temp_storage import save_data, load_data, list_temp_files, delete_temp_file

# Importamos funciones de manejo de archivos
from .file_io import (
    read_file, 
    save_excel, 
    save_csv, 
    save_temp_file, 
    load_temp_file, 
    detect_file_type
) 