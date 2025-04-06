from itertools import product
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

# Actualización de la estructura de datos:
# - Yakus: Se agregaron campos de información personal (nombre, DNI, celular, correo)
# - Yakus: Nuevo campo "area" con tres opciones: "Arte & Cultura", "Bienestar Psicológico", "Asesoría a Colegios Nacionales"
# - Yakus: Opciones específicas por área
# - Yakus: Nuevo campo "num_beneficiarios"  
# - Yakus: Cambio en el manejo de horarios, ahora por períodos (Mañana, Tarde, Noche)
# - Yakus: Nuevo campo "nivel_quechua" reemplazando el campo "idioma"
# - Yakus: Grados ahora con valores fijos: "Primaria (3° y 4° grado)", "Primaria (5° y 6° grado)", "Secundaria (1°, 2° y 3° grado)"
# - Rurus: Adaptados para mantener compatibilidad con la nueva estructura

# Siguientes pasos:
# - Uniformizar formularios de inscripción de yakus y rurus
# - Conectar formularios con el algoritmo

class Ruru:
    def __init__(self, nombre, opciones, disponibilidad, idioma, grado, area=None):
        self.nombre = nombre
        self.opciones = opciones  # Lista de opciones en orden de preferencia
        self.disponibilidad = disponibilidad  # Diccionario con horarios por día
        self.idioma = idioma
        self.grado = grado  # Grado escolar del Ruru
        # Nuevo campo área para mantener compatibilidad con los Yakus
        self.area = area if area else "Estudiante"  # Por defecto es estudiante

class Yaku:
    def __init__(self, nombre, dni, celular, correo, area, opciones, num_beneficiarios, disponibilidad, nivel_quechua, grados):
        self.nombre = nombre
        self.dni = dni
        self.celular = celular
        self.correo = correo
        self.area = area  # "Arte & Cultura", "Bienestar Psicológico", o "Asesoría a Colegios Nacionales"
        self.opciones = opciones  # Lista de opciones según el área
        self.num_beneficiarios = num_beneficiarios  # Número de beneficiarios a atender
        self.disponibilidad = disponibilidad  # Diccionario con horarios por día
        self.nivel_quechua = nivel_quechua  # Nivel de idioma quechua
        self.grados = grados  # Lista de grados que puede enseñar

