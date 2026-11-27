def calcular_flexocompresion(Pr, Pc, Mrx, Mcx):
    """
    Calcula la interacción de flexocompresión según las ecuaciones del AISC 360 (Capítulo H).
    """
    if Pc <= 0 or Mcx <= 0:
        return {"error": "Las capacidades disponibles deben ser mayores a cero."}
        
    # Calcular las relaciones individuales
    relacion_axial = Pr / Pc
    relacion_momento = Mrx / Mcx
    
    # Evaluar según el límite de 0.2 de la especificación AISC H1-1
    if relacion_axial >= 0.2:
        indice = relacion_axial + (8.0 / 9.0) * relacion_momento
        ecuacion = "AISC Ecuación H1-1a (Pr/Pc >= 0.2)"
    else:
        indice = (relacion_axial / 2.0) + relacion_momento
        ecuacion = "AISC Ecuación H1-1b (Pr/Pc < 0.2)"
        
    if indice <= 1.0:
        estado = f"Diseño Satisfactorio (Índice = {round(indice, 3)} <= 1.0)"
    else:
        estado = f"No cumple: Excede la capacidad (Índice = {round(indice, 3)} > 1.0)"

    return {
        "relacion_axial": round(relacion_axial, 3),
        "relacion_momento": round(relacion_momento, 3),
        "indice_interaccion": round(indice, 3),
        "ecuacion": ecuacion,
        "estado": estado
    }