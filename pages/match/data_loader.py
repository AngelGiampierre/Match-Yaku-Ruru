import streamlit as st
import pandas as pd
from utils.match_algorithm import Yaku, Ruru, convertir_horarios

def cargar_datos_page():
    """
    Página para cargar datos de Yakus y Rurus
    """
    st.markdown("<h2 class='section-header'>Cargar y Mapear Datos</h2>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Datos de Yakus", "Datos de Rurus"])
    
    with tabs[0]:
        st.markdown("<h3 class='subsection-header'>Datos de Yakus</h3>", unsafe_allow_html=True)
        st.markdown("<p class='info-text'>Carga el archivo Excel con la información de los Yakus y mapea las columnas a los campos requeridos.</p>", unsafe_allow_html=True)
        
        uploaded_yaku_file = st.file_uploader("Cargar Excel de Yakus", type=["xlsx", "xls"], key="yaku_uploader")
        
        if uploaded_yaku_file is not None:
            try:
                yaku_df = pd.read_excel(uploaded_yaku_file)
                
                st.success(f"¡Archivo cargado exitosamente! Se encontraron {len(yaku_df)} registros.")
                
                with st.expander("Ver datos cargados", expanded=True):
                    st.dataframe(yaku_df.head(10))
                
                # Guardar el DataFrame en session_state para usarlo después
                st.session_state["yaku_df"] = yaku_df
                
                # Lista de columnas disponibles
                cols = yaku_df.columns.tolist()
                
                # Mapeo de letras de Excel a índices (A=0, B=1, etc.)
                def excel_col_to_index(col_letter):
                    if not col_letter:
                        return 0  # Por defecto seleccionar el primero
                    
                    # Convertir a índice (A=0, B=1, etc.)
                    col_letter = col_letter.upper()
                    if len(col_letter) == 1:
                        return ord(col_letter) - ord('A')
                    elif len(col_letter) == 2:
                        return (ord(col_letter[0]) - ord('A') + 1) * 26 + (ord(col_letter[1]) - ord('A'))
                    return 0
                
                # Función para obtener el índice en el selectbox
                def get_selectbox_index(col_letter, options):
                    if not col_letter:
                        return 0
                    
                    col_index = excel_col_to_index(col_letter)
                    if col_index < len(options) - 1:
                        return col_index + 1  # +1 porque la primera opción es "--Seleccionar--"
                    return 0
                
                st.markdown("<h4 class='subsection-header'>Mapeo de Columnas</h4>", unsafe_allow_html=True)
                
                # Crear dos columnas para organizar el mapeo
                col1, col2 = st.columns(2)
                
                with col1:
                    # Información personal con valores predefinidos
                    st.markdown("<p class='small-text'>Información Personal</p>", unsafe_allow_html=True)
                    nombre_col = st.selectbox("Nombre (Predefinido: B)", options=["--Seleccionar--"] + cols, key="yaku_nombre", index=get_selectbox_index("B", cols))
                    dni_col = st.selectbox("DNI (Predefinido: F)", options=["--Seleccionar--"] + cols, key="yaku_dni", index=get_selectbox_index("F", cols))
                    celular_col = st.selectbox("Celular (Predefinido: D)", options=["--Seleccionar--"] + cols, key="yaku_celular", index=get_selectbox_index("D", cols))
                    correo_col = st.selectbox("Correo (Predefinido: E)", options=["--Seleccionar--"] + cols, key="yaku_correo", index=get_selectbox_index("E", cols))
                    
                    # Información profesional con valores predefinidos
                    st.markdown("<p class='small-text'>Información Profesional</p>", unsafe_allow_html=True)
                    area_col = st.selectbox("Área (Predefinido: L)", options=["--Seleccionar--"] + cols, key="yaku_area", index=get_selectbox_index("L", cols))
                    
                    # Mostrar todas las columnas de opciones siempre, independientemente del área detectada
                    st.markdown("<p class='small-text'>Columnas para cada tipo de opción:</p>", unsafe_allow_html=True)
                    
                    # Siempre mostrar las tres opciones
                    opciones_arte_col = st.selectbox(
                        "Opciones Arte & Cultura (Predefinido: M - Cuenta cuentos, Dibujo y Pintura, etc.)", 
                        options=["--Seleccionar--"] + cols, 
                        key="yaku_opciones_arte", 
                        index=get_selectbox_index("M", cols)
                    )
                    
                    opciones_asesoria_col = st.selectbox(
                        "Opciones Asesoría a Colegios (Predefinido: O - Comunicación, Inglés, Matemática)", 
                        options=["--Seleccionar--"] + cols, 
                        key="yaku_opciones_asesoria", 
                        index=get_selectbox_index("O", cols)
                    )
                    
                    opciones_bienestar_col = st.selectbox(
                        "Opciones Bienestar Psicológico (Predefinido: P - Facilitador psicoeducativo)", 
                        options=["--Seleccionar--"] + cols, 
                        key="yaku_opciones_bienestar", 
                        index=get_selectbox_index("P", cols)
                    )
                    
                    beneficiarios_col = st.selectbox("Número de Beneficiarios (Predefinido: N)", options=["--Seleccionar--"] + cols, key="yaku_beneficiarios", index=get_selectbox_index("N", cols))
                    nivel_quechua_col = st.selectbox("Nivel de Quechua (Predefinido: AD)", options=["--Seleccionar--"] + cols, key="yaku_nivel_quechua", index=get_selectbox_index("AD", cols))
                    grados_col = st.selectbox("Grados (Predefinido: Y)", options=["--Seleccionar--"] + cols, key="yaku_grados", index=get_selectbox_index("Y", cols))
                
                with col2:
                    # Disponibilidad por día con valores predefinidos
                    st.markdown("<p class='small-text'>Disponibilidad por Día</p>", unsafe_allow_html=True)
                    lunes_col = st.selectbox("Lunes (Predefinido: R)", options=["--Seleccionar--"] + cols, key="yaku_lunes", index=get_selectbox_index("R", cols))
                    martes_col = st.selectbox("Martes (Predefinido: S)", options=["--Seleccionar--"] + cols, key="yaku_martes", index=get_selectbox_index("S", cols))
                    miercoles_col = st.selectbox("Miércoles (Predefinido: T)", options=["--Seleccionar--"] + cols, key="yaku_miercoles", index=get_selectbox_index("T", cols))
                    jueves_col = st.selectbox("Jueves (Predefinido: U)", options=["--Seleccionar--"] + cols, key="yaku_jueves", index=get_selectbox_index("U", cols))
                    viernes_col = st.selectbox("Viernes (Predefinido: V)", options=["--Seleccionar--"] + cols, key="yaku_viernes", index=get_selectbox_index("V", cols))
                    sabado_col = st.selectbox("Sábado (Predefinido: W)", options=["--Seleccionar--"] + cols, key="yaku_sabado", index=get_selectbox_index("W", cols))
                    domingo_col = st.selectbox("Domingo (Predefinido: X)", options=["--Seleccionar--"] + cols, key="yaku_domingo", index=get_selectbox_index("X", cols))
                
                # Guardar la configuración de mapeo
                if st.button("Guardar Mapeo de Yakus"):
                    mapeo_yakus = {
                        "nombre": nombre_col if nombre_col != "--Seleccionar--" else None,
                        "dni": dni_col if dni_col != "--Seleccionar--" else None,
                        "celular": celular_col if celular_col != "--Seleccionar--" else None,
                        "correo": correo_col if correo_col != "--Seleccionar--" else None,
                        "area": area_col if area_col != "--Seleccionar--" else None,
                        # Guardar las tres columnas de opciones
                        "opciones_arte": opciones_arte_col if opciones_arte_col != "--Seleccionar--" else None,
                        "opciones_asesoria": opciones_asesoria_col if opciones_asesoria_col != "--Seleccionar--" else None,
                        "opciones_bienestar": opciones_bienestar_col if opciones_bienestar_col != "--Seleccionar--" else None,
                        "beneficiarios": beneficiarios_col if beneficiarios_col != "--Seleccionar--" else None,
                        "nivel_quechua": nivel_quechua_col if nivel_quechua_col != "--Seleccionar--" else None,
                        "grados": grados_col if grados_col != "--Seleccionar--" else None,
                        "disponibilidad": {
                            "lunes": lunes_col if lunes_col != "--Seleccionar--" else None,
                            "martes": martes_col if martes_col != "--Seleccionar--" else None,
                            "miercoles": miercoles_col if miercoles_col != "--Seleccionar--" else None,
                            "jueves": jueves_col if jueves_col != "--Seleccionar--" else None,
                            "viernes": viernes_col if viernes_col != "--Seleccionar--" else None,
                            "sabado": sabado_col if sabado_col != "--Seleccionar--" else None,
                            "domingo": domingo_col if domingo_col != "--Seleccionar--" else None
                        }
                    }
                    
                    st.session_state["mapeo_yakus"] = mapeo_yakus
                    st.success("¡Mapeo de Yakus guardado correctamente!")
                    
                    # Mostrar vista previa de los primeros registros procesados
                    if st.checkbox("Mostrar vista previa procesada"):
                        try:
                            preview_df = procesar_preview_yakus(yaku_df, mapeo_yakus)
                            st.dataframe(preview_df)
                        except Exception as e:
                            st.error(f"Error al procesar la vista previa: {str(e)}")
                
            except Exception as e:
                st.error(f"Error al cargar el archivo: {str(e)}")
    
    with tabs[1]:
        st.markdown("<h3 class='subsection-header'>Datos de Rurus</h3>", unsafe_allow_html=True)
        st.markdown("<p class='info-text'>Carga el archivo Excel con la información de los Rurus y mapea las columnas a los campos requeridos.</p>", unsafe_allow_html=True)
        
        uploaded_ruru_file = st.file_uploader("Cargar Excel de Rurus", type=["xlsx", "xls"], key="ruru_uploader")
        
        if uploaded_ruru_file is not None:
            try:
                ruru_df = pd.read_excel(uploaded_ruru_file)
                
                st.success(f"¡Archivo cargado exitosamente! Se encontraron {len(ruru_df)} registros.")
                
                with st.expander("Ver datos cargados", expanded=True):
                    st.dataframe(ruru_df.head(10))
                
                # Guardar el DataFrame en session_state para usarlo después
                st.session_state["ruru_df"] = ruru_df
                
                # Lista de columnas disponibles
                cols = ruru_df.columns.tolist()
                
                st.markdown("<h4 class='subsection-header'>Mapeo de Columnas</h4>", unsafe_allow_html=True)
                
                # Crear dos columnas para organizar el mapeo
                col1, col2 = st.columns(2)
                
                with col1:
                    # Información del Ruru
                    st.markdown("<p class='small-text'>Información del Ruru</p>", unsafe_allow_html=True)
                    nombre_col = st.selectbox("Nombre", options=["--Seleccionar--"] + cols, key="ruru_nombre")
                    opciones_col = st.selectbox("Opciones/Intereses", options=["--Seleccionar--"] + cols, key="ruru_opciones")
                    idioma_col = st.selectbox("Idioma", options=["--Seleccionar--"] + cols, key="ruru_idioma")
                    grado_col = st.selectbox("Grado", options=["--Seleccionar--"] + cols, key="ruru_grado")
                
                with col2:
                    # Disponibilidad por día
                    st.markdown("<p class='small-text'>Disponibilidad por Día</p>", unsafe_allow_html=True)
                    lunes_col = st.selectbox("Lunes", options=["--Seleccionar--"] + cols, key="ruru_lunes")
                    martes_col = st.selectbox("Martes", options=["--Seleccionar--"] + cols, key="ruru_martes")
                    miercoles_col = st.selectbox("Miércoles", options=["--Seleccionar--"] + cols, key="ruru_miercoles")
                    jueves_col = st.selectbox("Jueves", options=["--Seleccionar--"] + cols, key="ruru_jueves")
                    viernes_col = st.selectbox("Viernes", options=["--Seleccionar--"] + cols, key="ruru_viernes")
                    sabado_col = st.selectbox("Sábado", options=["--Seleccionar--"] + cols, key="ruru_sabado")
                    domingo_col = st.selectbox("Domingo", options=["--Seleccionar--"] + cols, key="ruru_domingo")
                
                # Guardar la configuración de mapeo
                if st.button("Guardar Mapeo de Rurus"):
                    mapeo_rurus = {
                        "nombre": nombre_col if nombre_col != "--Seleccionar--" else None,
                        "opciones": opciones_col if opciones_col != "--Seleccionar--" else None,
                        "idioma": idioma_col if idioma_col != "--Seleccionar--" else None,
                        "grado": grado_col if grado_col != "--Seleccionar--" else None,
                        "disponibilidad": {
                            "lunes": lunes_col if lunes_col != "--Seleccionar--" else None,
                            "martes": martes_col if martes_col != "--Seleccionar--" else None,
                            "miercoles": miercoles_col if miercoles_col != "--Seleccionar--" else None,
                            "jueves": jueves_col if jueves_col != "--Seleccionar--" else None,
                            "viernes": viernes_col if viernes_col != "--Seleccionar--" else None,
                            "sabado": sabado_col if sabado_col != "--Seleccionar--" else None,
                            "domingo": domingo_col if domingo_col != "--Seleccionar--" else None
                        }
                    }
                    
                    st.session_state["mapeo_rurus"] = mapeo_rurus
                    st.success("¡Mapeo de Rurus guardado correctamente!")
                    
                    # Mostrar vista previa de los primeros registros procesados
                    if st.checkbox("Mostrar vista previa procesada"):
                        try:
                            preview_df = procesar_preview_rurus(ruru_df, mapeo_rurus)
                            st.dataframe(preview_df)
                        except Exception as e:
                            st.error(f"Error al procesar la vista previa: {str(e)}")
                
            except Exception as e:
                st.error(f"Error al cargar el archivo: {str(e)}")
    
    # Botón para ejecutar el match si los datos están cargados
    if "yaku_df" in st.session_state and "ruru_df" in st.session_state and "mapeo_yakus" in st.session_state and "mapeo_rurus" in st.session_state:
        st.markdown("<div class='highlight'>", unsafe_allow_html=True)
        st.markdown("<h3 class='subsection-header'>Ejecutar Match</h3>", unsafe_allow_html=True)
        if st.button("Ejecutar Match", key="ejecutar_match"):
            st.session_state["ejecutar_match_clicked"] = True
            st.success("¡Proceso iniciado! Vaya a la pestaña de Resultados para ver los matches.")
        st.markdown("</div>", unsafe_allow_html=True)


