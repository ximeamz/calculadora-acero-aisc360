from fpdf import FPDF
import tempfile
import os

def limpiar_texto(texto):
    """Reemplaza caracteres especiales y asegura que no queden símbolos incompatibles con Helvetica."""
    if not isinstance(texto, str):
        texto = str(texto)
    
    # Reemplazos específicos comunes
    reemplazos = {
        'φ': 'phi',
        'ϕ': 'phi',
        '≤': '<=',
        '≥': '>=',
        '•': '-',
        '°': ' deg'
    }
    for char, replacement in reemplazos.items():
        texto = texto.replace(char, replacement)
    
    # Filtro definitivo: convierte cualquier carácter fuera del rango estándar Latin-1 en '?'
    # Esto evita el 100% de las excepciones FPDFUnicodeEncodingException
    texto_seguro = "".join(c if ord(c) < 256 else '?' for c in texto)
    return texto_seguro

def generar_pdf_analisis(titulo, resultados):
    """
    Genera un reporte en PDF profesional basado en el diccionario de resultados.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    titulo_limpio = limpiar_texto(titulo)
    
    # Encabezado corporativo
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(43, 92, 143) # Azul corporativo
    pdf.cell(0, 10, limpiar_texto("Calculadora de Diseño Estructural - AISC 360"), 0, 1, "L")
    
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, limpiar_texto(f"Módulo: {titulo_limpio}"), 0, 1, "L")
    pdf.ln(5)
    
    # Línea divisoria
    pdf.set_draw_color(43, 92, 143)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    
    # Tabla de resultados
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, limpiar_texto("Resumen de Parámetros y Resultados Evaluados:"), 0, 1, "L")
    pdf.ln(3)
    
    # Cabeceras de tabla
    pdf.set_fill_color(43, 92, 143)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(95, 8, limpiar_texto(" Parámetro / Variable"), 1, 0, "L", fill=True)
    pdf.cell(95, 8, limpiar_texto(" Resultado / Estado"), 1, 1, "L", fill=True)
    
    # Filas de la tabla
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    
    fill = False
    for clave, valor in resultados.items():
        if str(clave).lower() == "error":
            continue
        pdf.set_fill_color(240, 244, 248) if fill else pdf.set_fill_color(255, 255, 255)
        
        clave_limpia = limpiar_texto(str(clave).replace("_", " ").capitalize())
        valor_limpio = limpiar_texto(str(valor))
        
        pdf.cell(95, 7, f" {clave_limpia}", 1, 0, "L", fill=True)
        pdf.cell(95, 7, f" {valor_limpio}", 1, 1, "L", fill=True)
        fill = not fill
        
    pdf.ln(15)
    
    # Pie de página
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, limpiar_texto("Reporte generado automáticamente por Calculadora AISC 360."), 0, 1, "C")
    pdf.cell(0, 5, limpiar_texto("Este documento es una referencia de cálculo y debe ser validado por un ingeniero estructural."), 0, 1, "C")
    
    # Guardar en archivo temporal para retornar los bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp_name = tmp.name
        
    pdf.output(tmp_name)
    
    with open(tmp_name, "rb") as f:
        pdf_bytes = f.read()
        
    os.remove(tmp_name)
    return pdf_bytes