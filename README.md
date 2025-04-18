# Match-Yaku-Ruru
008/100: Este repositorio contiene un algoritmo que mejora la asignación de Yakus (mentores) a Rurus (estudiantes) en Yachay Wasi, una organización educativa de voluntariado. Mediante la automatización del proceso y considerando horarios, áreas temáticas y grados, ahorra tiempo a los voluntarios y mejora las experiencias de aprendizaje de los estudiantes.

## Estructura del Proyecto

La aplicación está estructurada de forma modular para facilitar el mantenimiento y desarrollo independiente de cada funcionalidad:

```
/Match-Yaku-Ruru/
├── app.py                         # Punto de entrada principal (dashboard)
├── assets/                        # Recursos estáticos
│   └── styles.css                 # Estilos CSS separados
│
├── preprocessing/                 # Módulo de preprocesamiento
│   ├── __init__.py
│   ├── preprocessing_main.py      # Integración de tabs
│   ├── tabs/                      # Interfaces de usuario
│   │   ├── __init__.py
│   │   ├── column_selection_tab.py  # Selección de columnas
│   │   ├── dni_validation_tab.py    # Validación de DNIs
│   │   └── filter_area_tab.py       # Filtrado por área
│   ├── ui/                        # Componentes UI reutilizables
│   │   ├── __init__.py
│   │   ├── file_uploaders.py      # Uploaders de archivos
│   │   ├── selectors.py           # Selectores (columnas, IDs)
│   │   └── displays.py            # Visualizadores (estadísticas, edición)
│   ├── data/                      # Procesamiento de datos
│   │   ├── __init__.py
│   │   ├── validators.py          # Validación (DNI, email)
│   │   ├── column_handlers.py     # Manejo de columnas
│   │   └── filters.py             # Filtrado de datos
│   └── utils/                     # Utilidades del preprocesamiento
│       ├── __init__.py
│       ├── file_io.py             # Operaciones con archivos
│       └── temp_storage.py        # Almacenamiento temporal
│
├── match/                         # Módulo de match (a implementar)
│   └── ...
│
├── email/                         # Módulo de envío de emails (a implementar)
│   └── ...
│
└── shared/                        # Utilidades compartidas
    ├── __init__.py
    └── session_state.py           # Gestión del estado de sesión
```

## Descripción de los módulos principales

### Aplicación Principal

- **app.py**: Punto de entrada de la aplicación. Integra los diferentes módulos (preprocesamiento, match, envío de correos) y proporciona navegación entre ellos.

### Módulo de Preprocesamiento

El módulo de preprocesamiento está estructurado siguiendo un enfoque modular que separa claramente las responsabilidades:

#### Tabs (Interfaces de Usuario)

- **column_selection_tab.py**: Permite cargar un archivo, seleccionar columnas relevantes y exportar el resultado.
- **dni_validation_tab.py**: Valida y corrige DNIs o correos electrónicos en un archivo, mostrando estadísticas y permitiendo ediciones.
- **filter_area_tab.py**: Filtra datos por área y por una lista de identificadores (DNI, correo, nombre).

#### Componentes de UI

- **file_uploaders.py**: Componentes reutilizables para cargar archivos y mostrar botones de descarga.
- **selectors.py**: Componentes para seleccionar columnas, IDs, áreas, etc.
- **displays.py**: Componentes para mostrar datos, estadísticas y interfaces de edición.

#### Procesamiento de Datos

- **validators.py**: Funciones para validar DNIs, correos electrónicos y otros datos.
- **column_handlers.py**: Funciones para manipular columnas (actualizar valores, estandarizar, etc.).
- **filters.py**: Funciones para filtrar datos por diferentes criterios.

#### Utilidades

- **file_io.py**: Funciones para cargar y guardar archivos en diferentes formatos.
- **temp_storage.py**: Sistema para almacenar y recuperar datos temporales entre tabs.

### Utilidades Compartidas

- **session_state.py**: Funciones para gestionar el estado de sesión entre módulos.

## Funcionalidades implementadas

### Preprocesamiento

1. **Selección de Columnas**
   - Carga de archivos Excel/CSV
   - Detección automática de columnas importantes (DNI, nombre, email, etc.)
   - Selección por categoría o individual
   - Exportación en diferentes formatos

2. **Validación de DNIs/Correos**
   - Validación automática de formatos de DNI y correo electrónico
   - Estandarización automática de valores
   - Interfaz para editar valores inválidos
   - Estadísticas detalladas de validación
   - Exportación de datos corregidos

3. **Filtrado por Área**
   - Detección automática de columnas de área e identificadores
   - Filtrado por área específica
   - Filtrado por lista de IDs (DNI, correo, nombre)
   - Manejo de IDs no encontrados
   - Exportación de resultados filtrados

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

**Notas sobre los datos de Yakus:**

- **Área de voluntariado**: Puede ser "Arte & Cultura", "Asesoría a Colegios Nacionales" o "Bienestar Psicológico".
- **Horarios disponibles**: Normalmente se expresan como "Mañana (8am -12 m)", "Tarde (2pm -6 pm)" o "Noche (6pm -10 pm)" para cada día de la semana.
- **Niveles educativos**: Indica los grados escolares con los que el Yaku puede trabajar.
- **Nivel de Quechua**: Puede ser "No lo hablo", "Nivel básico", "Nivel intermedio", "Nivel avanzado" o "Nativo".

## Ventajas de la estructura modular

1. **Separación de responsabilidades**: Cada componente tiene una única función bien definida
2. **Reutilización de código**: Los componentes comunes se comparten entre diferentes tabs
3. **Mantenibilidad**: Es más fácil localizar y corregir problemas
4. **Escalabilidad**: Facilita la adición de nuevas funcionalidades
5. **Testabilidad**: Los componentes independientes son más fáciles de probar

## Ejecutando la aplicación

Para ejecutar la aplicación:

```bash
streamlit run app.py
```

## Dependencias

- Python 3.7+
- Streamlit
- Pandas
- NumPy

## Próximos pasos

1. Implementación del módulo de Match para la asignación automática
2. Implementación del módulo de Envío de Correos
3. Mejoras en la interfaz de usuario
4. Implementación de pruebas unitarias
