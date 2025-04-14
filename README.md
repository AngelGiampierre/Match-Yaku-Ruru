# Match-Yaku-Ruru
008/100: Este repositorio contiene un algoritmo que mejora la asignación de Yakus (mentores) a Rurus (estudiantes) en Yachay Wasi, una organización educativa de voluntariado. Mediante la automatización del proceso y considerando horarios, áreas temáticas y grados, ahorra tiempo a los voluntarios y mejora las experiencias de aprendizaje de los estudiantes.

## Estructura del Proyecto

La aplicación está estructurada de forma modular para facilitar el mantenimiento y desarrollo independiente de cada funcionalidad:

```
/Match-Yaku-Ruru/
├── app.py                         # Punto de entrada principal (dashboard)
├── assets/                        # Recursos estáticos
│   └── styles.css                 # Estilos CSS separados
├── components/                    # Componentes reutilizables
│   ├── __init__.py
│   ├── dashboard.py               # Página principal del dashboard
│   └── sidebar.py                 # Componente de navegación lateral
├── pages/                         # Páginas individuales
│   ├── __init__.py
│   ├── match/                     # Funcionalidad de Match
│   │   ├── __init__.py
│   │   ├── data_loader.py         # Carga de datos y mapeo
│   │   ├── results.py             # Visualización de resultados
│   │   └── match_page.py          # Página principal de Match
│   ├── preprocessing/             # Pre-procesamiento (estructura modular)
│   │   ├── __init__.py
│   │   ├── preprocess_main.py     # Punto de entrada del preprocesamiento
│   │   ├── tabs/                  # Tabs individuales
│   │   │   ├── __init__.py
│   │   │   ├── load_clean_tab.py  # Tab de carga y limpieza
│   │   │   ├── selection_area_tab.py # Tab de selección por área
│   │   │   └── export_tab.py      # Tab de exportación
│   │   ├── components/            # Componentes reutilizables
│   │   │   ├── __init__.py
│   │   │   ├── data_validators.py # Validadores de datos (DNI, email)
│   │   │   ├── data_handlers.py   # Manejo de datos
│   │   │   └── file_handlers.py   # Manejo de archivos
│   └── email/                     # Envío de emails
│       ├── __init__.py
│       └── email_page.py          # Página de envío de emails
└── utils/                         # Utilidades compartidas
    ├── __init__.py
    ├── match_algorithm.py         # Algoritmo de matching
    ├── data_processors.py         # Procesamiento de datos
    └── email_sender.py            # Funcionalidad de envío de emails
```

## Descripción de los componentes principales

### Archivo principal

- **app.py**: Punto de entrada de la aplicación. Configura Streamlit, carga estilos CSS y maneja la navegación entre páginas.

### Assets

- **styles.css**: Contiene todos los estilos CSS utilizados en la aplicación.

### Components

- **dashboard.py**: Implementa la página principal del dashboard con tarjetas para acceder a cada funcionalidad.
- **sidebar.py**: Implementa la barra lateral de navegación que se muestra en todas las páginas.

### Pages/Match

- **match_page.py**: Controlador principal para la funcionalidad de match.
- **data_loader.py**: Maneja la carga y mapeo de datos de Yakus y Rurus desde archivos Excel.
- **results.py**: Muestra los resultados del algoritmo de match y permite exportarlos.

### Pages/Preprocessing (Nueva estructura modular)

- **preprocess_main.py**: Punto de entrada principal de la funcionalidad de preprocesamiento.
  
