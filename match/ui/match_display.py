"""
Funciones para mostrar los resultados del match en la interfaz de Streamlit.
"""
import streamlit as st
import pandas as pd

def display_match_results(
    assigned_df: pd.DataFrame,
    unassigned_yakus_df: pd.DataFrame,
    unassigned_rurus_df: pd.DataFrame
):
    """
    Muestra tablas y resúmenes de los resultados del match de forma organizada.

    Args:
        assigned_df: DataFrame formateado de asignaciones.
        unassigned_yakus_df: DataFrame formateado de Yakus no asignados.
        unassigned_rurus_df: DataFrame formateado de Rurus no asignados.
    """

    # 1. Mostrar Métricas Resumen
    st.subheader("Resumen de la Asignación")
    col1, col2, col3 = st.columns(3)
    num_assigned = len(assigned_df) if assigned_df is not None else 0
    num_unassigned_y = len(unassigned_yakus_df) if unassigned_yakus_df is not None else 0
    num_unassigned_r = len(unassigned_rurus_df) if unassigned_rurus_df is not None else 0

    with col1:
        st.metric("✅ Rurus Asignados", num_assigned)
    with col2:
        st.metric("⚠️ Yakus No Asignados", num_unassigned_y)
    with col3:
        st.metric("⚠️ Rurus No Asignados", num_unassigned_r)

    st.markdown("---") # Separador visual

    # 2. Mostrar Tabla de Asignaciones
    st.subheader("Tabla de Asignaciones")
    if assigned_df is not None and not assigned_df.empty:
        # Usar st.dataframe para interactividad (ordenar, filtrar)
        st.dataframe(assigned_df)
        st.caption(f"Total: {num_assigned} asignaciones.")
    else:
        st.info("No se encontraron asignaciones para mostrar.")

    st.markdown("---")

    # 3. Mostrar Tablas de No Asignados (en expanders)
    st.subheader("Detalle de No Asignados")

    with st.expander(f"Ver Yakus No Asignados ({num_unassigned_y})"):
        if unassigned_yakus_df is not None and not unassigned_yakus_df.empty:
            st.dataframe(unassigned_yakus_df)
        else:
            st.write("No hay Yakus no asignados para mostrar.")

    with st.expander(f"Ver Rurus No Asignados ({num_unassigned_r})"):
        if unassigned_rurus_df is not None and not unassigned_rurus_df.empty:
            st.dataframe(unassigned_rurus_df)
        else:
            st.write("No hay Rurus no asignados para mostrar.") 