from itertools import product

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
                    interseccion_horarios = encontrar_interseccion(ruru.disponibilidad, yaku.disponibilidad, requerir_dias_distintos=True)
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
                            interseccion_horarios = encontrar_interseccion(ruru.disponibilidad, yaku.disponibilidad, requerir_dias_distintos=True)
                            if interseccion_horarios:
                                horas_asignadas = calcular_horas_asignadas(interseccion_horarios)
                                if horas_asignadas >= 2:  # Mínimo 2 horas distribuidas en 2 días
                                    asignaciones.append((ruru.nombre, yaku.nombre, r_opcion, interseccion_horarios, y_preferencia))
                                    backtrack(asignaciones, rurus_restantes[1:])
                                    asignaciones.pop()

    backtrack([], rurus)
    return sorted(mejor_asignacion, key=lambda x: x[4]), max_horas

def encontrar_interseccion(horarios_ruru, horarios_yaku, requerir_dias_distintos=True):
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

    if requerir_dias_distintos and dias_distintos >= 2:
        return interseccion
    elif not requerir_dias_distintos and dias_distintos >= 1:
        return interseccion
    else:
        return {}

# Ejemplo de uso:
ruru1 = Ruru("Ruru1", "Bienestar", ["ajedrez", "dibujo", "música"], 
             {"lunes": [(13, 18)], "jueves": [(13, 18)]}, 
             "Español", "5to Primaria")

ruru2 = Ruru("Ruru2", "Arte", ["dibujo", "ajedrez", "música"], 
             {"lunes": [(13, 16)], "miércoles": [(13, 16)]}, 
             "Español y Quechua", "3ero Secundaria")    

yaku1 = Yaku("Yaku1", "Bienestar", ["dibujo"], 
             {"lunes": [(13, 15), (16, 18)], "martes": [(13, 15)], 
              "miércoles": [(13, 15)], "jueves": [(13, 15)], 
              "viernes": [(13, 15)]}, 
             "Español", ["5to Primaria", "6to Primaria"], 
             ["dibujo"])

yaku2 = Yaku("Yaku2", "Arte", ["música", "ajedrez"], 
             {"lunes": [(13, 14), (16, 18)], "miércoles": [(13, 14)]}, 
             "Español y Quechua", ["3ero Secundaria", "4to Secundaria"], 
             ["ajedrez", "música"])

yaku3 = Yaku("Yaku3", "Bienestar", [], 
             {"lunes": [(13, 15), (16, 18)], "jueves": [(16, 18)]}, 
             "Español", ["1ero Secundaria", "2do Secundaria", "3ero Secundaria"], 
             [])

mejor_asignacion, max_horas = encontrar_match([ruru1, ruru2], [yaku1, yaku2, yaku3])

for match in mejor_asignacion:
    print(f"{match[0]} se empareja con {match[1]} en el curso/área de {match[2]} durante los horarios: {match[3]} con preferencia {match[4]}")
print(f"Máximo de horas asignadas: {max_horas}")
