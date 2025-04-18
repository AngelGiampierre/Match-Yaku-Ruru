"""
Utilidades compartidas entre todos los módulos de Match-Yaku-Ruru.

Contiene funciones y clases que pueden ser utilizadas por cualquier módulo
del sistema (preprocesamiento, match, email).
"""

# Importamos funciones de gestión de estado para exponerlas
from .session_state import (
    get_value,
    set_value,
    delete_value,
    has_value,
    get_all_values,
    clear_all_values
) 