def procesar_preview_yakus(df, mapeo):
    """Crea una vista previa de cómo se procesarían los datos de Yakus."""
    preview_data = []
    
    for _, row in df.head(5).iterrows():
        try:
            nombre = row[mapeo["nombre"]] if mapeo["nombre"] else "No especificado"
            dni = row[mapeo["dni"]] if mapeo["dni"] else "No especificado"
            area = row[mapeo["area"]] if mapeo["area"] else "No especificado"
            opciones = row[mapeo["opciones_arte"]] if mapeo["opciones_arte"] else "No especificado"
            
            # Procesar disponibilidad para una vista simplificada
            disponibilidad = []
            for dia, col in mapeo["disponibilidad"].items():
                if col and not pd.isna(row[col]) and row[col]:
                    disponibilidad.append(f"{dia.capitalize()}: {row[col]}")
            
            disponibilidad_str = ", ".join(disponibilidad) if disponibilidad else "No especificado"
            
            preview_data.append({
                "Nombre": nombre,
                "DNI": dni,
                "Área": area,
                "Opciones": opciones,
                "Disponibilidad": disponibilidad_str
            })
        except Exception as e:
            # Ignorar errores para la vista previa
            continue
    
    return pd.DataFrame(preview_data)


def procesar_preview_rurus(df, mapeo):
    """Crea una vista previa de cómo se procesarían los datos de Rurus."""
    preview_data = []
    
    for _, row in df.head(5).iterrows():
        try:
            nombre = row[mapeo["nombre"]] if mapeo["nombre"] else "No especificado"
            opciones = row[mapeo["opciones"]] if mapeo["opciones"] else "No especificado"
            idioma = row[mapeo["idioma"]] if mapeo["idioma"] else "No especificado"
            grado = row[mapeo["grado"]] if mapeo["grado"] else "No especificado"
            
            # Procesar disponibilidad para una vista simplificada
            disponibilidad = []
            for dia, col in mapeo["disponibilidad"].items():
                if col and not pd.isna(row[col]) and row[col]:
                    disponibilidad.append(f"{dia.capitalize()}: {row[col]}")
            
            disponibilidad_str = ", ".join(disponibilidad) if disponibilidad else "No especificado"
            
            preview_data.append({
                "Nombre": nombre,
                "Opciones": opciones,
                "Idioma": idioma,
                "Grado": grado,
                "Disponibilidad": disponibilidad_str
            })
        except Exception as e:
            # Ignorar errores para la vista previa
            continue
    
    return pd.DataFrame(preview_data)