class MatchMaker:
    def __init__(self):
        self._cache_intersecciones = {}
    
    def es_idioma_compatible(self, idioma_ruru, nivel_quechua_yaku):
        """
        Verifica si el nivel de quechua del Yaku es compatible con el idioma del Ruru.
        Un Ruru con "Español y Quechua" necesita un Yaku con al menos nivel básico de quechua.
        """
        if idioma_ruru == "Español":
            return True  # Un Ruru que habla español es compatible con cualquier Yaku
        # Para un Ruru que habla "Español y Quechua", el Yaku necesita algún nivel de quechua
        if idioma_ruru == "Español y Quechua" and nivel_quechua_yaku != "No lo hablo":
            return True
        return False

    def _es_match_valido(self, ruru, yaku):
        """
        Verifica si hay al menos una opción en común, nivel de quechua compatible y grado válido.
        """
        return (
            any(opcion in yaku.opciones for opcion in ruru.opciones) and
            self.es_idioma_compatible(ruru.idioma, yaku.nivel_quechua) and
            ruru.grado in yaku.grados
        )

    def calcular_horas_asignadas(self, interseccion):
        """
        Calcula cuántas horas hay en la intersección de horarios.
        """
        total_horas = 0
        for dia, rangos in interseccion.items():
            for (inicio, fin) in rangos:
                h1 = (inicio // 100) + (inicio % 100) / 60
                h2 = (fin // 100) + (fin % 100) / 60
                total_horas += (h2 - h1)
        return round(total_horas, 1)

    def encontrar_interseccion(self, horarios_ruru, horarios_yaku):
        # Crear una clave única para esta combinación de horarios
        clave = (
            tuple((d, tuple(h)) for d,h in sorted(horarios_ruru.items())),
            tuple((d, tuple(h)) for d,h in sorted(horarios_yaku.items()))
        )
        
        if clave not in self._cache_intersecciones:
            self._cache_intersecciones[clave] = self._calcular_interseccion(horarios_ruru, horarios_yaku)
        
        return self._cache_intersecciones[clave]

    def _calcular_interseccion(self, horarios_ruru, horarios_yaku):
        """
        Calcula la intersección de horarios entre un Ruru y un Yaku.
        Retorna un diccionario con los rangos de tiempo que coinciden.
        """
        interseccion = {}
        
        # Iterar sobre los días que aparecen en ambos horarios
        dias_comunes = set(horarios_ruru.keys()) & set(horarios_yaku.keys())
        
        for dia in dias_comunes:
            rangos_ruru = horarios_ruru[dia]
            rangos_yaku = horarios_yaku[dia]
            
            # Encontrar intersecciones para cada combinación de rangos
            rangos_interseccion = []
            for (inicio_r, fin_r) in rangos_ruru:
                for (inicio_y, fin_y) in rangos_yaku:
                    # Calcular el rango de intersección
                    inicio = max(inicio_r, inicio_y)
                    fin = min(fin_r, fin_y)
                    
                    if inicio < fin:  # Si hay intersección
                        rangos_interseccion.append((inicio, fin))
            
            # Si encontramos intersecciones para este día, las guardamos
            if rangos_interseccion:
                interseccion[dia] = rangos_interseccion
        
        return interseccion

    def encontrar_match(self, rurus, yakus):
        matches_principales = []
        matches_secundarios = []

        # Diccionario para llevar cuenta de cuántos Rurus tiene cada Yaku
        rurus_por_yaku = {yaku.nombre: 0 for yaku in yakus}

        # Fase 1: matches de 2+ horas
        for ruru in rurus:
            mejor_match = None
            mejor_horas = 0.0
            menor_carga = float('inf')  # Para contar cuántos Rurus ya tiene el Yaku

            for yaku in yakus:
                if self._es_match_valido(ruru, yaku):
                    inter = self.encontrar_interseccion(ruru.disponibilidad, yaku.disponibilidad)
                    horas = self.calcular_horas_asignadas(inter)
                    if horas >= 2:
                        carga_actual = rurus_por_yaku[yaku.nombre]
                        # Priorizar Yakus con menos carga
                        if (horas > mejor_horas) or (horas == mejor_horas and carga_actual < menor_carga):
                            mejor_horas = horas
                            menor_carga = carga_actual
                            opcion_comun = next(op for op in ruru.opciones if op in yaku.opciones)
                            mejor_match = (ruru.nombre, yaku.nombre, opcion_comun, inter, 0)

            if mejor_match:
                matches_principales.append(mejor_match)
                # Actualizar el contador de Rurus para este Yaku
                rurus_por_yaku[mejor_match[1]] += 1

        # Identificar rurus sin match principal 
        rurus_sin_match = [r for r in rurus if not any(m[0] == r.nombre for m in matches_principales)]
        
        # Fase 2: matches de 1+ hora (similar a la fase 1 pero con diferente umbral de horas)
        for ruru in rurus_sin_match:
            mejor_match = None
            mejor_horas = 0.0
            menor_carga = float('inf')

            for yaku in yakus:
                if self._es_match_valido(ruru, yaku):
                    inter = self.encontrar_interseccion(ruru.disponibilidad, yaku.disponibilidad)
                    horas = self.calcular_horas_asignadas(inter)
                    if horas >= 1:
                        carga_actual = rurus_por_yaku[yaku.nombre]
                        if (horas > mejor_horas) or (horas == mejor_horas and carga_actual < menor_carga):
                            mejor_horas = horas
                            menor_carga = carga_actual
                            opcion_comun = next(op for op in ruru.opciones if op in yaku.opciones)
                            mejor_match = (ruru.nombre, yaku.nombre, opcion_comun, inter, 0)

            if mejor_match:
                matches_secundarios.append(mejor_match)
                rurus_por_yaku[mejor_match[1]] += 1

        total_horas_principales = sum(self.calcular_horas_asignadas(m[3]) for m in matches_principales)
        return matches_principales, matches_secundarios, total_horas_principales

    def _procesar_match(self, ruru, yaku, asignaciones, rurus_restantes, backtrack_fn, yakus_usados):
        if ruru.area == "Bienestar":
            self._procesar_match_bienestar(ruru, yaku, asignaciones, rurus_restantes, backtrack_fn, yakus_usados)
        else:
            self._procesar_match_regular(ruru, yaku, asignaciones, rurus_restantes, backtrack_fn, yakus_usados)

    def _procesar_match_bienestar(self, ruru, yaku, asignaciones, rurus_restantes, backtrack_fn, yakus_usados):
        interseccion_horarios = self.encontrar_interseccion(ruru.disponibilidad, yaku.disponibilidad)
        if interseccion_horarios:
            horas_asignadas = self.calcular_horas_asignadas(interseccion_horarios)
            if horas_asignadas >= 2:
                asignaciones.append((ruru.nombre, yaku.nombre, "Bienestar", interseccion_horarios, 0))
                backtrack_fn(asignaciones, rurus_restantes[1:], yakus_usados)
                asignaciones.pop()

    def _procesar_match_regular(self, ruru, yaku, asignaciones, rurus_restantes, backtrack_fn, yakus_usados):
        for r_opcion in ruru.opciones:
            if r_opcion in yaku.cursos:
                y_preferencia = yaku.preferencias.index(r_opcion) if r_opcion in yaku.preferencias else len(yaku.preferencias)
                interseccion_horarios = self.encontrar_interseccion(ruru.disponibilidad, yaku.disponibilidad)
                if interseccion_horarios:
                    horas_asignadas = self.calcular_horas_asignadas(interseccion_horarios)
                    if horas_asignadas >= 2:
                        asignaciones.append((ruru.nombre, yaku.nombre, r_opcion, interseccion_horarios, y_preferencia))
                        backtrack_fn(asignaciones, rurus_restantes[1:], yakus_usados)
                        asignaciones.pop()

    def diagnosticar_ruru_sin_match(self, ruru, yakus, asignaciones_existentes):
        print(f"\nDiagnóstico para {ruru.nombre}:")
        print(f"Área: {ruru.area}")
        print(f"Idioma: {ruru.idioma}")
        print(f"Grado: {ruru.grado}")
        print(f"Disponibilidad: {self._formato_horario(ruru.disponibilidad)}")
        
        for yaku in yakus:
            print(f"\nAnalizando compatibilidad con {yaku.nombre}:")
            print(f"Área: {yaku.area} - {'✓' if yaku.area == ruru.area else '✗'}")
            print(f"Nivel quechua: {yaku.nivel_quechua} - {'✓' if self.es_idioma_compatible(ruru.idioma, yaku.nivel_quechua) else '✗'}")
            print(f"Grado compatible: {'✓' if ruru.grado in yaku.grados else '✗'}")
            
            # Verificar horarios disponibles
            horarios_disponibles = self._obtener_horarios_disponibles(yaku, asignaciones_existentes)
            interseccion = self.encontrar_interseccion(ruru.disponibilidad, horarios_disponibles)
            if interseccion:
                horas = self.calcular_horas_asignadas(interseccion)
                print(f"Horas posibles: {horas}")
            else:
                print("No hay intersección de horarios")

    def _formato_horario(self, horarios):
        return {dia: [(f"{inicio//100}:{inicio%100:02d}", f"{fin//100}:{fin%100:02d}") 
                      for inicio, fin in slots] 
                for dia, slots in horarios.items()}

    def _obtener_horarios_disponibles(self, yaku, asignaciones):
        """Retorna todos los horarios del Yaku, permitiendo compartir"""
        return yaku.disponibilidad

    def _segunda_fase_matching(self, rurus_restantes, yakus, asignaciones_previas):
        """Segunda fase: emparejar Rurus restantes con Yakus existentes"""
        asignaciones_adicionales = []
        
        for ruru in rurus_restantes:
            mejor_match = None
            mejor_horas = 0
            
            for yaku in yakus:
                if self._es_match_valido(ruru, yaku):
                    # Usar directamente la disponibilidad del Yaku
                    interseccion = self.encontrar_interseccion(ruru.disponibilidad, yaku.disponibilidad)
                    if interseccion:
                        horas = self.calcular_horas_asignadas(interseccion)
                        if horas >= 1:  # Permitir matches de 1+ hora en segunda fase
                            if horas > mejor_horas:
                                mejor_horas = horas
                                mejor_match = (ruru.nombre, yaku.nombre, ruru.area, interseccion, 0)
            
            if mejor_match:
                asignaciones_adicionales.append(mejor_match)
        
        return asignaciones_adicionales

class ReportGenerator:
    def __init__(self, matchmaker):
        self.matchmaker = matchmaker

    def generar_reporte(self, rurus_originales, yakus_originales, mejor_asignacion):
        # Identificar Rurus y Yakus emparejados
        rurus_emparejados = set(match[0] for match in mejor_asignacion)
        yakus_emparejados = set(match[1] for match in mejor_asignacion)
        
        # Identificar los que quedaron sin emparejar
        rurus_sin_match = [ruru for ruru in rurus_originales if ruru.nombre not in rurus_emparejados]
        yakus_sin_match = [yaku for yaku in yakus_originales if yaku.nombre not in yakus_emparejados]
        
        # Buscar matches secundarios
        matches_secundarios = self.encontrar_match_secundario(rurus_sin_match, yakus_sin_match)
        
        # Añadir estadísticas y métricas
        stats = {
            'total_matches': len(mejor_asignacion),
            'promedio_horas': sum(self.matchmaker.calcular_horas_asignadas(m[3]) for m in mejor_asignacion) / len(mejor_asignacion),
            'rurus_sin_match': len(rurus_sin_match),
            'yakus_sin_match': len(yakus_sin_match)
        }
        
        # Generar el reporte
        self._escribir_reporte(mejor_asignacion, matches_secundarios, yakus_sin_match, rurus_sin_match)

    def _escribir_reporte(self, mejor_asignacion, matches_secundarios, yakus_sin_match, rurus_sin_match):
        # Organizamos los matches por Yaku para mostrar todos los Rurus asociados
        matches_por_yaku = {}
        for match in mejor_asignacion:
            yaku_nombre = match[1]
            if yaku_nombre not in matches_por_yaku:
                matches_por_yaku[yaku_nombre] = []
            matches_por_yaku[yaku_nombre].append({
                'ruru': match[0],
                'opcion': match[2],
                'horas': self.matchmaker.calcular_horas_asignadas(match[3])
            })

        # Similar para matches secundarios
        matches_secundarios_por_yaku = {}
        for match in matches_secundarios:
            yaku_nombre = match[1]
            if yaku_nombre not in matches_secundarios_por_yaku:
                matches_secundarios_por_yaku[yaku_nombre] = []
            matches_secundarios_por_yaku[yaku_nombre].append({
                'ruru': match[0],
                'horas': match[2]
            })

        with open('reporte_matches.txt', 'w', encoding='utf-8') as f:
            f.write("=== MATCHES PRINCIPALES (2+ HORAS) ===\n")
            for yaku, matches in matches_por_yaku.items():
                f.write(f"\n{yaku} enseña a:\n")
                for match in matches:
                    f.write(f"  - {match['ruru']} ({match['opcion']}, {match['horas']} horas)\n")
            
            f.write("\n=== MATCHES SECUNDARIOS (1+ HORA) ===\n")
            for yaku, matches in matches_secundarios_por_yaku.items():
                f.write(f"\n{yaku} enseña a:\n")
                for match in matches:
                    f.write(f"  - {match['ruru']} ({match['horas']} horas)\n")
            
            f.write("\n=== YAKUS SIN EMPAREJAR ===\n")
            for yaku in yakus_sin_match:
                f.write(f"{yaku.nombre} (opciones: {', '.join(yaku.opciones)})\n")
                
            f.write("\n=== RURUS SIN EMPAREJAR ===\n")
            for ruru in rurus_sin_match:
                f.write(f"{ruru.nombre}:\n")
                f.write(f"  Opciones: {', '.join(ruru.opciones)}\n")
                f.write(f"  Horarios disponibles:\n")
                for dia, rangos in sorted(ruru.disponibilidad.items()):
                    for inicio, fin in rangos:
                        # Formatear hora de 24h a formato más legible
                        hora_inicio = f"{inicio//100:02d}:{inicio%100:02d}"
                        hora_fin = f"{fin//100:02d}:{fin%100:02d}"
                        f.write(f"    - {dia.capitalize()}: {hora_inicio} a {hora_fin}\n")
                f.write("\n")

    def encontrar_match_secundario(self, rurus_sin_match, yakus_sin_match):
        """
        Ahora, un Yaku no será eliminado de 'yakus_sin_match' al emparejar
        con el primer Ruru. De esta forma, un mismo Yaku podrá
        compartirse entre múltiples Rurus en los matches secundarios.
        """
        matches_secundarios = []
        rurus_a_remover = []

        for ruru in rurus_sin_match:
            for yaku in yakus_sin_match:
                if self._es_match_secundario_valido(ruru, yaku):
                    interseccion_horarios = self.matchmaker.encontrar_interseccion(
                        ruru.disponibilidad, 
                        yaku.disponibilidad
                    )
                    if interseccion_horarios:
                        horas = self.matchmaker.calcular_horas_asignadas(interseccion_horarios)
                        if 1 <= horas < 2:
                            matches_secundarios.append((ruru.nombre, yaku.nombre, horas))
                            rurus_a_remover.append(ruru)
                            break

        # Removemos únicamente a los Rurus que ya se emparejaron
        for ruru in rurus_a_remover:
            if ruru in rurus_sin_match:
                rurus_sin_match.remove(ruru)

        return matches_secundarios

    def _es_match_secundario_valido(self, ruru, yaku):
        """
        Verifica si hay al menos una opción en común, nivel de quechua compatible y grado válido.
        """
        return (
            any(opcion in yaku.opciones for opcion in ruru.opciones) and
            self.matchmaker.es_idioma_compatible(ruru.idioma, yaku.nivel_quechua) and
            ruru.grado in yaku.grados
        )

    def _formato_horario(self, horarios):
        """Convierte horarios del formato 24h a un formato más legible"""
        return {dia: [(f"{inicio//100:02d}:{inicio%100:02d}", 
                      f"{fin//100:02d}:{fin%100:02d}") 
                for inicio, fin in slots] 
                for dia, slots in horarios.items()}

# Función auxiliar para convertir horarios
def convertir_horarios(form_data):
    dias_map = {
        "Lunes": "lunes",
        "Martes": "martes",
        "Miércoles": "miércoles",
        "Jueves": "jueves",
        "Viernes": "viernes",
        "Sábado": "sábado",
        "Domingo": "domingo"
    }
    
    # Definir horarios estándar
    rangos_horarios = {
        "Mañana": (800, 1200),  # 8am a 12m
        "Tarde": (1400, 1800),  # 2pm a 6pm
        "Noche": (1800, 2200)   # 6pm a 10pm
    }
    
    horarios = {}
    for entrada in form_data.split(','):
        partes = entrada.strip().split(' ')
        dia = partes[0]
        periodo = partes[1]
        
        # Convertir nombre del día a formato estándar
        dia = dias_map[dia]
        
        # Obtener el rango horario correspondiente
        inicio, fin = rangos_horarios[periodo]
        
        if dia not in horarios:
            horarios[dia] = []
        horarios[dia].append((inicio, fin))
    
    return horarios

# Ejemplos de Rurus con las opciones permitidas ahora ajustadas a las opciones disponibles para Yakus:
# Para Arte & Cultura: Cuenta cuentos, Dibujo y Pintura, Música, Oratoria, Teatro, Danza
# Para Asesoría a Colegios Nacionales: Comunicación, Inglés, Matemática

ruru1 = Ruru("Ruru1", ["Música", "Matemática"], 
             convertir_horarios("Lunes Tarde, Jueves Tarde"), 
             "Español", "Primaria (5° y 6° grado)")

ruru2 = Ruru("Ruru2", ["Dibujo y Pintura", "Danza"], 
             convertir_horarios("Lunes Tarde, Miércoles Tarde"), 
             "Español y Quechua", "Secundaria (1°, 2° y 3° grado)")

ruru3 = Ruru("Ruru3", ["Matemática", "Inglés"], 
             convertir_horarios("Martes Mañana, Jueves Tarde"), 
             "Español", "Secundaria (1°, 2° y 3° grado)")

ruru4 = Ruru("Ruru4", ["Comunicación", "Oratoria"], 
             convertir_horarios("Miércoles Tarde, Viernes Mañana"), 
             "Español", "Secundaria (1°, 2° y 3° grado)")

ruru5 = Ruru("Ruru5", ["Música", "Inglés"], 
             convertir_horarios("Lunes Tarde, Sábado Mañana"), 
             "Español", "Secundaria (1°, 2° y 3° grado)")

ruru6 = Ruru("Ruru6", ["Matemática", "Teatro"], 
             convertir_horarios("Martes Tarde, Jueves Tarde"), 
             "Español", "Secundaria (1°, 2° y 3° grado)")

ruru7 = Ruru("Ruru7", ["Dibujo y Pintura", "Danza"], 
             convertir_horarios("Lunes Mañana, Miércoles Tarde"), 
             "Español y Quechua", "Primaria (5° y 6° grado)")

ruru8 = Ruru("Ruru8", ["Matemática", "Inglés"], 
             convertir_horarios("Martes Mañana, Jueves Mañana"), 
             "Español", "Primaria (5° y 6° grado)")

ruru9 = Ruru("Ruru9", ["Comunicación", "Oratoria"], 
             convertir_horarios("Miércoles Mañana, Viernes Tarde"), 
             "Español", "Secundaria (1°, 2° y 3° grado)")

ruru10 = Ruru("Ruru10", ["Música", "Facilitador psicoeducativo"], 
              convertir_horarios("Lunes Mañana, Domingo Tarde"), 
              "Español", "Secundaria (1°, 2° y 3° grado)")

# Rurus con horarios específicos
ruru11 = Ruru("Ruru11", ["Dibujo y Pintura", "Teatro"], 
              convertir_horarios("Lunes Mañana"), # Solo un periodo disponible
              "Español", "Secundaria (1°, 2° y 3° grado)")

ruru12 = Ruru("Ruru12", ["Música", "Inglés"], 
              convertir_horarios("Sábado Tarde"), # Horario poco común
              "Español", "Secundaria (1°, 2° y 3° grado)")

ruru13 = Ruru("Ruru13", ["Matemática", "Cuenta cuentos"], 
              convertir_horarios("Domingo Mañana"), # Solo domingo
              "Español y Quechua", "Secundaria (1°, 2° y 3° grado)")

ruru14 = Ruru("Ruru14", ["Comunicación", "Oratoria"], 
              convertir_horarios("Viernes Noche"), # Horario nocturno
              "Español", "Secundaria (1°, 2° y 3° grado)")

ruru15 = Ruru("Ruru15", ["Matemática", "Inglés"], 
              convertir_horarios("Martes Mañana, Jueves Tarde"), 
              "Español", "Secundaria (1°, 2° y 3° grado)")

# Yakus con sus opciones según el nuevo formato
yaku1 = Yaku(
    "Yaku1", 
    "12345678", 
    "999888777", 
    "yaku1@mail.com",
    "Asesoría a Colegios Nacionales", 
    ["Matemática", "Inglés"], 
    3,
    convertir_horarios("Lunes Mañana, Jueves Tarde"), 
    "Nivel básico",
    ["Primaria (5° y 6° grado)", "Secundaria (1°, 2° y 3° grado)"]
)

yaku2 = Yaku(
    "Yaku2", 
    "87654321", 
    "999777666", 
    "yaku2@mail.com",
    "Asesoría a Colegios Nacionales", 
    ["Comunicación"], 
    2,
    convertir_horarios("Martes Tarde, Jueves Tarde"), 
    "No lo hablo",
    ["Secundaria (1°, 2° y 3° grado)"]
)

yaku3 = Yaku(
    "Yaku3", 
    "23456789", 
    "999666555", 
    "yaku3@mail.com",
    "Arte & Cultura", 
    ["Música"], 
    4,
    convertir_horarios("Lunes Mañana, Miércoles Mañana"), 
    "Nivel intermedio",
    ["Primaria (3° y 4° grado)", "Primaria (5° y 6° grado)", "Secundaria (1°, 2° y 3° grado)"]
)

yaku4 = Yaku(
    "Yaku4", 
    "34567890", 
    "999555444", 
    "yaku4@mail.com",
    "Arte & Cultura", 
    ["Dibujo y Pintura"], 
    5,
    convertir_horarios("Martes Tarde, Viernes Tarde"), 
    "No lo hablo",
    ["Primaria (3° y 4° grado)", "Primaria (5° y 6° grado)"]
)

yaku5 = Yaku(
    "Yaku5", 
    "45678901", 
    "999444333", 
    "yaku5@mail.com",
    "Bienestar Psicológico", 
    ["Facilitador psicoeducativo"], 
    6,
    convertir_horarios("Lunes Tarde, Jueves Tarde"), 
    "Nivel avanzado",
    ["Secundaria (1°, 2° y 3° grado)"]
)

# Más ejemplos de Yakus
yaku6 = Yaku(
    "Yaku6", 
    "56789012", 
    "999333222", 
    "yaku6@mail.com",
    "Asesoría a Colegios Nacionales", 
    ["Matemática", "Comunicación", "Inglés"], 
    4,
    convertir_horarios("Lunes Tarde, Jueves Tarde"), 
    "No lo hablo",
    ["Secundaria (1°, 2° y 3° grado)"]
)

yaku7 = Yaku(
    "Yaku7", 
    "67890123", 
    "999222111", 
    "yaku7@mail.com",
    "Arte & Cultura", 
    ["Dibujo y Pintura"], 
    3,
    convertir_horarios("Lunes Mañana, Miércoles Tarde"), 
    "Nativo",
    ["Primaria (3° y 4° grado)", "Primaria (5° y 6° grado)"]
)

yaku8 = Yaku(
    "Yaku8", 
    "78901234", 
    "999111000", 
    "yaku8@mail.com",
    "Arte & Cultura", 
    ["Música"], 
    5,
    convertir_horarios("Lunes Tarde, Sábado Mañana"), 
    "Nivel básico",
    ["Secundaria (1°, 2° y 3° grado)"]
)

yaku9 = Yaku(
    "Yaku9", 
    "89012345", 
    "999000999", 
    "yaku9@mail.com",
    "Asesoría a Colegios Nacionales", 
    ["Comunicación"], 
    2,
    convertir_horarios("Miércoles Tarde, Viernes Mañana"), 
    "No lo hablo",
    ["Secundaria (1°, 2° y 3° grado)"]
)

yaku10 = Yaku(
    "Yaku10", 
    "90123456", 
    "999999888", 
    "yaku10@mail.com",
    "Asesoría a Colegios Nacionales", 
    ["Matemática"], 
    3,
    convertir_horarios("Martes Mañana, Jueves Tarde"), 
    "Nivel básico",
    ["Secundaria (1°, 2° y 3° grado)"]
)

yaku11 = Yaku(
    "Yaku11", 
    "01234567", 
    "999888777", 
    "yaku11@mail.com",
    "Bienestar Psicológico", 
    ["Facilitador psicoeducativo"], 
    4,
    convertir_horarios("Lunes Mañana, Jueves Tarde"), 
    "Nivel intermedio",
    ["Primaria (5° y 6° grado)", "Secundaria (1°, 2° y 3° grado)"]
)

yaku12 = Yaku(
    "Yaku12", 
    "12345670", 
    "999777666", 
    "yaku12@mail.com",
    "Asesoría a Colegios Nacionales", 
    ["Matemática", "Inglés"], 
    5,
    convertir_horarios("Martes Mañana, Jueves Mañana"), 
    "No lo hablo",
    ["Primaria (5° y 6° grado)"]
)

# Actualizar las listas
rurus_lista = [ruru1, ruru2, ruru3, ruru4, ruru5, ruru6, ruru7, ruru8, ruru9, ruru10,
               ruru11, ruru12, ruru13, ruru14, ruru15]
yakus_lista = [yaku1, yaku2, yaku3, yaku4, yaku5, yaku6, yaku7, yaku8, yaku9, yaku10, yaku11, yaku12]

matchmaker = MatchMaker()
report_generator = ReportGenerator(matchmaker)

mejor_asignacion, matches_secundarios, max_horas = matchmaker.encontrar_match(rurus_lista, yakus_lista)
report_generator.generar_reporte(rurus_lista, yakus_lista, mejor_asignacion)

print("Se ha generado el archivo 'reporte_matches.txt' con los resultados")

class GoogleSheetReader:
    def __init__(self, credentials_path, spreadsheet_id):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.service = self._get_service()

    def _get_service(self):
        """Configura y retorna el servicio de Google Sheets."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.scopes
            )
            return build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            print(f"Error al configurar el servicio: {e}")
            return None

    def leer_datos(self, rango):
        """Lee datos de un rango específico de la hoja."""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=rango
            ).execute()
            
            valores = result.get('values', [])
            if not valores:
                print('No se encontraron datos.')
                return None
                
            return valores
        except HttpError as error:
            print(f"Error al leer datos: {error}")
            return None

    def obtener_rurus(self, rango_rurus):
        """Convierte los datos de la hoja en objetos Ruru."""
        datos = self.leer_datos(rango_rurus)
        if not datos:
            return []

        rurus = []
        # Asumiendo que las columnas están en este orden:
        # Nombre | Opciones | Disponibilidad | Idioma | Grado
        for fila in datos[1:]:  # Saltamos la cabecera
            try:
                nombre = fila[0]
                opciones = [op.strip() for op in fila[1].split(',')]
                
                # Procesar disponibilidad - asumimos formato similar a Yakus
                disponibilidad_raw = []
                if len(fila) > 2:
                    # Si está en formato antiguo (texto con formato "Lunes 1400-1600")
                    if ',' in fila[2]:
                        disponibilidad = convertir_horarios(fila[2])
                    else:
                        # Formato nuevo con columnas por día
                        for i in range(7):  # Columnas de disponibilidad (Lun-Dom)
                            if i + 2 < len(fila) and fila[i + 2].strip():
                                dia = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][i]
                                periodos = fila[i + 2].strip().split(',')
                                for periodo in periodos:
                                    if periodo.strip() in ["Mañana", "Tarde", "Noche"]:
                                        disponibilidad_raw.append(f"{dia} {periodo.strip()}")
                
                    disponibilidad = convertir_horarios(','.join(disponibilidad_raw))
                else:
                    disponibilidad = {}
                
                idioma = fila[9] if len(fila) > 9 else "Español"
                grado = fila[10] if len(fila) > 10 else "1ero Secundaria"
                
                ruru = Ruru(nombre, opciones, disponibilidad, idioma, grado)
                rurus.append(ruru)
            except Exception as e:
                print(f"Error al procesar Ruru {fila[0]}: {e}")
                continue
                
        return rurus

    def obtener_yakus(self, rango_yakus):
        """Convierte los datos de la hoja en objetos Yaku."""
        datos = self.leer_datos(rango_yakus)
        if not datos:
            return []

        yakus = []
        # Las columnas en orden:
        # Nombre | DNI | Celular | Correo | Área | Opciones | N° Beneficiarios | 
        # Disponibilidad (Lun-Dom) | Nivel Quechua | Grados
        for fila in datos[1:]:  # Saltamos la cabecera
            try:
                if len(fila) < 10:
                    print(f"Fila incompleta: {fila}")
                    continue
                
                nombre = fila[0]
                dni = fila[1]
                celular = fila[2]
                correo = fila[3]
                area = fila[4]
                opciones = [op.strip() for op in fila[5].split(',')]
                num_beneficiarios = int(fila[6])
                
                # Procesar disponibilidad
                disponibilidad_raw = []
                for i in range(7):  # Columnas de disponibilidad (Lun-Dom)
                    if i + 7 < len(fila) and fila[i + 7].strip():
                        dia = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][i]
                        periodos = fila[i + 7].strip().split(',')
                        for periodo in periodos:
                            if periodo.strip() in ["Mañana", "Tarde", "Noche"]:
                                disponibilidad_raw.append(f"{dia} {periodo.strip()}")
                
                disponibilidad = convertir_horarios(','.join(disponibilidad_raw))
                
                nivel_quechua = fila[14] if len(fila) > 14 else "No lo hablo"
                
                # Procesar grados
                grados_raw = fila[15] if len(fila) > 15 else ""
                grados = [g.strip() for g in grados_raw.split(',')] if grados_raw else []
                
                yaku = Yaku(
                    nombre, 
                    dni, 
                    celular, 
                    correo, 
                    area, 
                    opciones, 
                    num_beneficiarios, 
                    disponibilidad, 
                    nivel_quechua, 
                    grados
                )
                yakus.append(yaku)
            except Exception as e:
                print(f"Error al procesar Yaku {fila[0]}: {e}")
                continue
                
        return yakus

# Modificar la parte final del script para usar los datos de Google Sheets
if __name__ == "__main__":
    # Configuración de Google Sheets
    CREDENTIALS_PATH = 'ruta/a/tu/archivo/credentials.json'
    SPREADSHEET_ID = 'tu_spreadsheet_id'
    
    # Rangos de las hojas (ajusta según tu estructura)
    RANGO_RURUS = 'Rurus!A2:E50'  # A2:E50 asume que tienes hasta 50 filas de datos
    RANGO_YAKUS = 'Yakus!A2:E50'
    
    try:
        # Inicializar el lector de Google Sheets
        sheet_reader = GoogleSheetReader(CREDENTIALS_PATH, SPREADSHEET_ID)
        
        # Obtener datos de la hoja
        rurus_lista = sheet_reader.obtener_rurus(RANGO_RURUS)
        yakus_lista = sheet_reader.obtener_yakus(RANGO_YAKUS)
        
        # Usar los datos obtenidos
        matchmaker = MatchMaker()
        report_generator = ReportGenerator(matchmaker)
        
        mejor_asignacion, matches_secundarios, max_horas = matchmaker.encontrar_match(rurus_lista, yakus_lista)
        report_generator.generar_reporte(rurus_lista, yakus_lista, mejor_asignacion)
        
        print("Se ha generado el archivo 'reporte_matches.txt' con los resultados")
        
    except Exception as e:
        print(f"Error en la ejecución: {e}")
