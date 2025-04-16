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
│   │   │   ├── export_tab.py      # Tab de exportación
│   │   │   ├── file_explorer_tab.py # Tab de explorador de archivos
│   │   │   ├── yaku_process_tab.py # Tab de procesamiento de yakus
│   │   │   ├── ruru_process_tab.py # Tab de procesamiento de rurus
│   │   │   ├── courses_process_tab.py # Tab de procesamiento de cursos
│   │   │   └── config_tab.py      # Tab de configuración
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
    ├── data_utils.py              # Utilidades para manejo de datos (carga/guardado)
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
    
  - **file_explorer_tab.py**: Implementa el tab para explorar archivos temporales con:
    - Listado de archivos en el directorio temporal
    - Información de tamaño y fecha de modificación
    - Opciones para eliminar archivos
    
  - **yaku_process_tab.py**: Implementa el tab para procesar datos de yakus con:
    - Carga de archivos xlsx/csv de yakus
    - Visualización de datos y estadísticas
    - Procesamiento y exportación de datos
    
  - **ruru_process_tab.py**: Implementa el tab para procesar datos de rurus con:
    - Carga de archivos xlsx/csv de rurus
    - Identificación automática de columnas relevantes
    - Procesamiento y estandarización de datos
    - Exportación en diversos formatos
    
  - **courses_process_tab.py**: Implementa el tab para procesar datos de cursos con:
    - Carga de archivos de cursos
    - Estandarización de nombres de cursos
    - Exportación de datos procesados
    
  - **config_tab.py**: Implementa el tab de configuración con:
    - Opciones para formato de DNI/Pasaporte
    - Configuración de formato de nombres
    - Opciones de estandarización y limpieza

