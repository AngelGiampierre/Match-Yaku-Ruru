from itertools import product

# Siguientes pasos:
# - Uniformizar formularios de inscripción de yakus y rurus
# - Conectar formularios con el algoritmo
class Ruru:
    def __init__(self, nombre, area, opciones, disponibilidad, idioma, grado):
        self.nombre = nombre
        self.area = area
        self.opciones = opciones  # Lista de opciones en orden de preferencia
        self.disponibilidad = disponibilidad  # Diccionario con horarios por día
        self.idioma = idioma
        self.grado = grado  # Grado escolar del Ruru

class Yaku:
    def __init__(self, nombre, area, cursos, disponibilidad, idioma, grados, preferencias):
        self.nombre = nombre
        self.area = area
        self.cursos = cursos  # Lista de cursos que enseña
        self.disponibilidad = disponibilidad  # Diccionario con horarios por día
        self.idioma = idioma
        self.grados = grados  # Lista de grados que puede enseñar
        self.preferencias = preferencias  # Lista de cursos en orden de preferencia

def encontrar_match(rurus, yakus):
    mejor_asignacion = []
    max_horas = 0

    def es_idioma_compatible(idioma_ruru, idioma_yaku):
        return idioma_ruru == idioma_yaku or (idioma_ruru == "Español y Quechua" and idioma_yaku == "Solo Español")

    def calcular_horas_asignadas(interseccion_horarios):
        horas_totales = 0
        for horas_por_dia in interseccion_horarios.values():
            for inicio, fin in horas_por_dia:
                horas_totales += fin - inicio
        return horas_totales

    def backtrack(asignaciones, rurus_restantes):
        nonlocal mejor_asignacion, max_horas

        if not rurus_restantes:
            horas_totales = sum([calcular_horas_asignadas(horas) for _, _, _, horas, _ in asignaciones])
            if horas_totales > max_horas:
                max_horas = horas_totales
                mejor_asignacion = asignaciones[:]
            return

        ruru = rurus_restantes[0]
        for yaku in yakus:
            if yaku.area == ruru.area and es_idioma_compatible(ruru.idioma, yaku.idioma) and ruru.grado in yaku.grados:
                if ruru.area == "Bienestar":
                    interseccion_horarios = encontrar_interseccion(ruru.disponibilidad, yaku.disponibilidad, requerir_dias_distintos=False)
                    if interseccion_horarios:
                        horas_asignadas = calcular_horas_asignadas(interseccion_horarios)
                        if horas_asignadas >= 2:
                            asignaciones.append((ruru.nombre, yaku.nombre, "Bienestar", interseccion_horarios, 0))
                            backtrack(asignaciones, rurus_restantes[1:])
                            asignaciones.pop()
                else:
                    for r_opcion in ruru.opciones:
                        if r_opcion in yaku.cursos:
                            y_preferencia = yaku.preferencias.index(r_opcion) if r_opcion in yaku.preferencias else len(yaku.preferencias)
                            interseccion_horarios = encontrar_interseccion(ruru.disponibilidad, yaku.disponibilidad, requerir_dias_distintos=False)
                            if interseccion_horarios:
                                horas_asignadas = calcular_horas_asignadas(interseccion_horarios)
                                if horas_asignadas >= 2:  # Mínimo 2 horas a la semana
                                    asignaciones.append((ruru.nombre, yaku.nombre, r_opcion, interseccion_horarios, y_preferencia))
                                    backtrack(asignaciones, rurus_restantes[1:])
                                    asignaciones.pop()

    backtrack([], rurus)
    return sorted(mejor_asignacion, key=lambda x: x[4]), max_horas

def encontrar_interseccion(horarios_ruru, horarios_yaku, requerir_dias_distintos=False):
    interseccion = {}
    dias_distintos = 0

    for dia, horas_r in horarios_ruru.items():
        if dia in horarios_yaku:
            for rango_r in horas_r:
                for rango_y in horarios_yaku[dia]:
                    inicio = max(rango_r[0], rango_y[0])
                    fin = min(rango_r[1], rango_y[1])
                    if inicio < fin:
                        if dia not in interseccion:
                            interseccion[dia] = []
                        interseccion[dia].append((inicio, fin))
                        dias_distintos += 1

    if dias_distintos >= 1:
        return interseccion
    else:
        return {}

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
    horarios = {}
    for entrada in form_data.split(','):
        dia, horas = entrada.strip().split(' ')
        inicio, fin = map(lambda x: int(x.replace(':', '')), horas.split('-'))
        dia = dias_map[dia]
        if dia not in horarios:
            horarios[dia] = []
        horarios[dia].append((inicio, fin))
    return horarios

# Ejemplo de uso:
ruru1 = Ruru("Ruru1", "Bienestar", ["ajedrez", "dibujo", "música"], 
             convertir_horarios("Lunes 1300-1500, Jueves 1300-1800"), 
             "Español", "5to Primaria")

ruru2 = Ruru("Ruru2", "Arte", ["dibujo", "ajedrez", "música"], 
             convertir_horarios("Lunes 1300-1600, Miércoles 1300-1600"), 
             "Español y Quechua", "3ero Secundaria")