- **tabs/**:
  - **load_clean_tab.py**: Implementa el tab para carga y limpieza de datos con funciones para:
    - Detección automática de columnas importantes
    - Validación de DNI/Pasaporte
    - Validación de email
    - Ordenamiento de datos
    - Exportación rápida
  
  - **selection_area_tab.py**: Implementa el tab para filtrado por área con funciones para:
    - Cargar archivo de selección
    - Validar DNIs en selección
    - Filtrado por área específica
    - Gestión de DNIs no encontrados
    - Búsqueda en todas las áreas
    
  - **export_tab.py**: Implementa el tab para exportación de datos procesados con:
    - Exportación a Excel/CSV
    - Resumen de datos
    - Distribución por área

- **components/**:
  - **data_validators.py**: Componentes para validar datos como DNI y correo electrónico.
  - **data_handlers.py**: Funciones para manejar operaciones con datos como actualización de DNI y ordenamiento.
  - **file_handlers.py**: Funciones para exportar datos a diferentes formatos.

### Pages/Email

- **email_page.py**: Implementa la funcionalidad para enviar emails a Yakus y Rurus con sus asignaciones.

### Utils

- **match_algorithm.py**: Contiene las clases `Yaku`, `Ruru`, `MatchMaker` y `ReportGenerator` que implementan el algoritmo de matching.
- **data_processors.py**: Funciones utilitarias para el procesamiento de datos (estandarización de DNIs, validación de emails, etc.).
- **email_sender.py**: Implementa la funcionalidad para enviar emails.

## Guía para el desarrollo por funcionalidad

Para trabajar de forma independiente en cada funcionalidad, estos son los archivos relevantes por área:

### Funcionalidad de Match

1. Para editar la interfaz de carga de datos:
   - `pages/match/data_loader.py`
   - `assets/styles.css` (si necesitas ajustar estilos)

2. Para editar la visualización de resultados:
   - `pages/match/results.py`
   - `assets/styles.css` (si necesitas ajustar estilos)

3. Para modificar el algoritmo de match:
   - `utils/match_algorithm.py`

### Funcionalidad de Preprocesamiento (Nueva estructura modular)

1. Para modificar el punto de entrada principal:
   - `pages/preprocessing/preprocess_main.py`

2. Para trabajar en la carga y limpieza de datos:
   - `pages/preprocessing/tabs/load_clean_tab.py`
   - `pages/preprocessing/components/data_validators.py`

3. Para trabajar en la selección por área:
   - `pages/preprocessing/tabs/selection_area_tab.py`

4. Para trabajar en la exportación:
   - `pages/preprocessing/tabs/export_tab.py`
   - `pages/preprocessing/components/file_handlers.py`

5. Para modificar los componentes reutilizables:
   - `pages/preprocessing/components/data_validators.py`
   - `pages/preprocessing/components/data_handlers.py`
   - `pages/preprocessing/components/file_handlers.py`

6. Características principales de preprocesamiento:
   - **Carga y limpieza de datos**: Subir archivos Excel/CSV y detectar automáticamente columnas importantes.
   - **Edición de DNIs**: Corregir y estandarizar números de documento con persistencia de cambios.
   - **Validación de correos**: Detectar y corregir problemas con direcciones de correo electrónico.
   - **Ordenamiento inteligente**: Ordenar datos por área u otras columnas manteniendo el orden en la exportación.
   - **Filtrado por área y selección**: Filtrar yakus específicos por área usando una lista de seleccionados.
   - **Gestión de DNIs no encontrados**: Identificar y gestionar yakus que no se encuentran en un área específica.
   - **Búsqueda avanzada**: Localizar yakus por DNI o nombre en toda la base de datos.
   - **Asignación manual de área**: Reasignar yakus a áreas específicas cuando es necesario.

### Funcionalidad de Emails

1. Para desarrollar esta funcionalidad:
   - `pages/email/email_page.py`
   - `utils/email_sender.py`

### Interfaz general

1. Para modificar el dashboard principal:
   - `components/dashboard.py`
   - `assets/styles.css`

2. Para modificar la navegación:
   - `components/sidebar.py`
   - `app.py`

## Ejecutando la aplicación

Para ejecutar la aplicación:

```bash
streamlit run app.py
```

## Flujo de trabajo típico

1. **Preprocesar los datos** de Yakus y Rurus:
   - Cargar archivo de datos de yakus
   - Seleccionar columnas relevantes
   - Limpiar y estandarizar DNIs/Pasaportes y correos
   - Ordenar datos por área u otras columnas de interés
   - Filtrar por área usando lista de seleccionados
   - Gestionar casos especiales de DNIs no encontrados
   - Exportar datos limpios y ordenados

2. **Cargar los datos** en la funcionalidad de Match
3. **Ejecutar el algoritmo** para encontrar las mejores asignaciones
4. **Enviar emails** a los participantes con sus asignaciones

## Beneficios de la estructura modular

La aplicación ha sido diseñada con un enfoque modular para facilitar:

1. **Mantenimiento**: Cada componente tiene una única responsabilidad
2. **Desarrollo en paralelo**: Diferentes desarrolladores pueden trabajar en diferentes módulos
3. **Reutilización de código**: Componentes compartidos evitan duplicación
4. **Pruebas unitarias**: Código modular facilita pruebas independientes
5. **Extensibilidad**: Nuevos componentes pueden ser añadidos fácilmente

## Funcionalidades avanzadas de preprocesamiento

### Gestión de DNIs y ordenamiento
- Editar manualmente DNIs con formato incorrecto
- Conservar documentos especiales (carnets de extranjería, etc.)
- Ordenar por área o cualquier columna con persistencia del ordenamiento
- Exportación que mantiene todas las ediciones y ordenamiento realizados

### Gestión de DNIs no encontrados
- Ver la lista detallada de yakus no encontrados en un área específica
- Buscar estos yakus en toda la base de datos por DNI
- Buscar por nombre cuando no se encuentra el DNI
- Reasignar yakus a otras áreas cuando sea necesario

## Dependencias

- Python 3.7+
- Streamlit
- Pandas
- NumPy

## Contribuciones

Para contribuir al proyecto, por favor:

1. Crea un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request
