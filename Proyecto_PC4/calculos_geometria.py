import numpy as np

def propiedades_rectangulo(z_min, y_min, base, altura):
    """Calcula las propiedades de un rectángulo respetando Z+ izquierda, Y+ arriba."""
    area = base * altura
    return {
        'area': area,
        'Cz': z_min + base / 2, # Centroide en Z
        'Cy': y_min + altura / 2, # Centroide en Y
        'Izc': (base * altura**3) / 12, # Inercia respecto a Z local
        'Iyc': (altura * base**3) / 12, # Inercia respecto a Y local
        'Izyc': 0.0
    }

def propiedades_circulo_analitico(v1_z, v1_y, r):
    """Calcula las propiedades analíticas puras de un círculo apoyado en (v1_z, v1_y)."""
    cz = v1_z + r
    cy = v1_y + r
    area = np.pi * (r**2)
    Iyc = (np.pi * (r**4)) / 4.0
    Izc = (np.pi * (r**4)) / 4.0
    return {
        'area': area,
        'Cz': cz,
        'Cy': cy,
        'Iyc': Iyc,
        'Izc': Izc,
        'Izyc': 0.0,
        'Iy': Iyc + area * (cz**2),
        'Iz': Izc + area * (cy**2),
        'Izy': area * cz * cy
    }

def propiedades_elipse_analitica(v1_z, v1_y, sz, sy):
    """Calcula las propiedades analíticas puras de una elipse apoyada en (v1_z, v1_y)."""
    cz = v1_z + sz
    cy = v1_y + sy
    area = np.pi * sz * sy
    Iyc = (np.pi * sy * (sz**3)) / 4.0
    Izc = (np.pi * sz * (sy**3)) / 4.0
    return {
        'area': area,
        'Cz': cz,
        'Cy': cy,
        'Iyc': Iyc,
        'Izc': Izc,
        'Izyc': 0.0,
        'Iy': Iyc + area * (cz**2),
        'Iz': Izc + area * (cy**2),
        'Izy': area * cz * cy
    }

def combinar_rectangulos(rectangulos):
    """Combina rectángulos usando el Teorema de Ejes Paralelos (Steiner)."""
    area_total = sum(r['area'] for r in rectangulos)
    Cz_total = sum(r['area'] * r['Cz'] for r in rectangulos) / area_total
    Cy_total = sum(r['area'] * r['Cy'] for r in rectangulos) / area_total

    Izc_total = sum(r['Izc'] + r['area'] * (r['Cy'] - Cy_total)**2 for r in rectangulos)
    Iyc_total = sum(r['Iyc'] + r['area'] * (r['Cz'] - Cz_total)**2 for r in rectangulos)
    
    # En flexión asimétrica el producto de inercia es vital
    Izyc_total = sum(r['Izyc'] + r['area'] * (r['Cz'] - Cz_total) * (r['Cy'] - Cy_total) for r in rectangulos)

    return {
        'area': area_total, 'Cz': Cz_total, 'Cy': Cy_total,
        'Izc': Izc_total, 'Iyc': Iyc_total, 'Izyc': Izyc_total,
        'Iz': Izc_total + area_total * Cy_total**2,
        'Iy': Iyc_total + area_total * Cz_total**2,
        'Izy': Izyc_total + area_total * Cz_total * Cy_total
    }

