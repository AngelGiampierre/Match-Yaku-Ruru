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
│   ├── preprocessing/             # Pre-procesamiento
│   │   ├── __init__.py
│   │   └── preprocess_page.py     # Página de preprocesamiento
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

### Pages/Preprocessing

- **preprocess_page.py**: Implementa la funcionalidad para limpiar y preparar datos antes del match.

### Pages/Email

- **email_page.py**: Implementa la funcionalidad para enviar emails a Yakus y Rurus con sus asignaciones.

### Utils

- **match_algorithm.py**: Contiene las clases `Yaku`, `Ruru`, `MatchMaker` y `ReportGenerator` que implementan el algoritmo de matching.
- **data_processors.py**: Funciones utilitarias para el procesamiento de datos.
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

### Funcionalidad de Preprocesamiento

1. Para desarrollar esta funcionalidad:
   - `pages/preprocessing/preprocess_page.py`
   - `utils/data_processors.py`

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

1. Preprocesar los datos de Yakus y Rurus para asegurar su consistencia
2. Cargar los datos en la funcionalidad de Match
3. Ejecutar el algoritmo para encontrar las mejores asignaciones
4. Enviar emails a los participantes con sus asignaciones

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
