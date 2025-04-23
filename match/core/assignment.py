"""
Algoritmo para encontrar la asignación óptima 1-a-1 Yaku-Ruru.
"""
import pandas as pd
from typing import List, Dict, Any, Tuple, Set

def find_best_matches(
    yakus_df: pd.DataFrame,
    rurus_df: pd.DataFrame,
    scores_list: List[Dict[str, Any]]
) -> Tuple[pd.DataFrame, Set[str], Set[str]]:
    """
    Implementa un algoritmo greedy para encontrar la mejor asignación 1-a-1.

    Args:
        yakus_df: DataFrame completo de Yakus para el área.
        rurus_df: DataFrame filtrado de Rurus para el área.
        scores_list: Lista de diccionarios, cada uno con 'yaku_id', 'ruru_id', 'score'.

    Returns:
        - DataFrame con las asignaciones finales ('yaku_id', 'ruru_id', 'score').
        - Set de IDs de Yakus no asignados.
        - Set de IDs de Rurus no asignados.
    """
    if not scores_list:
        # Si no hay pares compatibles, devolver todo como no asignado
        all_yaku_ids = set(yakus_df['yaku_id'].unique())
        all_ruru_ids = set(rurus_df['ID del estudiante:'].unique())
        return pd.DataFrame(columns=['yaku_id', 'ruru_id', 'score']), all_yaku_ids, all_ruru_ids

    # 1. Ordenar los scores de mayor a menor
    sorted_scores = sorted(scores_list, key=lambda x: x['score'], reverse=True)

    # 2. Inicializar conjuntos para llevar registro de asignados
    assigned_yakus: Set[str] = set()
    assigned_rurus: Set[str] = set()
    final_assignments: List[Dict[str, Any]] = []

    # 3. Iterar y asignar (Algoritmo Greedy)
    for potential_match in sorted_scores:
        yaku_id = potential_match['yaku_id']
        ruru_id = potential_match['ruru_id']

        # Verificar si ambos están disponibles
        if yaku_id not in assigned_yakus and ruru_id not in assigned_rurus:
            # Asignar!
            final_assignments.append(potential_match)
            assigned_yakus.add(yaku_id)
            assigned_rurus.add(ruru_id)

            # Opcional: Detener si ya hemos asignado a todos los posibles (ej, si Rurus < Yakus)
            # if len(assigned_rurus) == len(rurus_df):
            #    break
            # if len(assigned_yakus) == len(yakus_df):
            #    break

    # 4. Convertir a DataFrame
    assigned_df = pd.DataFrame(final_assignments)

    # 5. Identificar los no asignados
    all_yaku_ids = set(yakus_df['yaku_id'].unique())
    all_ruru_ids = set(rurus_df['ID del estudiante:'].unique())

    unassigned_yaku_ids = all_yaku_ids - assigned_yakus
    unassigned_ruru_ids = all_ruru_ids - assigned_rurus

    return assigned_df, unassigned_yaku_ids, unassigned_ruru_ids 