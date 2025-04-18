"""
Componentes de UI para carga de archivos.

Contiene widgets reutilizables para subir archivos con validación.
"""

import streamlit as st
import os


def file_uploader(
    label="Subir archivo",
    types=None,
    key=None,
    help_text=None,
    on_change=None
):
    """
    Crea un widget para subir archivos con validación de extensión.
    
    Args:
        label (str): Etiqueta para el uploader
        types (list): Lista de extensiones permitidas sin el punto (ej: ["xlsx", "csv"])
        key (str): Clave única para el widget
        help_text (str): Texto de ayuda
        on_change (callable): Función a llamar cuando cambia el archivo
        
    Returns:
        file: Archivo subido o None
    """
    if types is None:
        types = ["xlsx", "xls", "csv"]
    
    # Convertir tipos a formato para st.file_uploader
    accepted_types = [f".{t.lower()}" if not t.startswith(".") else t.lower() for t in types]
    
    # Crear mensaje de ayuda si no se proporciona
    if help_text is None:
        type_str = ", ".join([t.upper() for t in types])
        help_text = f"Formatos aceptados: {type_str}"
    
    # Crear uploader
    uploaded_file = st.file_uploader(
        label,
        type=accepted_types,
        key=key,
        help=help_text,
        on_change=on_change
    )
    
    # Validar archivo
    if uploaded_file is not None:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Verificar extensión
        if file_ext not in accepted_types:
            st.error(f"❌ Formato de archivo no válido. Formatos aceptados: {', '.join(types)}")
            return None
        
        # Mostrar información del archivo
        file_size_kb = uploaded_file.size / 1024
        st.success(f"✅ Archivo cargado: {uploaded_file.name} ({file_size_kb:.1f} KB)")
    
    return uploaded_file 