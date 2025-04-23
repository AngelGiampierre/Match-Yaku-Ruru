"""
Funciones para calcular la compatibilidad y puntuación entre Yakus y Rurus.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import streamlit as st
import re

# --- Constantes de Puntuación (Ajustables) ---
# Estos pesos reflejan las prioridades discutidas
SCORE_SCHEDULE_BASE = 1.0  # Puntuación mínima por tener al menos 1 horario coincidente
SCORE_SCHEDULE_BONUS_2PLUS = 10.0 # Bonus grande por >= 2 horarios
SCORE_QUECHUA_COMPATIBLE = 5.0   # Bonus medio por compatibilidad de quechua
SCORE_SUBJECT_PRIO_1 = 3.0     # Bonus bajo por asignatura/taller Prio 1
SCORE_SUBJECT_PRIO_2 = 2.0     # Bonus menor por Prio 2
SCORE_SUBJECT_PRIO_3 = 1.0     # Bonus mínimo por Prio 3 (solo Arte)

# Niveles de Quechua para comparación
QUECHUA_NO_HABLA = ["No lo hablo"]
QUECHUA_BASICO = ["Nivel básico"]
QUECHUA_INTERMEDIO_AVANZADO = ["Nivel intermedio", "Nivel avanzado", "Nativo"]

# Columnas de horarios
HORARIO_COLS = [f"horario_{dia}" for dia in ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]]

# --- Funciones de Compatibilidad ---

def _parse_schedule_string(schedule_str: str) -> set:
    """Convierte el string de horarios de un día en un set de bloques."""
    if pd.isna(schedule_str) or schedule_str.strip().lower() in ["", "no disponible"]:
        return set()
    # Extraer bloques como "Mañana (8am -12 m)"
    # Usamos regex para ser un poco más robustos a espacios extra
    blocks = re.findall(r"(Mañana\s*\(.*?\)|\s*Tarde\s*\(.*?\)|\s*Noche\s*\(.*?\))", schedule_str)
    # Limpiar espacios extra de cada bloque encontrado
    return set(block.strip() for block in blocks)

def check_schedule_compatibility(yaku_row: pd.Series, ruru_row: pd.Series) -> int:
    """Calcula el número de bloques horarios semanales coincidentes."""
    total_matching_blocks = 0
    for col in HORARIO_COLS:
        yaku_blocks = _parse_schedule_string(yaku_row.get(col, ""))
        ruru_blocks = _parse_schedule_string(ruru_row.get(col, ""))
        # Contar bloques comunes para este día
        total_matching_blocks += len(yaku_blocks.intersection(ruru_blocks))
    return total_matching_blocks

def check_quechua_compatibility(yaku_quechua: Optional[str], ruru_quechua: Optional[str]) -> bool:
    """Verifica si el nivel de quechua es compatible (Ruru Básico+ -> Yaku Intermedio+)."""
    # Normalizar valores NaN o vacíos a "No lo hablo"
    yaku_level = yaku_quechua if pd.notna(yaku_quechua) and yaku_quechua.strip() else "No lo hablo"
    ruru_level = ruru_quechua if pd.notna(ruru_quechua) and ruru_quechua.strip() else "No lo hablo"

    # Si Ruru es Básico o superior, Yaku debe ser Intermedio o superior
    if ruru_level in QUECHUA_BASICO or ruru_level in QUECHUA_INTERMEDIO_AVANZADO:
        return yaku_level in QUECHUA_INTERMEDIO_AVANZADO
    # Si Ruru no habla o es básico, no hay requisito estricto para Yaku
    return True # Compatible por defecto si Ruru no requiere nivel alto de Yaku

def _clean_taller_name(taller_str: str) -> str:
    """Elimina notas como (con internet) / (sin internet) del nombre del taller."""
    if pd.isna(taller_str):
        return ""
    # Convertir a string, eliminar espacios extra al inicio/final
    cleaned = str(taller_str).strip()
    # Eliminar paréntesis y su contenido (si contienen 'internet')
    cleaned = re.sub(r'\s*\((?:con|sin)\s+internet\)\s*$', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip().lower() # Devolver en minúsculas y sin espacios finales

def check_subject_taller_compatibility(yaku_row: pd.Series, ruru_row: pd.Series, area: str) -> int:
    """Verifica compatibilidad de asignatura/taller y devuelve prioridad (1, 2, 3 o 0)."""
    if area == "Asesoría a Colegios Nacionales":
        yaku_subjects_str = yaku_row.get('asignatura', '')
        yaku_subjects_str = str(yaku_subjects_str) if pd.notna(yaku_subjects_str) else ''
        yaku_subjects = set(subj.strip() for subj in yaku_subjects_str.lower().split(',') if subj.strip())

        ruru_prio1 = str(ruru_row.get('asignatura_opcion1', '')) if pd.notna(ruru_row.get('asignatura_opcion1')) else ''
        ruru_prio2 = str(ruru_row.get('asignatura_opcion2', '')) if pd.notna(ruru_row.get('asignatura_opcion2')) else ''

        if ruru_prio1.strip().lower() in yaku_subjects:
            return 1
        elif ruru_prio2.strip().lower() in yaku_subjects:
            return 2
        else:
            return 0
    elif area == "Arte & Cultura":
        # Limpiar nombre del taller del Yaku
        yaku_taller = _clean_taller_name(yaku_row.get('taller', ''))

        # Limpiar nombres de las opciones de taller del Ruru
        ruru_prio1_clean = _clean_taller_name(ruru_row.get('taller_opcion1', ''))
        ruru_prio2_clean = _clean_taller_name(ruru_row.get('taller_opcion2', ''))
        ruru_prio3_clean = _clean_taller_name(ruru_row.get('taller_opcion3', ''))

        # Comparar usando los nombres limpios
        if yaku_taller and yaku_taller == ruru_prio1_clean:
            return 1
        elif yaku_taller and yaku_taller == ruru_prio2_clean:
            return 2
        elif yaku_taller and yaku_taller == ruru_prio3_clean:
            return 3
        else:
            return 0
    else: # Bienestar Psicológico u otras áreas
        return 0

# --- Función Principal de Puntuación ---

def calculate_match_score(yaku_row: pd.Series, ruru_row: pd.Series, area: str) -> float:
    """Calcula un puntaje numérico para un par (Yaku, Ruru)."""
    score = 0.0

    # 1. Compatibilidad de Horarios (Requisito Mínimo)
    schedule_matches = check_schedule_compatibility(yaku_row, ruru_row)
    if schedule_matches == 0:
        return 0.0 # No hay coincidencia horaria, puntaje es 0

    # Puntuación base por coincidencia horaria
    score += SCORE_SCHEDULE_BASE

    # Bonus por >= 2 horarios
    if schedule_matches >= 2:
        score += SCORE_SCHEDULE_BONUS_2PLUS

    # 2. Compatibilidad de Quechua
    quechua_compatible = check_quechua_compatibility(yaku_row.get('quechua'), ruru_row.get('quechua'))
    if quechua_compatible:
        score += SCORE_QUECHUA_COMPATIBLE

    # 3. Compatibilidad Asignatura/Taller (si aplica al área)
    if area in ["Asesoría a Colegios Nacionales", "Arte & Cultura"]:
        subject_prio = check_subject_taller_compatibility(yaku_row, ruru_row, area)
        if subject_prio == 1:
            score += SCORE_SUBJECT_PRIO_1
        elif subject_prio == 2:
            score += SCORE_SUBJECT_PRIO_2
        elif subject_prio == 3: # Solo aplica a Arte
            score += SCORE_SUBJECT_PRIO_3

    return round(score, 2) # Redondear para evitar problemas de precisión flotante

# --- Función para Crear Lista de Scores ---

def create_scores_list(yakus_df: pd.DataFrame, rurus_df: pd.DataFrame, area: str) -> List[Dict[str, Any]]:
    """Calcula la puntuación para todos los pares Yaku-Ruru posibles y devuelve una lista."""
    scores_list = []
    total_pairs = len(yakus_df) * len(rurus_df)
    progress_bar = st.progress(0)
    processed_pairs = 0

    st.info(f"Calculando puntuaciones para {total_pairs} pares posibles...")

    # IDs para referencia
    yaku_id_col = 'yaku_id' # Asumiendo que esta columna fue creada por data_loader
    ruru_id_col = 'ID del estudiante:'

    for idx_y, yaku_row in yakus_df.iterrows():
        for idx_r, ruru_row in rurus_df.iterrows():
            # Calcular puntaje
            score = calculate_match_score(yaku_row, ruru_row, area)

            # Guardar solo si el puntaje es > 0 (cumple el mínimo de horario)
            if score > 0:
                scores_list.append({
                    'yaku_id': yaku_row[yaku_id_col],
                    'ruru_id': ruru_row[ruru_id_col],
                    'score': score,
                    # Opcional: añadir detalles del match para referencia futura
                    # 'schedule_matches': schedule_matches,
                    # 'quechua_match': quechua_compatible,
                    # 'subject_prio': subject_prio if area in [...] else 0
                })

            processed_pairs += 1
            # Actualizar barra de progreso (con menos frecuencia para rendimiento)
            if processed_pairs % 100 == 0 or processed_pairs == total_pairs:
                 progress = min(1.0, processed_pairs / total_pairs)
                 progress_bar.progress(progress)

    progress_bar.empty() # Limpiar barra de progreso
    st.success(f"Cálculo de puntuaciones finalizado. Se encontraron {len(scores_list)} pares compatibles.")
    return scores_list 