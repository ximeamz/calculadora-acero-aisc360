import math

def calcular_compresion(Ag, r, L, Fy, E=29000.0, K=1.0, metodo="LRFD"):
    """
    Calcula la resistencia a compresión según AISC 360 (Capítulo E) para LRFD y ASD.
    """
    slender_ratio = (K * L) / r
    Fe = (math.pi**2 * E) / (slender_ratio**2)
    limite_esbeltez = 4.71 * math.sqrt(E / Fy)
    
    if slender_ratio <= 200:
        if slender_ratio <= limite_esbeltez:
            Fcr = (0.658 ** (Fy / Fe)) * Fy
        else:
            Fcr = 0.877 * Fe
            
        Pn = Fcr * Ag
        
        if metodo == "LRFD":
            # phi_c = 0.90
            capacidad = 0.90 * Pn
            etiqueta_cap = "Resistencia de Diseño (φPn)"
        else:
            # Omega_c = 1.67
            capacidad = Pn / 1.67
            etiqueta_cap = "Resistencia Admisible (Pn/Ω)"

        return {
            "esbeltez": round(slender_ratio, 2),
            "limite": round(limite_esbeltez, 2),
            "Fcr": round(Fcr, 2),
            "Pn_nominal": round(Pn, 2),
            "capacidad_final": round(capacidad, 2),
            "etiqueta_cap": etiqueta_cap,
            "estado": "Aceptable (Esbeltez menor a 200)"
        }
    else:
        return {
            "esbeltez": round(slender_ratio, 2),
            "estado": "No cumple: La esbeltez supera el límite máximo normativo de 200."
        }