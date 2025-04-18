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

### Ejemplo de datos de Yakus (mentores)

A continuación se muestra un ejemplo anonimizado de cómo se estructura un archivo de datos de Yakus para Arte y Cultura:

| area | correo | horario_lunes | horario_martes | horario_miercoles | horario_jueves | horario_viernes | horario_sabado | horario_domingo | grado | nombre | dni | quechua | celular | taller |
|------|--------|---------------|----------------|-------------------|----------------|-----------------|----------------|-----------------|-------|--------|-----|---------|---------|--------|
| Arte & Cultura | ejemplo1@gmail.com | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | No disponible | No disponible | Mañana (8am -12 m) | Mañana (8am -12 m) | Mañana (8am -12 m) | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | María Pérez García | 70123456 | No lo hablo | 994000111 | Dibujo y Pintura |
| Arte & Cultura | ejemplo2@gmail.com | Mañana (8am -12 m) | Mañana (8am -12 m) | Mañana (8am -12 m) | Mañana (8am -12 m) | Mañana (8am -12 m) | Mañana (8am -12 m) | Mañana (8am -12 m) | Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Carlos Mendoza Torres | 71234567 | No lo hablo | 955222333 | Oratoria |
| Arte & Cultura | ejemplo3@edu.pe | No disponible | No disponible | No disponible | No disponible | No disponible | Mañana (8am -12 m), Tarde (2pm -6 pm), Noche (6pm -10 pm) | Mañana (8am -12 m), Tarde (2pm -6 pm), Noche (6pm -10 pm) | Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Ana Rojas López | 74000111 | Nivel avanzado | 901000222 | Oratoria |
| Arte & Cultura | ejemplo4@gmail.com | No disponible | No disponible | No disponible | No disponible | No disponible | Mañana (8am -12 m), Tarde (2pm -6 pm) | Mañana (8am -12 m), Tarde (2pm -6 pm) | Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Pablo Huamán Quispe | 74222333 | Nivel básico | 965000444 | Teatro |
| Arte & Cultura | ejemplo5@edu.pe | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | Mañana (8am -12 m) | Mañana (8am -12 m) | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | Lucía García Torres | 77444555 | Nivel intermedio | 901000666 | Música |
| Arte & Cultura | ejemplo6@edu.pe | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Tarde (2pm -6 pm), Noche (6pm -10 pm) | Mañana (8am -12 m), Tarde (2pm -6 pm) | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | Rosa Vallejos Prado | 72555666 | No lo hablo | 925000777 | Danza |
| Arte & Cultura | ejemplo7@gmail.com | No disponible | Noche (6pm -10 pm) | No disponible | Noche (6pm -10 pm) | No disponible | No disponible | No disponible | Primaria (3° y 4° grado) | Jorge Paredes Díaz | 74666777 | No lo hablo | 984000888 | Cuenta cuentos |
| Arte & Cultura | ejemplo8@gmail.com | Mañana (8am -12 m) | Mañana (8am -12 m) | No disponible | No disponible | No disponible | Tarde (2pm -6 pm) | No disponible | Primaria (3° y 4° grado) | Carmen Ruiz Flores | 71666888 | No lo hablo | 983000999 | Oratoria |

**Notas sobre los datos de Yakus:**

- **Área de voluntariado**: En este ejemplo todos pertenecen a "Arte & Cultura", pero también puede ser "Asesoría a Colegios Nacionales" o "Bienestar Psicológico".
- **Correo electrónico**: Se utiliza para contactar al Yaku y enviarle información sobre su asignación.
- **Horarios disponibles**: Cada día puede tener una o varias opciones: "Mañana (8am -12 m)", "Tarde (2pm -6 pm)", "Noche (6pm -10 pm)" o estar vacío (no disponible).
- **Grados escolares**: Pueden ser uno o varios: "Primaria (3° y 4° grado)", "Primaria (5° y 6° grado)", "Secundaria (1°, 2° y 3° grado)".
- **Nivel de Quechua**: Puede ser "No lo hablo", "Nivel básico", "Nivel intermedio", "Nivel avanzado" o "Nativo".
- **Taller**: Corresponde al taller específico dentro del área de Arte y Cultura. Opciones comunes incluyen "Dibujo y Pintura", "Música", "Danza", "Teatro", "Oratoria" y "Cuenta cuentos".

#### Ejemplo de datos de Yakus para Bienestar Psicológico

En el caso de Bienestar Psicológico, la estructura es similar pero sin las columnas de taller y asignatura:

