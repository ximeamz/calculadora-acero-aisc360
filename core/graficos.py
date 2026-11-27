import plotly.graph_objects as go
import numpy as np
import math

def generar_grafico_buckling(Fy, E, K_L_r_usuario, Fcr_usuario):
    """
    Genera un gráfico interactivo con Plotly para la curva de pandeo en compresión (AISC Capítulo E).
    """
    klr_vals = np.linspace(1, 200, 200)
    fcr_vals = []
    limite_esbeltez = 4.71 * math.sqrt(E / Fy)
    
    for klr in klr_vals:
        Fe = (math.pi**2 * E) / (klr**2)
        if klr <= limite_esbeltez:
            fcr = (0.658 ** (Fy / Fe)) * Fy
        else:
            fcr = 0.877 * Fe
        fcr_vals.append(fcr)
        
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=klr_vals, 
        y=fcr_vals,
        mode='lines',
        name='Curva AISC 360 (Fcr)',
        line=dict(color='#2b5c8f', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=[K_L_r_usuario], 
        y=[Fcr_usuario],
        mode='markers+text',
        name='Su Elemento',
        text=["Punto Evaluado"],
        textposition="top center",
        marker=dict(color='#e74c3c', size=14, symbol='star')
    ))
    
    fig.update_layout(
        title="Comportamiento a Compresión Axial (Capítulo E)",
        xaxis_title="Relación de Esbeltez (Kl/r)",
        yaxis_title="Esfuerzo Crítico Fcr (ksi)",
        template="plotly_white",
        height=450,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    return fig


def generar_grafico_flexocompresion(pr_pc, mr_mc):
    """
    Genera un gráfico interactivo con Plotly para la envolvente de interacción de Flexocompresión (AISC Capítulo H).
    """
    pr_vals = np.linspace(0, 1.0, 100)
    mr_vals = []
    
    for pr in pr_vals:
        if pr >= 0.2:
            mr = (9.0 / 8.0) * (1.0 - pr)
        else:
            mr = 2.0 * (1.0 - pr)
        mr_vals.append(max(0, mr))
        
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=mr_vals, 
        y=pr_vals,
        mode='lines',
        name='Límite AISC (Interacción = 1.0)',
        line=dict(color='#e74c3c', width=3, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=[mr_mc], 
        y=[pr_pc],
        mode='markers+text',
        name='Su Solicitud',
        text=["Punto Evaluado"],
        textposition="top right",
        marker=dict(color='#2b5c8f', size=14, symbol='diamond')
    ))
    
    fig.update_layout(
        title="Envolvente de Interacción Flexocompresión (Capítulo H)",
        xaxis_title="Relación de Momento (Mr / Mc)",
        yaxis_title="Relación Axial (Pr / Pc)",
        template="plotly_white",
        height=450,
        xaxis=dict(range=[0, 1.2]),
        yaxis=dict(range=[0, 1.2]),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    return fig