def calcular_propiedades_geometricas(tipo, *args):
    """Función maestra unificada que calcula las propiedades y genera los vértices locales."""
    res = {}
    nombre = tipo
    v_glob = None

    if tipo == 'rectangulo':
        v1_z, v1_y, base, altura = args
        nombre = "Rectángulo"
        
        # 1. Propiedades analíticas directas y exactas
        res = propiedades_rectangulo(v1_z, v1_y, base, altura)
        res['Iz'] = res['Izc'] + res['area'] * res['Cy']**2
        res['Iy'] = res['Iyc'] + res['area'] * res['Cz']**2
        res['Izy'] = res['Izyc'] + res['area'] * res['Cz'] * res['Cy']

        # 2. Coordenadas respetando Z+ Izquierda, Y+ Arriba
        v_glob = np.array([
            [v1_z, v1_y], 
            [v1_z + base, v1_y],
            [v1_z + base, v1_y + altura], 
            [v1_z, v1_y + altura]
        ], dtype=float)

    elif tipo == 'L':
        v1_z, v1_y, b_ala, a_ala, b_patin, a_patin = args
        nombre = "Perfil L"
        z_patin = v1_z + b_ala - b_patin
        y_patin = v1_y + a_ala
        r1 = propiedades_rectangulo(v1_z, v1_y, b_ala, a_ala)
        r2 = propiedades_rectangulo(z_patin, y_patin, b_patin, a_patin)
        res = combinar_rectangulos([r1, r2])
        v_glob = np.array([
            [v1_z, v1_y], [v1_z+b_ala, v1_y], [v1_z+b_ala, v1_y+a_ala],
            [v1_z+b_ala, y_patin+a_patin], [z_patin, y_patin+a_patin],
            [z_patin, v1_y+a_ala], [v1_z, v1_y+a_ala]
        ], dtype=float)

    elif tipo == 'Z':
        v1_z, v1_y, b_sup, a_sup, b_alma, a_alma, b_inf, a_inf = args
        nombre = "Perfil Z"
        
        # Ala superior (A la izquierda del alma)
        z_sup = v1_z
        y_sup = v1_y + a_inf + a_alma
        
        # Alma vertical
        z_alma = v1_z + b_sup - b_alma
        y_alma = v1_y + a_inf
        
        # Ala inferior (A la derecha del alma)
        z_inf = z_alma
        y_inf = v1_y
        
        r1 = propiedades_rectangulo(z_sup, y_sup, b_sup, a_sup)    # Ala superior
        r2 = propiedades_rectangulo(z_alma, y_alma, b_alma, a_alma) # Alma
        r3 = propiedades_rectangulo(z_inf, y_inf, b_inf, a_inf)    # Ala inferior
        
        res = combinar_rectangulos([r1, r2, r3])
        
        v_glob = np.array([
            [z_sup, y_sup],                             # 1. Esquina inferior izquierda - ala sup
            [z_sup, y_sup + a_sup],                     # 2. Esquina superior izquierda - ala sup
            [z_sup + b_sup, y_sup + a_sup],             # 3. Esquina superior derecha - ala sup
            [z_sup + b_sup, y_sup],                     # 4. Esquina inferior derecha - ala sup (unión alma)
            [z_alma + b_alma, y_alma],                  # 5. Cara derecha del alma (bajada)
            [z_inf + b_inf, y_inf + a_inf],             # 6. Esquina superior derecha - ala inf
            [z_inf + b_inf, y_inf],                     # 7. Esquina inferior derecha - ala inf
            [z_inf, y_inf],                             # 8. Esquina inferior izquierda - ala inf
            [z_inf, y_inf + a_inf],                     # 9. Esquina superior izquierda - ala inf
            [z_alma, y_alma],                           # 10. Cara izquierda del alma (subida)
            [z_alma, y_sup],                            # 11. Unión izquierda alma con ala sup
            [z_sup, y_sup]                              # 12. Cierre en el punto inicial
        ], dtype=float)

    elif tipo == 'T':
        v1_z, v1_y, b_ala, a_ala, b_alma, a_alma = args
        nombre = "Perfil T"
        
        # Ala superior 
        z_ala = v1_z
        y_ala = v1_y + a_alma  
        
        # Alma vertical
        z_alma = v1_z + (b_ala / 2.0) - (b_alma / 2.0)
        y_alma = v1_y
        
        r1 = propiedades_rectangulo(z_ala, y_ala, b_ala, a_ala)   # Ala superior
        r2 = propiedades_rectangulo(z_alma, y_alma, b_alma, a_alma) # Alma vertical
        
        res = combinar_rectangulos([r1, r2])
        
        v_glob = np.array([
            [z_ala, y_ala],                             # 1. Esquina inferior izq - ala sup
            [z_ala, y_ala + a_ala],                     # 2. Esquina superior izq - ala sup
            [z_ala + b_ala, y_ala + a_ala],             # 3. Esquina superior der - ala sup
            [z_ala + b_ala, y_ala],                     # 4. Esquina inferior der - ala sup
            [z_alma + b_alma, y_ala],                   # 5. Encuentro ala-alma (lado derecho)
            [z_alma + b_alma, y_alma],                  # 6. Esquina inferior der - alma (base)
            [z_alma, y_alma],                           # 7. Esquina inferior izq - alma (base)
            [z_alma, y_ala]                             # 8. Encuentro alma-ala (lado izquierdo)
        ], dtype=float)

    elif tipo == 'U':
        v1_z, v1_y, b_alma, a_alma, b_patin, a_patin = args
        nombre = "Perfil U"
        
        z_alma = v1_z
        y_alma = v1_y
        
        z_patin_izq = v1_z
        y_patin_izq = v1_y
        
        z_patin_der = v1_z + b_alma - b_patin
        y_patin_der = v1_y
        
        r1 = propiedades_rectangulo(z_patin_izq, y_patin_izq, b_patin, a_patin) # Patín izquierdo
        r2 = propiedades_rectangulo(z_alma + b_patin, y_alma, b_alma - 2*b_patin, a_alma) # Alma central neta
        r3 = propiedades_rectangulo(z_patin_der, y_patin_der, b_patin, a_patin) # Patín derecho
        
        res = combinar_rectangulos([r1, r2, r3])
        
        v_glob = np.array([
            [v1_z, v1_y],                                   # 1. Esquina inferior izquierda exterior
            [v1_z + b_alma, v1_y],                          # 2. Esquina inferior derecha exterior
            [v1_z + b_alma, v1_y + a_patin],                # 3. Esquina superior derecha del patín der
            [v1_z + b_alma - b_patin, v1_y + a_patin],      # 4. Esquina superior izquierda del patín der
            [v1_z + b_alma - b_patin, v1_y + a_alma],       # 5. Encuentro interior derecho (piso)
            [v1_z + b_patin, v1_y + a_alma],                # 6. Encuentro interior izquierdo (piso)
            [v1_z + b_patin, v1_y + a_patin],                # 7. Esquina superior derecha del patín izq
            [v1_z, v1_y + a_patin]                           # 8. Esquina superior izquierda del patín izq
        ], dtype=float)

    elif tipo == 'H':
        v1_z, v1_y, b_sup, a_sup, b_alma, a_alma, b_inf, a_inf = args
        nombre = "Perfil H"
        
        z_inf = v1_z
        y_inf = v1_y
        
        z_alma = v1_z + (b_inf / 2.0) - (b_alma / 2.0)
        y_alma = v1_y + a_inf
        
        z_sup = v1_z + (b_inf / 2.0) - (b_sup / 2.0)
        y_sup = y_alma + a_alma
        
        r1 = propiedades_rectangulo(z_inf, y_inf, b_inf, a_inf)    # Ala inferior
        r2 = propiedades_rectangulo(z_alma, y_alma, b_alma, a_alma) # Alma vertical
        r3 = propiedades_rectangulo(z_sup, y_sup, b_sup, a_sup)    # Ala superior
        
        res = combinar_rectangulos([r1, r2, r3])
        
        v_glob = np.array([
            [z_inf, y_inf],                             # 1. Esquina inferior izq - ala inf
            [z_inf + b_inf, y_inf],                     # 2. Esquina inferior der - ala inf
            [z_inf + b_inf, y_inf + a_inf],             # 3. Esquina superior der - ala inf
            [z_alma + b_alma, y_inf + a_inf],           # 4. Encuentro ala inf con cara der del alma
            [z_alma + b_alma, y_sup],                   # 5. Encuentro ala sup con cara der del alma
            [z_sup + b_sup, y_sup],                     # 6. Esquina inferior der - ala sup
            [z_sup + b_sup, y_sup + a_sup],             # 7. Esquina superior der - ala sup
            [z_sup, y_sup + a_sup],                     # 8. Esquina superior izq - ala sup
            [z_sup, y_sup],                             # 9. Esquina inferior izq - ala sup
            [z_alma, y_sup],                            # 10. Encuentro ala sup con cara izq del alma
            [z_alma, y_alma],                           # 11. Encuentro ala inf con cara izq del alma
            [z_inf, y_inf + a_inf]                      # 12. Esquina superior izq - ala inf
        ], dtype=float)

    elif tipo == 'circulo':
        v1_z, v1_y, r = args
        nombre = "Perfil Círculo"
        
        res = propiedades_circulo_analitico(v1_z, v1_y, r)
        
        theta = np.linspace(0, 2*np.pi, 100)
        v_glob = np.column_stack([res['Cz'] + r * np.cos(theta), res['Cy'] + r * np.sin(theta)])

    elif tipo == 'elipse':
        v1_z, v1_y, sz, sy = args
        nombre = "Perfil Elipse"
        
        res = propiedades_elipse_analitica(v1_z, v1_y, sz, sy)
        
        theta = np.linspace(0, 2*np.pi, 100)
        v_glob = np.column_stack([res['Cz'] + sz * np.cos(theta), res['Cy'] + sy * np.sin(theta)])

    # Estandarizamos las llaves (keys) para que coincidan exactamente con la Opción C
    diccionario_estandarizado = {
        # Para la Sección 2 (Mayúsculas)
        "Area": float(res['area']),
        "Zc": float(res['Cz']),
        "Yc": float(res['Cy']),
        "Iz": float(res.get('Izc', res.get('Iz'))),   
        "Iy": float(res.get('Iyc', res.get('Iy'))),   
        "Iyz": float(res.get('Izyc', res.get('Izy', 0.0))), 
        
        # Para tus ventanas de ingreso de perfiles A y B (Compatibilidad)
        "area": float(res['area']),
        "Cz": float(res['Cz']),
        "Cy": float(res['Cy']),
        "Izc": float(res.get('Izc', res.get('Iz'))),
        "Iyc": float(res.get('Iyc', res.get('Iy'))),
        "Izyc": float(res.get('Izyc', res.get('Izy', 0.0))),
        "nombre": nombre,
        
        # Vértices
        "vertices_globales": v_glob.tolist() if isinstance(v_glob, np.ndarray) else v_glob,
        "vertices_locales": (v_glob - np.array([res['Cz'], res['Cy']])).tolist() if isinstance(v_glob, np.ndarray) else []
    }
    
    return diccionario_estandarizado

