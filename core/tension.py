def calcular_tension(Ag, Ae, Fy, Fu, metodo="LRFD"):
    """
    Calcula la resistencia nominal y admisible/diseno a tensión según AISC 360 (Capítulo D).
    """
    # 1. Fluencia en el área gruesa
    Pn_fluencia = Fy * Ag
    # 2. Ruptura en el área neta efectiva
    Pn_ruptura = Fu * Ae

    if metodo == "LRFD":
        # Factores LRFD: phi_t = 0.90 (fluencia), phi_r = 0.75 (ruptura)
        val_fluencia = 0.90 * Pn_fluencia
        val_ruptura = 0.75 * Pn_ruptura
        capacidad_diseno = min(val_fluencia, val_ruptura)
        etiqueta_cap = "Resistencia de Diseño (φPn)"
    else:
        # Factores ASD: Omega_t = 1.67 (fluencia), Omega_r = 2.00 (ruptura)
        val_fluencia = Pn_fluencia / 1.67
        val_ruptura = Pn_ruptura / 2.00
        capacidad_diseno = min(val_fluencia, val_ruptura)
        etiqueta_cap = "Resistencia Admisible (Pn/Ω)"

    if capacidad_diseno == val_fluencia:
        estado = "Controla el estado límite de Fluencia en el área gruesa."
    else:
        estado = "Controla el estado límite de Ruptura en el área neta efectiva."

    return {
        "Pn_fluencia": round(Pn_fluencia, 2),
        "Pn_ruptura": round(Pn_ruptura, 2),
        "capacidad_final": round(capacidad_diseno, 2),
        "etiqueta_cap": etiqueta_cap,
        "estado": estado
    }