# Agregar más rurus
ruru3 = Ruru("Ruru3", "Ciencia", ["química", "física"], 
             convertir_horarios("Martes 1000-1200, Jueves 1400-1600"), 
             "Español", "4to Secundaria")

ruru4 = Ruru("Ruru4", "Deporte", ["fútbol", "baloncesto"], 
             convertir_horarios("Miércoles 1500-1700, Viernes 1000-1200"), 
             "Español", "1ero Secundaria")

ruru5 = Ruru("Ruru5", "Música", ["guitarra", "piano"], 
             convertir_horarios("Lunes 1400-1600, Sábado 1000-1200"), 
             "Español", "2do Secundaria")

ruru6 = Ruru("Ruru6", "Tecnología", ["programación", "robótica"], 
             convertir_horarios("Martes 1300-1500, Jueves 1300-1500"), 
             "Español", "3ero Secundaria")

ruru7 = Ruru("Ruru7", "Arte", ["pintura", "escultura"], 
             convertir_horarios("Lunes 1000-1200, Miércoles 1400-1600"), 
             "Español y Quechua", "5to Primaria")

ruru8 = Ruru("Ruru8", "Ciencia", ["biología", "química"], 
             convertir_horarios("Martes 1000-1200, Jueves 1000-1200"), 
             "Español", "6to Primaria")

ruru9 = Ruru("Ruru9", "Deporte", ["natación", "atletismo"], 
             convertir_horarios("Miércoles 1000-1200, Viernes 1400-1600"), 
             "Español", "4to Secundaria")

ruru10 = Ruru("Ruru10", "Música", ["violín", "batería"], 
              convertir_horarios("Lunes 1000-1200, Domingo 1400-1600"), 
              "Español", "3ero Secundaria")

yaku1 = Yaku("Yaku1", "Bienestar", ["dibujo"], 
             convertir_horarios("Lunes 1300-1500, Martes 1300-1500, Miércoles 1300-1500, Jueves 1300-1500, Viernes 1300-1500"), 
             "Español", ["5to Primaria", "6to Primaria"], 
             ["dibujo"])

yaku2 = Yaku("Yaku2", "Arte", ["música", "ajedrez"], 
             convertir_horarios("Lunes 1300-1400, Miércoles 1300-1400"), 
             "Español y Quechua", ["3ero Secundaria", "4to Secundaria"], 
             ["ajedrez", "música"])

# Agregar más yakus
yaku3 = Yaku("Yaku3", "Ciencia", ["química", "física"], 
             convertir_horarios("Martes 1000-1200, Jueves 1400-1600"), 
             "Español", ["4to Secundaria", "5to Secundaria"], 
             ["química", "física"])

yaku4 = Yaku("Yaku4", "Deporte", ["fútbol", "baloncesto"], 
             convertir_horarios("Miércoles 1500-1700, Viernes 1000-1200"), 
             "Español", ["1ero Secundaria", "2do Secundaria"], 
             ["fútbol", "baloncesto"])

yaku5 = Yaku("Yaku5", "Música", ["guitarra", "piano"], 
             convertir_horarios("Lunes 1400-1600, Sábado 1000-1200"), 
             "Español", ["2do Secundaria", "3ero Secundaria"], 
             ["guitarra", "piano"])

yaku6 = Yaku("Yaku6", "Tecnología", ["programación", "robótica"], 
             convertir_horarios("Martes 1300-1500, Jueves 1300-1500"), 
             "Español", ["3ero Secundaria", "4to Secundaria"], 
             ["programación", "robótica"])

yaku7 = Yaku("Yaku7", "Arte", ["pintura", "escultura"], 
             convertir_horarios("Lunes 1000-1200, Miércoles 1400-1600"), 
             "Español y Quechua", ["5to Primaria", "6to Primaria"], 
             ["pintura", "escultura"])

yaku8 = Yaku("Yaku8", "Ciencia", ["biología", "química"], 
             convertir_horarios("Martes 1000-1200, Jueves 1000-1200"), 
             "Español", ["6to Primaria", "1ero Secundaria"], 
             ["biología", "química"])

yaku9 = Yaku("Yaku9", "Deporte", ["natación", "atletismo"], 
             convertir_horarios("Miércoles 1000-1200, Viernes 1400-1600"), 
             "Español", ["4to Secundaria", "5to Secundaria"], 
             ["natación", "atletismo"])

yaku10 = Yaku("Yaku10", "Música", ["violín", "batería"], 
              convertir_horarios("Lunes 1000-1200, Domingo 1400-1600"), 
              "Español", ["3ero Secundaria", "4to Secundaria"], 
              ["violín", "batería"])

mejor_asignacion, max_horas = encontrar_match(
    [ruru1, ruru2, ruru3, ruru4, ruru5, ruru6, ruru7, ruru8, ruru9, ruru10],
    [yaku1, yaku2, yaku3, yaku4, yaku5, yaku6, yaku7, yaku8, yaku9, yaku10]
)

for match in mejor_asignacion:
    print(f"{match[0]} se empareja con {match[1]} en el curso/área de {match[2]} durante los horarios: {match[3]} con preferencia {match[4]}")
print(f"Máximo de horas asignadas: {max_horas}")