| area | correo | horario_lunes | horario_martes | horario_miercoles | horario_jueves | horario_viernes | horario_sabado | horario_domingo | grado | nombre | dni | quechua | celular |
|------|--------|---------------|----------------|-------------------|----------------|-----------------|----------------|-----------------|-------|--------|-----|---------|---------|
| Bienestar Psicológico | ejemplo10@gmail.com | No disponible | No disponible | Noche (6pm -10 pm) | Noche (6pm -10 pm) | No disponible | No disponible | No disponible | Primaria (3° y 4° grado), Primaria (5° y 6° grado) | Laura Martínez Valverde | 72800000 | Nivel básico | 981500000 |
| Bienestar Psicológico | ejemplo11@gmail.com | Tarde (2pm -6 pm) | No disponible | Mañana (8am -12 m) | No disponible | Mañana (8am -12 m), Tarde (2pm -6 pm) | Mañana (8am -12 m), Tarde (2pm -6 pm) | Mañana (8am -12 m) | Primaria (3° y 4° grado), Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Gabriel Casas Oropeza | 75800000 | No lo hablo | 992600000 |
| Bienestar Psicológico | ejemplo12@hotmail.com | No disponible | Mañana (8am -12 m) | No disponible | Mañana (8am -12 m) | No disponible | No disponible | No disponible | Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Sofía Pacheco Silva | 47100000 | No lo hablo | 986300000 |
| Bienestar Psicológico | ejemplo13@gmail.com | No disponible | No disponible | No disponible | No disponible | No disponible | Noche (6pm -10 pm) | Mañana (8am -12 m), Tarde (2pm -6 pm), Noche (6pm -10 pm) | Secundaria (1°, 2° y 3° grado) | Daniel Pro Chillitupa | 76800000 | No lo hablo | 965200000 |
| Bienestar Psicológico | ejemplo14@gmail.com | Mañana (8am -12 m) | Tarde (2pm -6 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Paula Guzmán Taco | 60400000 | No lo hablo | 995500000 |
| Bienestar Psicológico | ejemplo15@edu.pe | Mañana (8am -12 m), Tarde (2pm -6 pm), Noche (6pm -10 pm) | No disponible | No disponible | No disponible | No disponible | No disponible | Mañana (8am -12 m) | Primaria (3° y 4° grado), Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado) | Jimena Meneses Lapad | 60900000 | Nivel básico | 929400000 |

**Notas sobre los datos de Bienestar Psicológico:**
- A diferencia de Arte & Cultura, no incluye las columnas de taller ni asignatura.
- Los Yakus en esta área brindan apoyo psicológico y emocional a los Rurus.
- Los patrones de horarios y disponibilidad son similares a los de otras áreas.
- La compatibilidad con el nivel de quechua sigue siendo importante para la comunicación efectiva.

#### Ejemplo de datos de Yakus para Asesoría a Colegios Nacionales (ACN)

Para el área de Asesoría a Colegios Nacionales, la estructura incluye la columna de asignatura pero no la de taller:

| area | correo | horario_lunes | horario_martes | horario_miercoles | horario_jueves | horario_viernes | horario_sabado | horario_domingo | grado | nombre | dni | quechua | celular | asignatura |
|------|--------|---------------|----------------|-------------------|----------------|-----------------|----------------|-----------------|-------|--------|-----|---------|---------|------------|
| Asesoría a Colegios Nacionales | ejemplo20@gmail.com | "Mañana (8am -12 m), Tarde (2pm -6 pm)" | | | | Tarde (2pm -6 pm) | "Mañana (8am -12 m), Tarde (2pm -6 pm)" | "Mañana (8am -12 m), Tarde (2pm -6 pm)" | "Primaria (3° y 4° grado), Primaria (5° y 6° grado)" | Ana Sánchez Cervantes | 72970000 | No lo hablo | 926970000 | "Inglés, Matemática" |
| Asesoría a Colegios Nacionales | ejemplo21@gmail.com | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | "Primaria (3° y 4° grado), Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado)" | Julia Vilca Quispe | 70343000 | No lo hablo | 979410000 | "Inglés, Matemática" |
| Asesoría a Colegios Nacionales | ejemplo22@gmail.com | | "Tarde (2pm -6 pm), Noche (6pm -10 pm)" | "Tarde (2pm -6 pm), Noche (6pm -10 pm)" | Tarde (2pm -6 pm) | Mañana (8am -12 m) | Mañana (8am -12 m) | | "Primaria (3° y 4° grado), Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado)" | Kiara Yashira Solís | 60075000 | No lo hablo | 983870000 | "Comunicación, Matemática" |
| Asesoría a Colegios Nacionales | ejemplo23@pronabec.edu.pe | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Noche (6pm -10 pm) | Tarde (2pm -6 pm) | Tarde (2pm -6 pm) | Primaria (5° y 6° grado) | Dilmer Delgado Vera | 71548000 | Nivel intermedio | 943800000 | "Inglés, Matemática" |
| Asesoría a Colegios Nacionales | ejemplo24@gmail.com | Noche (6pm -10 pm) | Tarde (2pm -6 pm) | Noche (6pm -10 pm) | Mañana (8am -12 m) | Noche (6pm -10 pm) | Mañana (8am -12 m) | Mañana (8am -12 m) | "Secundaria (1°, 2° y 3° grado)" | Saori Anely Martínez | 74656000 | No lo hablo | 932450000 | Comunicación |
| Asesoría a Colegios Nacionales | ejemplo25@gmail.com | | Noche (6pm -10 pm) | | Noche (6pm -10 pm) | | "Mañana (8am -12 m), Tarde (2pm -6 pm)" | Mañana (8am -12 m) | "Primaria (5° y 6° grado), Secundaria (1°, 2° y 3° grado)" | Judith Sánchez Jesús | 73883000 | Nivel básico | 983870000 | "Comunicación, Inglés" |

**Notas sobre los datos de Asesoría a Colegios Nacionales:**
- Esta área incluye una columna de **asignatura** en lugar de taller, con valores como "Comunicación", "Inglés" y "Matemática".
- Los Yakus en esta área brindan refuerzo escolar en materias académicas específicas.
- Al igual que en otras áreas, los horarios se expresan como "Mañana (8am -12 m)", "Tarde (2pm -6 pm)" o "Noche (6pm -10 pm)".
- Algunos Yakus pueden enseñar múltiples asignaturas, como "Comunicación, Inglés, Matemática".
- La estructura de grados y disponibilidad por día sigue el mismo patrón que en otras áreas.

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