def procesar_yakus(df, mapeo):
    """Convierte el DataFrame en objetos Yaku según el mapeo de columnas."""
    yakus = []
    
    for idx, row in df.iterrows():
        try:
            # Extraer valores según el mapeo
            nombre = str(row[mapeo["nombre"]]) if mapeo["nombre"] and not pd.isna(row[mapeo["nombre"]]) else f"Yaku_{idx}"
            dni = str(row[mapeo["dni"]]) if mapeo["dni"] and not pd.isna(row[mapeo["dni"]]) else "00000000"
            celular = str(row[mapeo["celular"]]) if mapeo["celular"] and not pd.isna(row[mapeo["celular"]]) else "000000000"
            correo = str(row[mapeo["correo"]]) if mapeo["correo"] and not pd.isna(row[mapeo["correo"]]) else "correo@ejemplo.com"
            
            # Área con manejo de valores NaN
            area = None
            if mapeo["area"] and not pd.isna(row[mapeo["area"]]):
                area = str(row[mapeo["area"]])
            else:
                area = "Arte & Cultura"  # Valor por defecto
            
            # Procesar opciones según el área y usar la columna correspondiente
            opciones = []
            area_str = str(area).lower()
            
            # Determinar qué columna de opciones usar según el área
            if "arte" in area_str or "cultura" in area_str:
                opciones_col = mapeo["opciones_arte"]
            elif "asesor" in area_str or "colegio" in area_str:
                opciones_col = mapeo["opciones_asesoria"]
            elif "bienestar" in area_str or "psico" in area_str:
                opciones_col = mapeo["opciones_bienestar"]
            else:
                # Si no se reconoce el área, intentar usar cualquier columna disponible
                opciones_col = mapeo.get("opciones_arte") or mapeo.get("opciones_asesoria") or mapeo.get("opciones_bienestar")
            
            # Leer opciones de la columna seleccionada
            if opciones_col and not pd.isna(row[opciones_col]):
                opciones_str = str(row[opciones_col])
                if ',' in opciones_str:
                    opciones = [op.strip() for op in opciones_str.split(',')]
                else:
                    opciones = [opciones_str.strip()]
            
            # Si no hay opciones, asignar valor por defecto según el área
            if not opciones:
                if "arte" in area_str or "cultura" in area_str:
                    opciones = ["Música"]  # Valor por defecto para Arte & Cultura
                elif "asesor" in area_str or "colegio" in area_str:
                    opciones = ["Matemática"]  # Valor por defecto para Asesoría
                elif "bienestar" in area_str or "psico" in area_str:
                    opciones = ["Facilitador psicoeducativo"]  # Valor por defecto para Bienestar
                else:
                    opciones = ["No especificado"]
            
            # Número de beneficiarios
            num_beneficiarios = 0
            if mapeo["beneficiarios"] and not pd.isna(row[mapeo["beneficiarios"]]):
                try:
                    num_beneficiarios = int(row[mapeo["beneficiarios"]])
                except ValueError:
                    # Si no se puede convertir a entero, intentar extraer dígitos
                    import re
                    digits = re.findall(r'\d+', str(row[mapeo["beneficiarios"]]))
                    if digits:
                        num_beneficiarios = int(digits[0])
            
            # Procesar nivel de quechua
            nivel_quechua = "No lo hablo"  # Valor por defecto
            if mapeo["nivel_quechua"] and not pd.isna(row[mapeo["nivel_quechua"]]):
                nivel_quechua = str(row[mapeo["nivel_quechua"]])
            
            # Procesar grados (puede ser una lista separada por comas)
            grados = []
            if mapeo["grados"] and not pd.isna(row[mapeo["grados"]]):
                grados_str = str(row[mapeo["grados"]])
                if ',' in grados_str:
                    grados = [g.strip() for g in grados_str.split(',')]
                else:
                    grados = [grados_str.strip()]
            
            # Si no hay grados, asignar valor por defecto
            if not grados:
                grados = ["Secundaria (1°, 2° y 3° grado)"]
            
            # Procesar disponibilidad
            disponibilidad_raw = []
            for dia, col in mapeo["disponibilidad"].items():
                if col and not pd.isna(row[col]) and row[col]:
                    periodos = str(row[col]).strip().split(',')
                    for periodo in periodos:
                        periodo = periodo.strip()
                        if periodo in ["Mañana", "Tarde", "Noche"]:
                            dia_nombre = dia.capitalize() if dia != "miercoles" else "Miércoles"
                            disponibilidad_raw.append(f"{dia_nombre} {periodo}")
            
            disponibilidad = convertir_horarios(','.join(disponibilidad_raw)) if disponibilidad_raw else {}
            
            # Crear objeto Yaku
            yaku = Yaku(
                nombre=nombre,
                dni=dni,
                celular=celular,
                correo=correo,
                area=area,
                opciones=opciones,
                num_beneficiarios=num_beneficiarios,
                disponibilidad=disponibilidad,
                nivel_quechua=nivel_quechua,
                grados=grados
            )
            
            yakus.append(yaku)
        
        except Exception as e:
            print(f"Error al procesar Yaku en fila {idx}: {str(e)}")
            continue
    
    return yakus


