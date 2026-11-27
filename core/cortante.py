import math

def calcular_cortante(d, tw, Fy, E=29000.0, metodo="LRFD"):
    """
    Calcula la resistencia al corte según AISC 360 (Capítulo G) para LRFD y ASD.
    """
    Aw = d * tw
    h_tw = d / tw
    limite_h_tw = 2.24 * math.sqrt(E / Fy)
    
    if h_tw <= limite_h_tw:
        Cv1 = 1.0
        estado = "Alma compacta al corte (Cv1 = 1.0)."
    else:
        Cv1 = (1.10 * math.sqrt(E / Fy)) / h_tw
        estado = "Alma esbelta al corte (se requiere reducción)."
        
    Vn = 0.6 * Fy * Aw * Cv1
    
    if metodo == "LRFD":
        # phi_v = 1.00 para perfiles laminados típicos
        capacidad = 1.00 * Vn
        etiqueta_cap = "Resistencia de Diseño (φVn)"
    else:
        # Omega_v = 1.50 para perfiles laminados típicos
        capacidad = Vn / 1.50
        etiqueta_cap = "Resistencia Admisible (Vn/Ω)"
    
    return {
        "Aw": round(Aw, 2),
        "h_tw": round(h_tw, 2),
        "limite": round(limite_h_tw, 2),
        "Cv1": round(Cv1, 2),
        "Vn_nominal": round(Vn, 2),
        "capacidad_final": round(capacidad, 2),
        "etiqueta_cap": etiqueta_cap,
        "estado": estado
    }