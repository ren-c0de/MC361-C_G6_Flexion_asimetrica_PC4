import numpy as np

def motor_flexion_y_mohr(P, A, Iy, Iz, Iyz, My_total, Mz_total, lista_vertices):
    """
    Motor matemático. Procesa flexión asimétrica + carga axial 
    y calcula todas las propiedades necesarias para los gráficos de Mohr y Esfuerzos.
    """
    # 1. Ángulo de los ejes principales (Círculo de Mohr)
    numerador = Iyz
    denominador = (Iz - Iy) / 2
    tetha_rad = np.arctan2(numerador, denominador) / 2
    tetha_sexagesimal = np.degrees(tetha_rad)

    # 2. Momentos de inercia principales
    R_mohr = np.sqrt(((Iz - Iy) / 2)**2 + Iyz**2)
    Iprom = (Iz + Iy) / 2
    Iu = Iprom + R_mohr  # Imax
    Iv = Iprom - R_mohr  # Imin

    # 3. Descomposición de momentos en ejes principales u-v
    Mu = -My_total * np.sin(tetha_rad) + Mz_total * np.cos(tetha_rad)
    Mv = My_total * np.cos(tetha_rad) + Mz_total * np.sin(tetha_rad)

    # 4. Ángulo del Eje Neutro (Betha) respecto al eje principal u
    betha_rad = np.arctan2(Mv * Iu, Mu * Iv)
    betha_sexagesimal = np.degrees(betha_rad)

    # 5. Componente axial uniforme (P/A)
    esfuerzo_axial = P / A if A > 0 else 0.0

    esfuerzos = []
    vertices_transformados = []

    for idx, (z, y) in enumerate(lista_vertices):
        # Rotación de coordenadas a ejes principales
        u = z * np.cos(tetha_rad) - y * np.sin(tetha_rad)
        v = z * np.sin(tetha_rad) + y * np.cos(tetha_rad)
        vertices_transformados.append([u, v])

        # Efecto Mu (Regla de la mano derecha automatizada)
        if v > 0:
            efecto_Mu = -abs(Mu * v / Iu) * np.sign(Mu) if Iu != 0 else 0
        else:
            efecto_Mu = abs(Mu * v / Iu) * np.sign(Mu) if Iu != 0 else 0

        # Efecto Mv
        if u > 0:
            efecto_Mv = abs(Mv * u / Iv) * np.sign(Mv) if Iv != 0 else 0
        else:
            efecto_Mv = -abs(Mv * u / Iv) * np.sign(Mv) if Iv != 0 else 0

        # Superposición total: Bending + Axial
        sigma = esfuerzo_axial + efecto_Mu + efecto_Mv
        esfuerzos.append(sigma)

    # Identificación de extremos
    sigma_max = max(esfuerzos)
    sigma_min = min(esfuerzos)
    idx_max = esfuerzos.index(sigma_max)
    idx_min = esfuerzos.index(sigma_min)

    # Empaquetamos los resultados ordenados para los gráficos de la UI
    resultados = {
        "Iprom": Iprom, "R_mohr": R_mohr, "Iz": Iz, "Iy": Iy, "Iyz": Iyz,
        "Imax": Iu, "Imin": Iv, "tetha": tetha_sexagesimal, "tetha_rad": tetha_rad,
        "betha": betha_sexagesimal, "betha_rad": betha_rad,
        "esfuerzos": esfuerzos, "sigma_max": sigma_max, "sigma_min": sigma_min,
        "v_max": lista_vertices[idx_max], "v_min": lista_vertices[idx_min]
    }
    return resultados