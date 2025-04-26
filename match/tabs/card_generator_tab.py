"""
Pestaña para generar tarjetas de presentación para Yakus
basadas en un template de Word y el archivo final de asignaciones.
Permite generar archivos DOCX o PDF (usando LibreOffice via subprocess).
"""
import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import zipfile
from io import BytesIO
import os
import tempfile
import subprocess
import shutil

# --- NUEVO: Intentar importar docx2pdf ---
try:
    from docx2pdf import convert
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False
    # No mostrar error aquí, lo haremos en la UI si el usuario elige PDF

# --- Importar clean_str_number ---
try:
    # Asumiendo que output_generator está un nivel arriba
    from ..utils.output_generator import clean_str_number
except ImportError:
    # Fallback si la importación principal aún falla por alguna razón
    print("ADVERTENCIA: No se pudo importar clean_str_number desde utils. Usando fallback.")
    def clean_str_number(val):
        if pd.isna(val) or val == '': return ''
        try:
            cleaned_val = str(int(float(str(val))))
        except (ValueError, TypeError):
            cleaned_val = str(val).strip()
        if cleaned_val.endswith('.0'): cleaned_val = cleaned_val[:-2]
        return cleaned_val

# Mapeos específicos para BP según las reglas dadas
MAPEO_COLEGIO = {
    'CC': 'IE Cachin',
    'DI': 'IE 27 de diciembre',
    'EN': 'Org. Entre Notas',
    'GP': 'IE Gregorio Pita',
    'IA': 'Org. Activa Migrantes',
    'PD': 'Promoviendo la diversidad',
    'SL': 'Org. Sol y Luna',
}

MAPEO_CIUDAD = {
    'CC': 'Cusco',
    'DI': 'Lima Provincias',
    'EN': 'Cusco',
    'GP': 'Cajamarca',
    'IA': 'Callao',
    'PD': 'Trujillo',
    'SL': 'Cusco',
}

# --- NUEVO: Función para encontrar LibreOffice ---
# (Opcional pero recomendado para robustez)
@st.cache_data # Cachear el resultado para no buscar cada vez
def find_libreoffice_path():
    """Intenta encontrar el ejecutable de LibreOffice en ubicaciones comunes de macOS."""
    common_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        # Puedes añadir otras rutas si es necesario
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    # Alternativa: usar shutil.which que busca en el PATH del sistema
    soffice_path = shutil.which("soffice")
    if soffice_path:
        return soffice_path
    return None

# Función auxiliar para obtener prefijo (asumiendo IDs como 'CC123')
def get_prefix(ruru_id):
    if isinstance(ruru_id, str) and len(ruru_id) >= 2:
        prefix = ruru_id[:2].upper()
        return prefix
    return None

# Función auxiliar para limpiar valores de horario
def format_schedule(value):
    if pd.isna(value) or str(value).strip() == '':
        return "No disponible"
    return str(value).strip()