- **components/**:
  - **data_validators.py**: Componentes para validar datos como DNI y correo electrónico.
  - **data_handlers.py**: Funciones para manejar operaciones con datos como actualización de DNI y ordenamiento.
  - **file_handlers.py**: Funciones para exportar datos a diferentes formatos.

### Pages/Email

- **email_page.py**: Implementa la funcionalidad para enviar emails a Yakus y Rurus con sus asignaciones.

### Utils

- **match_algorithm.py**: Contiene las clases `Yaku`, `Ruru`, `MatchMaker` y `ReportGenerator` que implementan el algoritmo de matching.
- **data_processors.py**: Funciones utilitarias para el procesamiento de datos (estandarización de DNIs, validación de emails, etc.).
- **data_utils.py**: Funciones para cargar y guardar datos, así como gestionar archivos temporales.
- **email_sender.py**: Implementa la funcionalidad para enviar emails.

## Ejemplos de Datos

### Ejemplo de datos de Rurus (estudiantes)

A continuación se muestra un ejemplo anonimizado de cómo se estructura típicamente un archivo de datos de Rurus:

| ID | Nombres | Apellidos | DNI | Grado | Nivel | Edad | Zona | Horario_Lunes | Horario_Martes | Horario_Miércoles | Horario_Jueves | Horario_Viernes | Preferencia_Curso1 | Preferencia_Curso2 | Preferencia_Curso3 | Nivel_Quechua | Email_Contacto | Teléfono_Contacto |
|----|---------|-----------|-----|-------|-------|------|------|---------------|----------------|-------------------|----------------|-----------------|-------------------|-------------------|-------------------|---------------|----------------|-------------------|
| 1 | Ana María | García López | 71234567 | 5to | Primaria | 11 | Cusco - San Sebastián | Tarde | No disponible | Tarde | No disponible | Mañana | Matemática | Dibujo y Pintura | Comunicación | No lo hablo | padre_ana@ejemplo.com | 987654321 |
| 2 | Carlos | Huamán Quispe | 72345678 | 6to | Primaria | 12 | Cusco - Centro | No disponible | Tarde | No disponible | Tarde | No disponible | Inglés | Teatro | Música | Nivel básico | madre_carlos@ejemplo.com | 912345678 |
| 3 | Lucía | Mamani Torres | 73456789 | 1ro | Secundaria | 13 | Cusco - San Jerónimo | Mañana | No disponible | Mañana | No disponible | Tarde | Comunicación | Matemática | Danza | No lo hablo | tio_lucia@ejemplo.com | 998765432 |
| 4 | Pedro | Condori Huamaní | 74567890 | 2do | Secundaria | 14 | Cusco - Wanchaq | No disponible | Mañana | No disponible | Mañana | No disponible | Música | Comunicación | Dibujo y Pintura | Nivel intermedio | abuelo_pedro@ejemplo.com | 945678123 |
| 5 | Rosa | Sánchez Puma | 75678901 | 3ro | Secundaria | 15 | Cusco - Santiago | Tarde | No disponible | Tarde | No disponible | Tarde | Matemática | Inglés | Cuenta cuentos | Nivel básico | madre_rosa@ejemplo.com | 934567812 |

**Notas sobre los datos de Rurus:**

- **Identificación**: DNI de 8 dígitos (formato peruano) o formato alfanumérico para pasaportes extranjeros.
- **Grado y Nivel**: Combina grado específico (1ro, 2do, etc.) con nivel educativo (Primaria/Secundaria).
- **Horarios**: Normalmente se expresan como "Mañana", "Tarde", "Noche" o "No disponible" para cada día de la semana.
- **Preferencias de cursos**: Incluyen 2-3 opciones ordenadas por preferencia. Estas deben coincidir con los cursos ofrecidos por los yakus.
- **Nivel de Quechua**: Puede ser "No lo hablo", "Nivel básico", "Nivel intermedio", "Nivel avanzado" o "Nativo".
- **Contacto**: Generalmente corresponde a un familiar responsable (padre, madre, tutor).

### Ejemplo de datos de Yakus (mentores)

A continuación se muestra un ejemplo anonimizado de cómo se estructura típicamente un archivo de datos de Yakus:

| Área de voluntariado | Correo electrónico | Horarios [Lunes] | Horarios [Miércoles] | Horarios [Domingo] | Niveles educativos | Nombre completo | DNI o Pasaporte | Nivel de Quechua | Horarios [Viernes] | Horarios [Martes] | Teléfono móvil | Taller dentro del área | Asignaturas | Horarios [Jueves] | Horarios [Sábado] |
|----------------------|--------------------|-----------------|--------------------|-------------------|-------------------|----------------|----------------|-----------------|-------------------|-------------------|----------------|------------------------|------------|------------------|-------------------|
| Arte & Cultura | ejemplo1@gmail.com | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | No disponible | Primaria (3° y 4° grado) | Roberto Yimi Torres Castro | 71XXXXXX | No lo hablo | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | 97XXXXXXX | Música | No aplica | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) |
| Arte & Cultura | ejemplo2@gmail.com | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Tarde (2pm -6 pm) | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | Edith Sánchez López | 74XXXXXX | Nativo | Noche (6pm -10 pm) | Noche (6pm -10 pm) | 91XXXXXXX | Dibujo y Pintura | No aplica | Noche (6pm -10 pm) | Tarde (2pm -6 pm) |
| Arte & Cultura | ejemplo3@hotmail.com | Tarde (2pm -6 pm) | No disponible | Mañana (8am -12 m) | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | Milena Brigitte Cuenca Torres | 01XXXXXXX | No lo hablo | Mañana (8am -12 m) | Tarde (2pm -6 pm) | 99XXXXXXX | Dibujo y Pintura | No aplica | No disponible | Mañana (8am -12 m) |
| Arte & Cultura | ejemplo4@gmail.com | Mañana (8am -12 m) | Mañana, Tarde | Mañana, Tarde | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | Kelly Suliana Rodríguez Pérez | 72XXXXXX | Nativo | Tarde, Noche | Mañana, Tarde | 90XXXXXXX | Cuenta cuentos | No aplica | No disponible | Mañana, Tarde |
| Asesoría a Colegios Nacionales | ejemplo5@gmail.com | Mañana, Tarde | No disponible | Mañana, Tarde | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | Ana Shirley Condori Mamani | 72XXXXXX | No lo hablo | Tarde (2pm -6 pm) | No disponible | 92XXXXXXX | No aplica | Inglés, Matemática | No disponible | Mañana, Tarde |
| Asesoría a Colegios Nacionales | ejemplo6@gmail.com | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Primaria (3° y 4° grado), Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Julissa Mendoza Quispe | 70XXXXXX | No lo hablo | Noche (6pm -10 pm) | Noche (6pm -10 pm) | 97XXXXXXX | No aplica | Inglés, Matemática | Noche (6pm -10 pm) | Noche (6pm -10 pm) |
| Asesoría a Colegios Nacionales | ejemplo7@gmail.com | No disponible | Tarde, Noche | No disponible | Primaria (3° y 4° grado), Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Kiara Yashira Flores López | 60XXXXXX | No lo hablo | Mañana (8am -12 m) | Tarde, Noche | 98XXXXXXX | No aplica | Comunicación, Matemática | Tarde (2pm -6 pm) | Mañana (8am -12 m) |
| Bienestar Psicológico | ejemplo8@gmail.com | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | No disponible | Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Mario José Cáceres Torres | 43XXXXXX | Nivel básico | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | 95XXXXXXX | No aplica | No aplica | Tarde (2pm -6 pm) | No disponible |

**Notas sobre los datos de Yakus:**

- **Área de voluntariado**: Puede ser "Arte & Cultura", "Asesoría a Colegios Nacionales" o "Bienestar Psicológico".
- **Horarios disponibles**: Normalmente se expresan como "Mañana (8am -12 m)", "Tarde (2pm -6 pm)" o "Noche (6pm -10 pm)" para cada día de la semana.
- **Niveles educativos**: Indica los grados escolares con los que el Yaku puede trabajar.
- **Nivel de Quechua**: Puede ser "No lo hablo", "Nivel básico", "Nivel intermedio", "Nivel avanzado" o "Nativo".
- **Taller/Asignatura**: 
  - Para "Arte & Cultura": Pueden ser "Cuenta cuentos", "Dibujo y Pintura", "Música", "Oratoria", "Teatro" o "Danza".
  - Para "Asesoría a Colegios Nacionales": Pueden ser "Comunicación", "Inglés" o "Matemática".
  - Para "Bienestar Psicológico": Normalmente es "Facilitador psicoeducativo".

### Estructura esperada después del procesamiento

Para que el algoritmo de matching funcione correctamente, los datos de Yakus y Rurus deben ser procesados para tener una estructura estandarizada. Después del procesamiento, los datos deberían tener este formato:

#### Rurus procesados

| ID | Nombre | DNI | Grado | Horario_Lunes | Horario_Martes | Horario_Miércoles | Horario_Jueves | Horario_Viernes | Preferencia_Curso1 | Preferencia_Curso2 | Nivel_Quechua | Contacto |
|----|--------|-----|-------|---------------|----------------|-------------------|----------------|-----------------|-------------------|-------------------|---------------|----------|
| 1 | Ana María García L. | 71234567 | Primaria (5° y 6° grado) | Tarde | No disponible | Tarde | No disponible | Mañana | Matemática | Dibujo y Pintura | No lo hablo | padre_ana@ejemplo.com |
| 2 | Carlos Huamán Q. | 72345678 | Primaria (5° y 6° grado) | No disponible | Tarde | No disponible | Tarde | No disponible | Inglés | Teatro | Nivel básico | 912345678 |

#### Yakus procesados

| ID | Nombre | DNI | Área | Opciones | Horario_Lunes | Horario_Martes | Horario_Miércoles | Horario_Jueves | Horario_Viernes | Nivel_Quechua | Grados | Contacto |
|----|--------|-----|------|---------|---------------|----------------|-------------------|----------------|-----------------|---------------|--------|----------|
| 1 | Roberto Torres C. | 71XXXXXX | Arte & Cultura | Música | Tarde | Tarde | Tarde | Tarde | Tarde | No lo hablo | Primaria (3° y 4° grado) | ejemplo1@gmail.com |
| 2 | Edith Sánchez L. | 74XXXXXX | Arte & Cultura | Dibujo y Pintura | Noche | Noche | Noche | Noche | Noche | Nativo | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | 91XXXXXXX |
| 3 | Ana Condori M. | 72XXXXXX | Asesoría a Colegios Nacionales | Inglés, Matemática | Mañana, Tarde | No disponible | No disponible | No disponible | Tarde | No lo hablo | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | ejemplo5@gmail.com |

Esto permite que el algoritmo de matching pueda comparar eficientemente las preferencias, disponibilidad horaria, niveles educativos y otros criterios importantes para la asignación.

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

5. Para trabajar en el procesamiento de rurus:
   - `pages/preprocessing/tabs/ruru_process_tab.py`

6. Para trabajar en el procesamiento de yakus:
   - `pages/preprocessing/tabs/yaku_process_tab.py`

7. Para trabajar en el procesamiento de cursos:
   - `pages/preprocessing/tabs/courses_process_tab.py`

8. Para modificar la configuración:
   - `pages/preprocessing/tabs/config_tab.py`

9. Para modificar los componentes reutilizables:
   - `pages/preprocessing/components/data_validators.py`
   - `pages/preprocessing/components/data_handlers.py`
   - `pages/preprocessing/components/file_handlers.py`

10. Características principales de preprocesamiento:
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