#Para opcion B de bloques compuestos

def verificar_interseccion(nuevo_bloque, lista_bloques):
    """
    Devuelve True si el nuevo_bloque se cruza (se solapa internamente) 
    con alguno de los bloques ya existentes. Permite que se rocen los bordes.
    Formatos: nuevo_bloque = [b, h, z_c, y_c]
    """
    b_n, h_n, z_cn, y_cn = nuevo_bloque
    zn_min, zn_max = z_cn - b_n/2, z_cn + b_n/2
    yn_min, yn_max = y_cn - h_n/2, y_cn + h_n/2

    for bloque in lista_bloques:
        b, h, z_c, y_c = bloque
        z_min, z_max = z_c - b/2, z_c + b/2
        y_min, y_max = y_c - h/2, y_c + h/2

        # Condición de solapamiento en ambos ejes (intersección de áreas)
        if (zn_min < z_max and zn_max > z_min) and (yn_min < y_max and yn_max > y_min):
            return True # Hay intersección inválida
            
    return False


def verificar_conectividad(nuevo_bloque, lista_bloques):
    """
    Devuelve True si el nuevo_bloque está en contacto (al menos roza un borde)
    con alguno de los bloques existentes. Si la lista está vacía, devuelve True.
    """
    if not lista_bloques:
        return True # El primer bloque siempre es válido

    b_n, h_n, z_cn, y_cn = nuevo_bloque
    zn_min, zn_max = z_cn - b_n/2, z_cn + b_n/2
    yn_min, yn_max = y_cn - h_n/2, y_cn + h_n/2

    for bloque in lista_bloques:
        b, h, z_c, y_c = bloque
        z_min, z_max = z_c - b/2, z_c + b/2
        y_min, y_max = y_c - h/2, y_c + h/2

        # Para que se toquen, deben solaparse o coincidir en las proyecciones 
        # y que sus bordes estén exactamente alineados o cruzados en las puntas.
        # Una forma matemática limpia es ver si NO están completamente separados:
        # Tolerancia pequeña para errores de punto flotante en Python (1e-5)
        tol = 1e-5
        
        # Revisar si se intersectan extendiendo los bordes por un pelito infinitesimal
        if (zn_min <= z_max + tol and zn_max >= z_min - tol) and \
           (yn_min <= y_max + tol and yn_max >= y_min - tol):
            return True # Al menos toca a un bloque existente
            
    return False

