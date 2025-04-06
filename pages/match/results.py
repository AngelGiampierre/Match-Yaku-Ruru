import streamlit as st
import pandas as pd
import io
from utils.match_algorithm import MatchMaker, ReportGenerator
from pages.match.data_loader import procesar_yakus, procesar_rurus

def resultados_page():
    """
    Página para mostrar los resultados del match
    """
    st.markdown("<h2 class='section-header'>Resultados del Match</h2>", unsafe_allow_html=True)
    
    if "ejecutar_match_clicked" not in st.session_state or not st.session_state["ejecutar_match_clicked"]:
        st.info("Primero debe cargar los datos y ejecutar el match en la sección 'Cargar Datos'.")
        return
    
    if "yaku_df" not in st.session_state or "ruru_df" not in st.session_state or "mapeo_yakus" not in st.session_state or "mapeo_rurus" not in st.session_state:
        st.warning("No se han cargado todos los datos necesarios.")
        return
    
    try:
        # Procesar datos y ejecutar match
        yakus = procesar_yakus(st.session_state["yaku_df"], st.session_state["mapeo_yakus"])
        rurus = procesar_rurus(st.session_state["ruru_df"], st.session_state["mapeo_rurus"])
        
        # Ejecutar el algoritmo de match
        matchmaker = MatchMaker()
        report_generator = ReportGenerator(matchmaker)
        
        mejor_asignacion, matches_secundarios, max_horas = matchmaker.encontrar_match(rurus, yakus)
        
        # Mostrar resultados
        st.markdown("<h3 class='subsection-header'>Matches Principales (2+ horas)</h3>", unsafe_allow_html=True)
        
        # Convertir mejor_asignacion a un DataFrame para mostrar
        if mejor_asignacion:
            matches_df = []
            for match in mejor_asignacion:
                ruru_nombre, yaku_nombre, opcion, interseccion, _ = match
                horas = matchmaker.calcular_horas_asignadas(interseccion)
                matches_df.append({
                    "Ruru": ruru_nombre,
                    "Yaku": yaku_nombre,
                    "Opción": opcion,
                    "Horas": horas
                })
            
            matches_df = pd.DataFrame(matches_df)
            st.dataframe(matches_df)
            
            # Estadísticas
            st.markdown("<h4 class='subsection-header'>Estadísticas</h4>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Matches", len(mejor_asignacion))
            col2.metric("Promedio de Horas", round(max_horas / len(mejor_asignacion), 2) if len(mejor_asignacion) > 0 else 0)
            col3.metric("Total Horas", round(max_horas, 2))
        else:
            st.info("No se encontraron matches principales.")
        
        # Matches secundarios
        st.markdown("<h3 class='subsection-header'>Matches Secundarios (1+ hora)</h3>", unsafe_allow_html=True)
        
        if matches_secundarios:
            secundarios_df = []
            for match in matches_secundarios:
                ruru_nombre, yaku_nombre, opcion, interseccion, _ = match
                horas = matchmaker.calcular_horas_asignadas(interseccion)
                secundarios_df.append({
                    "Ruru": ruru_nombre,
                    "Yaku": yaku_nombre,
                    "Opción": opcion,
                    "Horas": horas
                })
            
            secundarios_df = pd.DataFrame(secundarios_df)
            st.dataframe(secundarios_df)
        else:
            st.info("No se encontraron matches secundarios.")
        
        # Rurus sin match
        st.markdown("<h3 class='subsection-header'>Rurus sin Match</h3>", unsafe_allow_html=True)
        rurus_emparejados = set(match[0] for match in mejor_asignacion + matches_secundarios)
        rurus_sin_match = [ruru.nombre for ruru in rurus if ruru.nombre not in rurus_emparejados]
        
        if rurus_sin_match:
            st.write(", ".join(rurus_sin_match))
        else:
            st.success("¡Todos los Rurus fueron emparejados!")
        
        # Yakus sin match
        st.markdown("<h3 class='subsection-header'>Yakus sin Match</h3>", unsafe_allow_html=True)
        yakus_emparejados = set(match[1] for match in mejor_asignacion + matches_secundarios)
        yakus_sin_match = [yaku.nombre for yaku in yakus if yaku.nombre not in yakus_emparejados]
        
        if yakus_sin_match:
            st.write(", ".join(yakus_sin_match))
        else:
            st.success("¡Todos los Yakus fueron emparejados!")
        
        # Botón para exportar resultados
        st.markdown("<h3 class='subsection-header'>Exportar Resultados</h3>", unsafe_allow_html=True)
        
        if st.button("Exportar a Excel"):
            # Crear un Excel con múltiples hojas
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer) as writer:
                # Hoja de matches principales
                if len(matches_df) > 0:
                    matches_df.to_excel(writer, sheet_name="Matches Principales", index=False)
                
                # Hoja de matches secundarios
                if matches_secundarios and len(secundarios_df) > 0:
                    secundarios_df.to_excel(writer, sheet_name="Matches Secundarios", index=False)
                
                # Hoja de Rurus sin match
                pd.DataFrame({"Nombre": rurus_sin_match}).to_excel(writer, sheet_name="Rurus sin Match", index=False)
                
                # Hoja de Yakus sin match
                pd.DataFrame({"Nombre": yakus_sin_match}).to_excel(writer, sheet_name="Yakus sin Match", index=False)
            
            excel_data = excel_buffer.getvalue()
            
            # Usar el componente de descarga de Streamlit
            st.download_button(
                label="Descargar Excel",
                data=excel_data,
                file_name="resultados_match.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    except Exception as e:
        st.error(f"Error al procesar los resultados: {str(e)}") 