def procesar_rurus(df, mapeo):
    """Convierte el DataFrame en objetos Ruru según el mapeo de columnas."""
    rurus = []
    
    for idx, row in df.iterrows():
        try:
            # Extraer valores según el mapeo
            nombre = str(row[mapeo["nombre"]]) if mapeo["nombre"] else f"Ruru_{idx}"
            
            # Procesar opciones (puede ser una lista separada por comas)
            if mapeo["opciones"]:
                opciones_str = str(row[mapeo["opciones"]])
                opciones = [op.strip() for op in opciones_str.split(',')] if ',' in opciones_str else [opciones_str]
            else:
                opciones = ["No especificado"]
            
            # Idioma
            idioma = str(row[mapeo["idioma"]]) if mapeo["idioma"] else "Español"
            
            # Grado
            grado = str(row[mapeo["grado"]]) if mapeo["grado"] else "Secundaria (1°, 2° y 3° grado)"
            
            # Procesar disponibilidad
            disponibilidad_raw = []
            for dia, col in mapeo["disponibilidad"].items():
                if col and not pd.isna(row[col]) and row[col]:
                    periodos = str(row[col]).strip().split(',')
                    for periodo in periodos:
                        if periodo.strip() in ["Mañana", "Tarde", "Noche"]:
                            dia_nombre = dia.capitalize() if dia != "miercoles" else "Miércoles"
                            disponibilidad_raw.append(f"{dia_nombre} {periodo.strip()}")
            
            disponibilidad = convertir_horarios(','.join(disponibilidad_raw)) if disponibilidad_raw else {}
            
            # Crear objeto Ruru
            ruru = Ruru(
                nombre=nombre,
                opciones=opciones,
                disponibilidad=disponibilidad,
                idioma=idioma,
                grado=grado
            )
            
            rurus.append(ruru)
        
        except Exception as e:
            print(f"Error al procesar Ruru en fila {idx}: {str(e)}")
            continue
    
    return rurus 