def calcular_perfil_compuesto(lista_bloques):
    """
    Convierte la lista de bloques de la Opción B al formato del motor del grupo,
    aplica combinar_rectangulos y calcula los vértices locales centroidales.
    """
    if not lista_bloques:
        return {
            'area': 0, 'Cz': 0, 'Cy': 0,
            'Izc': 0, 'Iyc': 0, 'Izyc': 0,
            'Iz': 0, 'Iy': 0, 'Izy': 0,
            'vertices_locales': []
        }

    # 1. Convertir cada bloque [b, h, z_c, y_c] al formato que lee propiedades_rectangulo
    rectangulos_formateados = []
    for bloque in lista_bloques:
        b, h, z_c, y_c = bloque
        # Como z_c = z_min + b/2 -> z_min = z_c - b/2
        z_min = z_c - b / 2
        y_min = y_c - h / 2
        
        # Obtenemos el diccionario con área e inercias locales de este bloque
        prop_r = propiedades_rectangulo(z_min, y_min, b, h)
        rectangulos_formateados.append(prop_r)

    # 2. Utilizar la función de Juan para acoplar el Teorema de Steiner masivo
    res_global = combinar_rectangulos(rectangulos_formateados)

    # Coordenadas del centroide global calculado por combinar_rectangulos
    Cz_glob = res_global['Cz']
    Cy_glob = res_global['Cy']

    # 3. Extraer todos los vértices únicos de los bloques respecto al CENTROIDE GLOBAL
    vertices_locales = []
    for bloque in lista_bloques:
        b, h, z_c, y_c = bloque
        
        # Las 4 esquinas de este rectángulo en coordenadas globales absolutas
        esquinas_globales = [
            [z_c - b/2, y_c - h/2],  # Inferior Izquierda
            [z_c + b/2, y_c - h/2],  # Inferior Derecha
            [z_c + b/2, y_c + h/2],  # Superior Derecha
            [z_c - b/2, y_c + h/2]   # Superior Izquierda
        ]
        
        # Trasladamos cada esquina restando el centroide global
        for pt in esquinas_globales:
            z_local = pt[0] - Cz_glob
            y_local = pt[1] - Cy_glob
            
            # Redondeamos a 4 decimales para fusionar puntos compartidos sin duplicados
            vertice_redondo = [round(z_local, 4), round(y_local, 4)]
            if vertice_redondo not in vertices_locales:
                vertices_locales.append(vertice_redondo)

    # Añadimos los vértices locales al diccionario de salida para la Sección 2
    res_global['vertices_locales'] = vertices_locales
    return res_global