# --- Pestaña Streamlit ---
def card_generator_tab():
    st.header("Generador de Tarjetas de Presentación (Yaku-Ruru)")
    st.write("Sube el template de Word y el archivo Excel final del match para generar las tarjetas.")

    # Estado de sesión específico
    if 'cardgen_template' not in st.session_state: st.session_state.cardgen_template = None
    if 'cardgen_excel_data' not in st.session_state: st.session_state.cardgen_excel_data = None
    if 'cardgen_zip_buffer' not in st.session_state: st.session_state.cardgen_zip_buffer = None
    if 'cardgen_area' not in st.session_state: st.session_state.cardgen_area = "Bienestar Psicológico" # Empezar con BP
    if 'cardgen_output_format' not in st.session_state: st.session_state.cardgen_output_format = "DOCX" # Nuevo estado

    # Selector de Área (por ahora solo BP, pero preparamos para futuro)
    area_options = ["Bienestar Psicológico", "Asesoría a Colegios Nacionales", "Arte & Cultura"]
    selected_area = st.selectbox(
        "Selecciona el Área para generar tarjetas:",
        area_options,
        index=area_options.index(st.session_state.cardgen_area), # Iniciar con BP
        key="cardgen_area_selector"
    )

    # Resetear si cambia el área
    if st.session_state.cardgen_area != selected_area:
        st.session_state.cardgen_area = selected_area
        st.session_state.cardgen_template = None
        st.session_state.cardgen_excel_data = None
        st.session_state.cardgen_zip_buffer = None
        st.rerun()

    st.subheader(f"Paso 1: Cargar Archivos para '{selected_area}'")

    # Uploaders
    uploaded_template = st.file_uploader("1. Cargar Template Word (.docx)", type=["docx"], key="cardgen_template_upload")
    uploaded_excel = st.file_uploader("2. Cargar Excel Final del Match (.xlsx)", type=["xlsx", "xls"], key="cardgen_excel_upload")

    # Cargar datos a sesión
    if uploaded_template:
        st.session_state.cardgen_template = uploaded_template
    if uploaded_excel:
        try:
            # Leer solo la hoja de asignaciones
            df_asignaciones = pd.read_excel(uploaded_excel, sheet_name="Asignaciones")
            # Filtrar por el área seleccionada (¡Asegúrate que la columna 'Area' exista!)
            if 'Area' in df_asignaciones.columns:
                 df_filtrado = df_asignaciones[df_asignaciones['Area'] == selected_area].copy()
                 if df_filtrado.empty:
                     st.warning(f"No se encontraron asignaciones para el área '{selected_area}' en la hoja 'Asignaciones'.")
                     st.session_state.cardgen_excel_data = None
                 else:
                     st.success(f"Se cargaron {len(df_filtrado)} asignaciones para '{selected_area}'.")
                     st.session_state.cardgen_excel_data = df_filtrado
            else:
                 st.error("Error: La hoja 'Asignaciones' no contiene la columna 'Area'. No se puede filtrar.")
                 st.session_state.cardgen_excel_data = None

        except Exception as e:
            st.error(f"Error al leer el archivo Excel: {e}")
            st.session_state.cardgen_excel_data = None

    # Botón para generar
    if st.session_state.cardgen_template is not None and st.session_state.cardgen_excel_data is not None:
        st.subheader("Paso 2: Configurar y Generar Tarjetas")

        output_format = st.radio(
            "Selecciona el formato de salida:",
            ("DOCX", "PDF"),
            index=0 if st.session_state.cardgen_output_format == "DOCX" else 1,
            key="cardgen_format_radio"
        )
        st.session_state.cardgen_output_format = output_format

        # --- ACTUALIZADO: Advertencia PDF ahora verifica si encontramos LibreOffice ---
        libreoffice_path = None
        if output_format == "PDF":
            libreoffice_path = find_libreoffice_path()
            if not libreoffice_path:
                st.error("No se pudo encontrar el ejecutable de LibreOffice ('soffice'). La generación de PDF no está disponible.")
                st.warning("Asegúrate de que LibreOffice esté instalado en una ubicación estándar (ej. /Applications) o que 'soffice' esté en el PATH del sistema.")
                generate_disabled = True
            else:
                st.success(f"Usando LibreOffice encontrado en: {libreoffice_path}")
                generate_disabled = False
        else: # DOCX
             generate_disabled = False

        if st.button(f"Generar Tarjetas en formato {output_format}", key="cardgen_generate_button", disabled=generate_disabled):
            with st.spinner(f"Generando documentos {output_format}..."):
                try:
                    template_file = st.session_state.cardgen_template
                    df_data = st.session_state.cardgen_excel_data
                    area_actual = st.session_state.cardgen_area
                    chosen_format = st.session_state.cardgen_output_format
                    # Usar la ruta encontrada o None si no se encontró y el formato es DOCX
                    lo_path = libreoffice_path if chosen_format == "PDF" else None

                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        processed_count = 0
                        errors_count = 0
                        for index, row in df_data.iterrows():
                            ruru_id = str(row.get('ID Ruru', '')).strip()
                            try:
                                with tempfile.TemporaryDirectory() as temp_dir:
                                    # Renderizar DOCX
                                    doc = DocxTemplate(template_file)
                                    context = {}
                                    context['ID_Ruru'] = ruru_id
                                    prefix = get_prefix(ruru_id)
                                    context['Colegio'] = MAPEO_COLEGIO.get(prefix, 'N/A')
                                    context['Ciudad'] = MAPEO_CIUDAD.get(prefix, 'N/A')
                                    context['Grado_Original_Ruru'] = str(row.get('Grado Original Ruru', 'N/A')).strip()
                                    quechua_raw = str(row.get('Quechua Ruru', 'N/A')).strip()
                                    if quechua_raw == "No lo hablo": context['Quechua_Ruru'] = "Español"
                                    elif quechua_raw == "Nivel básico": context['Quechua_Ruru'] = "Español y Quechua"
                                    else: context['Quechua_Ruru'] = quechua_raw
                                    context['Nombre_Ruru'] = str(row.get('Nombre Ruru', '')).strip()
                                    context['Area'] = area_actual
                                    nombre_apod_raw = str(row.get('Nombre Apoderado Ruru', '')).strip()
                                    if nombre_apod_raw.lower() == 'nan': context['Nombre_Apoderado_Ruru'] = ""
                                    else: context['Nombre_Apoderado_Ruru'] = nombre_apod_raw
                                    context['Celular_Asesoria_Ruru'] = clean_str_number(row.get('Celular Asesoria Ruru'))
                                    celular_apod_raw = row.get('Celular Apoderado Ruru')
                                    celular_apod_clean = clean_str_number(celular_apod_raw)
                                    if celular_apod_clean:
                                        context['Celular_del_Apoderado'] = "Celular del Apoderado:"
                                        context['Celular_Apoderado_Ruru'] = celular_apod_clean
                                    else:
                                        context['Celular_del_Apoderado'] = ""
                                        context['Celular_Apoderado_Ruru'] = ""
                                    for dia in ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']:
                                        col_excel = f'Horario {dia} Ruru'
                                        tag_plantilla = f'Horario_{dia}_Ruru'
                                        context[tag_plantilla] = format_schedule(row.get(col_excel))

                                    doc.render(context)
                                    temp_docx_path = os.path.join(temp_dir, f"{ruru_id}.docx")
                                    doc.save(temp_docx_path)

                                    # --- REEMPLAZO: Usar subprocess para PDF ---
                                    if chosen_format == "PDF":
                                        pdf_path = os.path.join(temp_dir, f"{ruru_id}.pdf")
                                        cmd = [
                                            lo_path, # Usar la ruta encontrada
                                            '--headless',         # No mostrar UI
                                            '--convert-to', 'pdf', # Formato de salida
                                            '--outdir', temp_dir, # Directorio de salida
                                            temp_docx_path        # Archivo de entrada
                                        ]
                                        try:
                                            # Ejecutar el comando
                                            process = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30) # Timeout de 30s

                                            # Verificar si LibreOffice reportó un error (código de retorno no cero)
                                            if process.returncode != 0:
                                                raise RuntimeError(f"LibreOffice falló (código {process.returncode}). Error: {process.stderr}")

                                            # Verificar si el PDF fue creado
                                            if not os.path.exists(pdf_path):
                                                raise RuntimeError(f"LibreOffice terminó correctamente (código {process.returncode}) pero no se encontró el archivo PDF. Output: {process.stdout} Stderr: {process.stderr}")

                                            # Leer el PDF si todo fue bien
                                            with open(pdf_path, "rb") as f_pdf:
                                                file_content = f_pdf.read()
                                            file_extension = ".pdf"

                                        except subprocess.TimeoutExpired:
                                             errors_count += 1
                                             st.warning(f"Timeout al convertir a PDF para Ruru ID '{ruru_id}'. LibreOffice tardó demasiado. Se omitirá.")
                                             continue
                                        except Exception as e_pdf:
                                            errors_count += 1
                                            st.warning(f"Error al convertir a PDF con LibreOffice para Ruru ID '{ruru_id}': {e_pdf}. Se omitirá.")
                                            continue # Saltar al siguiente Ruru
                                    else: # Formato DOCX
                                        with open(temp_docx_path, "rb") as f_docx:
                                            file_content = f_docx.read()
                                        file_extension = ".docx"
                                    # --- FIN REEMPLAZO ---

                                    filename_in_zip = f"{ruru_id}{file_extension}"
                                    zipf.writestr(filename_in_zip, file_content)
                                    processed_count += 1

                            except Exception as e_row:
                                errors_count += 1
                                st.warning(f"Error general al procesar Ruru ID '{ruru_id}': {e_row}")

                    zip_buffer.seek(0)
                    st.session_state.cardgen_zip_buffer = zip_buffer

                    if processed_count > 0: st.success(f"Se generaron {processed_count} tarjetas en formato {chosen_format} correctamente.")
                    if errors_count > 0: st.error(f"Hubo errores al generar/convertir {errors_count} tarjetas.")
                    if processed_count == 0 and errors_count == 0: st.info("No se procesó ninguna tarjeta.")

                except Exception as e:
                    st.error(f"Ocurrió un error general durante la generación: {e}")
                    st.session_state.cardgen_zip_buffer = None

    # Botón de descarga
    if st.session_state.get('cardgen_zip_buffer'):
        st.subheader("Paso 3: Descargar Tarjetas")
        area_filename = st.session_state.cardgen_area.replace(" ", "_").replace("&", "y")
        output_format_dl = st.session_state.cardgen_output_format # Usar el formato elegido
        st.download_button(
            label=f"Descargar Tarjetas_{area_filename}_{output_format_dl}.zip", # Nombre archivo incluye formato
            data=st.session_state.cardgen_zip_buffer,
            file_name=f"Tarjetas_{area_filename}_{output_format_dl}.zip",
            mime="application/zip",
            key="cardgen_download_button"
        ) 