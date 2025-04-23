"""
Funciones para calcular la compatibilidad y puntuación entre Yakus y Rurus.
"""
import pandas as pd

def check_schedule_compatibility(yaku_schedule_series, ruru_schedule_series) -> int:
    """Calcula el número de bloques horarios semanales coincidentes."""
    # Comparar horario_lunes, horario_martes... entre yaku y ruru
    pass

def check_quechua_compatibility(yaku_quechua, ruru_quechua) -> bool:
    """Verifica si el nivel de quechua es compatible."""
    pass

def check_subject_taller_compatibility(yaku_item, ruru_options_list, area) -> int:
    """Verifica compatibilidad de asignatura/taller y devuelve prioridad (1, 2, 3 o 0)."""
    # Lógica diferente para ACN (asignatura) y Arte (taller)
    pass

def calculate_match_score(yaku_row, ruru_row, area) -> float:
    """Calcula un puntaje numérico para un par (Yaku, Ruru)."""
    # Debe devolver 0 si no hay al menos 1 horario coincidente.
    # Ponderar: >=2 horarios > quechua > asignatura/taller
    pass

def create_score_matrix(yakus_df, rurus_df, area):
    """Calcula la matriz de puntuación para todos los pares Yaku-Ruru posibles."""
    # Iterar sobre todos los pares, llamar a calculate_match_score
    pass 