# Para la opcion C de poligono libre

def poligono_gauss(vertices):
    """
    [Código de Lenin] Calcula propiedades geométricas de un polígono simple 
    cualquiera mediante las fórmulas de Green reducidas a sumas sobre los lados.
    Entrada: vertices = [(z1,y1), (z2,y2), ..., (zn,yn)]
    """
    if len(vertices) < 3:
        return None

    n = len(vertices)
    A = Sz = Sy = 0.0
    Iy = Iz = Iyz = 0.0

    for i in range(n):
        z1, y1 = vertices[i]
        z2, y2 = vertices[(i + 1) % n]

        C = z1*y2 - z2*y1          # factor de cada lado

        A   += C
        Sz  += (z1 + z2) * C
        Sy  += (y1 + y2) * C
        Iy  += (z1**2 + z1*z2 + z2**2) * C
        Iz  += (y1**2 + y1*y2 + y2**2) * C
        Iyz += (2*z1*y1 + z1*y2 + z2*y1 + 2*z2*y2) * C

    A  /= 2
    Zc  = Sz / (6 * A)
    Yc  = Sy / (6 * A)
    Iy  /= 12
    Iz  /= 12
    Iyz /= 24

    # Steiner: pasar al centroide
    Iy_c  = Iy  - A * Zc**2
    Iz_c  = Iz  - A * Yc**2
    Iyz_c = Iyz - A * Zc * Yc

    # Convertimos los vértices locales a listas simples de punto flotante para homogeneizar
    vertices_locales = [[float(z - Zc), float(y - Yc)] for z, y in vertices]

    return {
        "A": A,
        "Zc": Zc,
        "Yc": Yc,
        "Iy": Iy_c,
        "Iz": Iz_c,
        "Iyz": Iyz_c,
        "vertices_locales": vertices_locales,
    }