import math

def calcular_flexion(Fy, Zx, Sx, Lb, Lp, Lr, Cb=1.0, metodo="LRFD"):
    """
    Calcula la resistencia a flexión según AISC 360 (Capítulo F) para LRFD y ASD.
    """
    Mp = Fy * Zx
    
    if Lb <= Lp:
        Mn = Mp
        estado = "Fluencia (Zona 1: Lb <= Lp). Sección totalmente compacta."
    elif Lp < Lb <= Lr:
        Mn = Cb * (Mp - (Mp - 0.7 * Fy * Sx) * ((Lb - Lp) / (Lr - Lp)))
        Mn = min(Mn, Mp)
        estado = "Pandeo Lateral-Torsional Inelástico (Zona 2)."
    else:
        Fcr = (Cb * math.pi**2 * 29000.0) / ((Lb / (Sx / Zx)) ** 2)
        Mn = min(Fcr * Sx, Mp)
        estado = "Pandeo Lateral-Torsional Elástico (Zona 3)."

    if metodo == "LRFD":
        # phi_b = 0.90
        capacidad = 0.90 * Mn
        etiqueta_cap = "Resistencia de Diseño (φMn)"
    else:
        # Omega_b = 1.67
        capacidad = Mn / 1.67
        etiqueta_cap = "Resistencia Admisible (Mn/Ω)"
    
    return {
        "Mp_nominal": round(Mp, 2),
        "Mn_nominal": round(Mn, 2),
        "capacidad_final": round(capacidad, 2),
        "etiqueta_cap": etiqueta_cap,
        "estado": estado
    }