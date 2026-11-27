import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.tension import calcular_tension
from core.compression import calcular_compresion
from core.flexion import calcular_flexion
from core.cortante import calcular_cortante
from core.flexocompresion import calcular_flexocompresion
from core.reporte_pdf import generar_pdf_analisis
from core.base_datos import cargar_perfiles_w
from core.graficos import generar_grafico_buckling, generar_grafico_flexocompresion

# Configuración inicial de la página
st.set_page_config(
    page_title="Proyecto Final - Diseño Estructural AISC 360",
    page_icon="🏗️",
    layout="wide"
)

# ==========================================
# ESTILOS VISUALES Y DISEÑO DE INTERFAZ (CSS)
# ==========================================
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
    }
    h1, h2, h3 {
        color: #1E3D59 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stButton>button {
        background-color: #2B5C8F;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1E3D59;
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    div.stInfo {
        background-color: #e8f1f5 !important;
        border-left: 6px solid #2B5C8F !important;
        color: #1E3D59 !important;
        border-radius: 4px;
    }
    .apunte-box {
        background-color: #ffffff;
        border: 1px solid #d6e0ea;
        border-left: 5px solid #e09f1f;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    div[data-testid="stMetricValue"] {
        color: #2B5C8F;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# Cargar base de datos comercial
df_perfiles = cargar_perfiles_w()
lista_nombres_perfiles = df_perfiles["perfil"].tolist() if not df_perfiles.empty else []

# ==========================================
# CONFIGURACIÓN GENERAL (SIDEBAR)
# ==========================================
st.sidebar.header("⚙️ Configuración General")

sistema_unidades = st.sidebar.selectbox(
    "Seleccione el Sistema de Unidades:",
    ["Imperial (in, kips, ksi)", "Métrico / SI (mm, MPa, kN)"]
)
es_metrico = "Métrico" in sistema_unidades

metodo_diseno = st.sidebar.selectbox(
    "Seleccione el Método de Diseño:",
    ["LRFD (Factores de Carga y Resistencia)", "ASD (Resistencia Admisible)"]
)
metodo_actual = "LRFD" if "LRFD" in metodo_diseno else "ASD"

st.sidebar.markdown("---")
st.sidebar.info(f"Método Activo: **{metodo_actual}**\n\nUnidades: **{'Métrico (SI)' if es_metrico else 'Imperial'}**")

# ==========================================
# FACTORES DE CONVERSIÓN Y UTILIDADES
# ==========================================
def conv_l(val): return val / 25.4 if es_metrico else val          # mm a in
def conv_a(val): return val / 6.4516 if es_metrico else val        # cm² a in²
def conv_s(val): return val / 16.387 if es_metrico else val        # cm³ a in³
def conv_f(val): return val / 6.89476 if es_metrico else val       # MPa a ksi
def conv_p(val): return val / 4.44822 if es_metrico else val       # kN a kips
def conv_m(val): return (val * 1000) / (4.44822 * 25.4) if es_metrico else val # kN·m a kips·in

def out_p(val_kips): return val_kips * 4.44822 if es_metrico else val_kips     # kips a kN
def out_m(val_kipin): return (val_kipin * 4.44822 * 25.4) / 1000 if es_metrico else val_kipin # kips·in a kN·m
def out_f(val_ksi): return val_ksi * 6.89476 if es_metrico else val_ksi        # ksi a MPa
def out_l(val_in): return val_in * 25.4 if es_metrico else val_in            # in a mm

def extraer_valor(res_item):
    val_str = str(res_item).split()[0]
    return float(val_str)

def dibujar_esquema_perfil_w(d, bf, tw, tf):
    """Genera un diagrama esquemático interactivo de la sección transversal en I (Perfil W)."""
    fig = go.Figure()
    h_2 = d / 2.0
    b_2 = bf / 2.0

    fig.add_shape(type="rect", x0=-b_2, y0=h_2 - tf, x1=b_2, y1=h_2,
                  line=dict(color="#1E3D59", width=2), fillcolor="rgba(43, 92, 143, 0.7)")
    fig.add_shape(type="rect", x0=-b_2, y0=-h_2, x1=b_2, y1=-h_2 + tf,
                  line=dict(color="#1E3D59", width=2), fillcolor="rgba(43, 92, 143, 0.7)")
    tw_2 = tw / 2.0
    fig.add_shape(type="rect", x0=-tw_2, y0=-h_2 + tf, x1=tw_2, y1=h_2 - tf,
                  line=dict(color="#1E3D59", width=2), fillcolor="rgba(70, 130, 180, 0.5)")

    # Ejes x y y como en apuntes de clase
    fig.add_shape(type="line", x0=-b_2*1.4, y0=0, x1=b_2*1.4, y1=0,
                  line=dict(color="#b85d19", width=1.5, dash="dashdot"))
    fig.add_shape(type="line", x0=0, y0=-h_2*1.2, x1=0, y1=h_2*1.2,
                  line=dict(color="#b85d19", width=1.5, dash="dashdot"))

    fig.add_annotation(x=0, y=h_2 + tf/2, text=f"bf = {round(bf, 2)}", showarrow=False, yshift=15, font=dict(color="#1E3D59", size=12))
    fig.add_annotation(x=b_2 + tw, y=0, text=f"d = {round(d, 2)}", showarrow=False, xshift=30, font=dict(color="#1E3D59", size=12))
    fig.add_annotation(x=b_2*1.35, y=0, text="x", showarrow=False, xshift=10, font=dict(color="#b85d19", size=12))
    fig.add_annotation(x=0, y=h_2*1.18, text="y", showarrow=False, yshift=10, font=dict(color="#b85d19", size=12))

    fig.update_layout(
        title=dict(text="<b>Esquema Geométrico y Ejes de la Sección (Perfil W)</b>", font=dict(color="#1E3D59")),
        xaxis=dict(range=[-b_2*1.8, b_2*1.8], showgrid=False, zeroline=False),
        yaxis=dict(range=[-h_2*1.3, h_2*1.3], showgrid=False, zeroline=False),
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# ==========================================
# NAVEGACIÓN PRINCIPAL POR PESTAÑAS (TABS)
# ==========================================
tab_presentacion, tab_calculadora = st.tabs(["📖 Presentación y Datos", "⚙️ Módulos de Cálculo AISC 360"])

with tab_presentacion:
    col_logo1, col_centro, col_logo2 = st.columns([1, 3, 1])
    with col_logo1:
        st.markdown("### 🏛️ **UdeG**")
        st.caption("Universidad de Guadalajara")
    with col_centro:
        st.markdown("<h3 style='text-align: center; color: #1E3D59;'>Centro Universitario de Arte, Arquitectura y Diseño (CUAAD)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #555;'>División de Proyectos / Departamento de Tecnología y Procesos</p>", unsafe_allow_html=True)
    with col_logo2:
        st.markdown("### 📐 **CUAAD**")
        st.caption("Arquitectura")

    st.markdown("---")

    st.title("Proyecto Final de Diseño Estructural")
    st.write("Una plataforma interactiva didáctica desarrollada para el análisis y diseño de miembros de acero bajo las especificaciones del **AISC 360**.")

    st.markdown("### Datos Generales del Proyecto")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.info("**Título del Proyecto Final:**\n\n Calculadora para Revisión y Diseño de Miembros de Acero")
        st.info("**Nombre del Alumno:**\n\n Ximena Amezcua Miranda")
        st.info("**Código de Estudiante:**\n\n 223987678")
    with col_d2:
        st.info("**Nombre de la Materia:**\n\n Diseño Estructural en Acero y Mampostería Confinada")
        st.info("**Nombre del Profesor:**\n\n Sergio Esteban Aldana Alonso")
        st.info("**Fecha de Presentación:**\n\n Noviembre 2026")

    st.markdown("---")
    st.subheader("1. Introducción")
    st.markdown("""
    En el diseño estructural contemporáneo, la revisión y dimensionamiento de elementos de acero bajo la norma **AISC 360** exige precisión normativa, agilidad en el manejo de catálogos comerciales y trazabilidad en los cálculos.

    Este proyecto presenta una aplicación interactiva desarrollada en **Python** con **Streamlit**. La herramienta busca unir el rigor de las especificaciones normativas con una interfaz didáctica y visual que facilite tanto el cálculo rápido como la comprensión del procedimiento matemático detrás de cada resultado.
    """)

    st.subheader("2. Desarrollo")
    st.markdown("""
    El sistema se organizó de manera modular y progresiva para cubrir los criterios fundamentales del diseño de miembros de acero:

    * **Arquitectura y módulos normativos (AISC 360):** Se implementaron rutinas de cálculo para **Tensión (Capítulo D)**, **Compresión (Capítulo E)**, **Flexión (Capítulo F)**, **Cortante (Capítulo G)** y **Flexocompresión (Capítulo H)**, permitiendo alternar entre los métodos **LRFD** y **ASD**, así como entre los sistemas de unidades **Imperial** y **Métrico / SI**.
    * **Base de datos y búsqueda ágil:** Se amplió el catálogo de perfiles a más de **65 perfiles comerciales W** con sus propiedades geométricas y mecánicas, incorporando un filtro de búsqueda para ubicar secciones de forma inmediata o ingresar propiedades manualmente.
    * **Visualización geométrica y didáctica:** Se integraron gráficos interactivos con **Plotly** (esquemas de la sección transversal con dimensiones como $d$, $b_f$, $t_w$ y $t_f$, curvas de pandeo y envolventes de interacción) junto con una **memoria de cálculo paso a paso** en formato LaTeX que detalla las ecuaciones y factores normativos aplicados en cada caso.
    * **Reportes en PDF:** Se estructuró una pestaña fija con los datos del proyecto, separada de los módulos de cálculo, y se añadió la exportación de reportes en **PDF** mediante **FPDF2**.
    """)

    st.subheader("3. Conclusiones")
    st.markdown("""
    La aplicación cumple con el objetivo de ofrecer una herramienta técnica y didáctica confiable para la revisión y el diseño preliminar de miembros de acero conforme al **AISC 360**. Al combinar cálculo automatizado, representación gráfica de secciones y comportamiento estructural, y el desglose explícito de las fórmulas, el proyecto reduce errores operativos y refuerza el criterio de diseño del estudiante. Como líneas de mejora futura, el sistema queda preparado para incorporar más geometrías estructurales (como perfiles HSS o ángulos), diseño de conexiones o verificaciones adicionales de esbeltez local y deflexiones.
    """)

# ==========================================
# PESTAÑA DE MÓDULOS DE CÁLCULO
# ==========================================
with tab_calculadora:
    tipo_miembro = st.selectbox(
        "Seleccione el tipo de solicitación a evaluar:",
        [
            "Tensión (Capítulo D)",
            "Compresión (Capítulo E)",
            "Flexión (Capítulo F)",
            "Cortante (Capítulo G)",
            "Flexocompresión (Capítulo H)"
        ],
        key="selector_modulo_principal"
    )

    st.markdown("---")

    def seleccionar_perfil_con_busqueda(key_sufijo=""):
        st.markdown(" **Búsqueda y Filtrado de Perfiles Comerciales W**")
        busqueda = st.text_input("Escribe para filtrar perfil (ej. W10, W14, W24):", "", key=f"search_{key_sufijo}")

        perfiles_filtrados = [p for p in lista_nombres_perfiles if busqueda.upper() in p.upper()]
        if not perfiles_filtrados:
            perfiles_filtrados = lista_nombres_perfiles

        perfil_sel = st.selectbox("Seleccione el perfil de la lista filtrada:", perfiles_filtrados, key=f"sel_{key_sufijo}")
        return perfil_sel

    # ==========================================
    # 0. MÓDULO DE TENSIÓN (Capítulo D) — Estilo Cuaderno de Clase
    # ==========================================
    if tipo_miembro == "Tensión (Capítulo D)":
        st.header(f"📌 Capítulo D: Revisión y Diseño a Tensión ({metodo_actual})")
        st.caption("Planteamiento editable: modifica los valores del problema para simular ejercicios de clase o propuestas propias.")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            carga_actuante = st.number_input(
                f"Carga actuante ({'kN' if es_metrico else 'kips'}):",
                value=294.2 if es_metrico else 66.1,
                min_value=0.1,
                key="tens_carga_act"
            )
            longitud_miembro = st.number_input(
                f"Longitud del miembro L ({'mm' if es_metrico else 'in'}):",
                value=2000.0 if es_metrico else 78.74,
                min_value=1.0,
                key="tens_long"
            )
        with col_p2:
            Fy_user = st.number_input(
                f"Esfuerzo de fluencia Fy ({'MPa' if es_metrico else 'ksi'}):",
                value=345.0 if es_metrico else 50.0,
                min_value=1.0,
                key="tens_fy"
            )
            Fu_user = st.number_input(
                f"Esfuerzo último Fu ({'MPa' if es_metrico else 'ksi'}):",
                value=450.0 if es_metrico else 65.0,
                min_value=1.0,
                key="tens_fu"
            )
        with col_p3:
            factor_ae = st.slider(
                "Relación Ae / Ag (área neta efectiva):",
                min_value=0.50,
                max_value=1.00,
                value=0.85,
                step=0.05,
                key="tens_ae_ratio"
            )
            propuesta_ag = st.number_input(
                f"Área propuesta para comprobación ({'cm²' if es_metrico else 'in²'}):",
                value=15.42 if es_metrico else 2.39,
                min_value=0.1,
                key="tens_ag_prop"
            )

        modo_entrada = st.radio(
            "Fuente de datos de la sección para revisión:",
            ["Seleccionar perfil comercial W", "Ingresar propiedades manualmente"],
            key="tens_modo"
        )

        d_val, bf_val, tw_val, tf_val, r_min_imp = 14.2, 8.0, 0.34, 0.61, 2.02
        if modo_entrada == "Seleccionar perfil comercial W" and lista_nombres_perfiles:
            perfil_sel = seleccionar_perfil_con_busqueda("tension")
            fila = df_perfiles[df_perfiles["perfil"] == perfil_sel].iloc[0]
            Ag_imp = float(fila["Ag"])
            r_min_imp = min(float(fila["rx"]), float(fila["ry"]))
            d_val, bf_val, tw_val, tf_val = float(fila["d"]), float(fila["bf"]), float(fila["tw"]), float(fila["tf"])
        else:
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                Ag_user = st.number_input(
                    f"Área gruesa Ag ({'cm²' if es_metrico else 'in²'}):",
                    value=77.4 if es_metrico else 12.0,
                    min_value=0.1,
                    key="tens_ag_man"
                )
            with c_m2:
                r_user = st.number_input(
                    f"Radio de giro crítico r ({'mm' if es_metrico else 'in'}):",
                    value=51.3 if es_metrico else 2.02,
                    min_value=0.01,
                    key="tens_r_man"
                )
            Ag_imp = conv_a(Ag_user)
            r_min_imp = conv_l(r_user)

        Ae_imp = Ag_imp * factor_ae
        st.plotly_chart(dibujar_esquema_perfil_w(d_val, bf_val, tw_val, tf_val), use_container_width=True)

        Fy_imp = conv_f(Fy_user)
        Fu_imp = conv_f(Fu_user)
        L_imp = conv_l(longitud_miembro)
        Pr_imp = conv_p(carga_actuante)

        if st.button("Calcular y Revisar en Tensión"):
            resultado = calcular_tension(Ag_imp, Ae_imp, Fy_imp, Fu_imp, metodo=metodo_actual)

            unidad_for = 'kN' if es_metrico else 'kips'
            unidad_est = 'MPa' if es_metrico else 'ksi'
            unidad_long = 'mm' if es_metrico else 'in'
            unidad_area = 'cm²' if es_metrico else 'in²'

            pn_fluencia_disp = out_p(extraer_valor(resultado["Pn_fluencia"]))
            cap_disp = out_p(extraer_valor(resultado["capacidad_final"]))
            radio_trabajo = carga_actuante / cap_disp if cap_disp > 0 else 0.0
            radio_pct = radio_trabajo * 100.0
            cumple_resistencia = cap_disp >= carga_actuante

            esbeltez_lr = L_imp / r_min_imp if r_min_imp > 0 else 0.0
            cumple_esbeltez = esbeltez_lr <= 300.0
            r_min_req_disp = out_l(L_imp / 300.0)

            factor_seg = 0.90 if metodo_actual == "LRFD" else 1.67
            if metodo_actual == "LRFD":
                ag_req_imp = (Pr_imp / (0.90 * Fy_imp)) if Fy_imp > 0 else 0.0
            else:
                ag_req_imp = ((Pr_imp * 1.67) / Fy_imp) if Fy_imp > 0 else 0.0
            ag_req_disp = ag_req_imp * (6.4516 if es_metrico else 1.0)
            ag_disp = Ag_imp * (6.4516 if es_metrico else 1.0)
            r_disp = out_l(r_min_imp)

            # Comprobación de propuesta ingresada
            ag_prop_imp = conv_a(propuesta_ag)
            res_prop = calcular_tension(ag_prop_imp, ag_prop_imp * factor_ae, Fy_imp, Fu_imp, metodo=metodo_actual)
            cap_prop_disp = out_p(extraer_valor(res_prop["capacidad_final"]))
            rt_prop = carga_actuante / cap_prop_disp if cap_prop_disp > 0 else 0.0
            cumple_prop = (propuesta_ag >= ag_req_disp) and (cap_prop_disp >= carga_actuante)

            st.subheader("Resultados del Análisis:")
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Resistencia Nominal Fluencia (Tn / Pn)", f"{round(pn_fluencia_disp, 2)} {unidad_for}")
            mcol2.metric(resultado["etiqueta_cap"], f"{round(cap_disp, 2)} {unidad_for}")
            mcol3.metric("Radio de Trabajo", f"{round(radio_trabajo, 2)} ({round(radio_pct, 1)}%)")

            st.info(
                f"**Evaluación:** {'Cumple por resistencia y esbeltez' if (cumple_resistencia and cumple_esbeltez) else 'No cumple — revisar sección'} "
                f"| Carga actuante = {round(carga_actuante, 2)} {unidad_for} vs Capacidad = {round(cap_disp, 2)} {unidad_for}"
            )

            st.markdown("---")
            st.subheader("Memoria de Cálculo")
            st.markdown('<div class="apunte-box">', unsafe_allow_html=True)

            if metodo_actual == "ASD":
                st.markdown(r"""
                **1. Datos y conversión de referencia:**
                * Carga de servicio actuante: $T_s = P_r$
                * Factor de seguridad por fluencia en tensión (ASD): $\Omega_t = 1.67$
                * Relación de esbeltez: $\frac{L}{r}$ (referencia de esbeltez $\le 300$, y radio mínimo por esbeltez $r_{\text{mín}} = \frac{L}{300}$)
                """)
                st.latex(rf"\frac{{L}}{{r}} = \frac{{{round(out_l(L_imp), 2)}\text{{ {unidad_long}}}}}{{{round(r_disp, 2)}\text{{ {unidad_long}}}}} = {round(esbeltez_lr, 2)} \quad (\text{{mín. requerido: }} r \ge {round(r_min_req_disp, 2)}\text{{ {unidad_long}}})")
                st.markdown("**2. Resistencia nominal y resistencia admisible:**")
                st.latex(rf"T_n = F_y \cdot A_g = ({round(Fy_user, 2)}\text{{ {unidad_est}}}) \cdot ({round(ag_disp, 2)}\text{{ {unidad_area}}}) \rightarrow T_n = {round(pn_fluencia_disp, 2)}\text{{ {unidad_for}}}")
                st.latex(rf"\frac{{T_n}}{{\Omega_t}} = \frac{{{round(pn_fluencia_disp, 2)}\text{{ {unidad_for}}}}}{{1.67}} = {round(cap_disp, 2)}\text{{ {unidad_for}}}")
                st.markdown("**3. Radio de trabajo y diseño / comprobación:**")
                st.latex(rf"\text{{Radio de trabajo}} = \frac{{T_s}}{{T_n / \Omega_t}} = \frac{{{round(carga_actuante, 2)}}}{{{round(cap_disp, 2)}}} = {round(radio_trabajo, 2)} \quad ({round(radio_pct, 1)}\%)")
                st.latex(rf"A_{{g,\text{{req}}}} \ge \frac{{T_s \cdot \Omega_t}}{{F_y}} \implies A_{{g,\text{{req}}}} \ge {round(ag_req_disp, 2)}\text{{ {unidad_area}}}")
                st.latex(rf"\text{{Comprobación propuesta }} (A_{{g,\text{{prop}}}} = {round(propuesta_ag, 2)}\text{{ {unidad_area}}}): \quad \text{{Capacidad}} = {round(cap_prop_disp, 2)}\text{{ {unidad_for}}}, \quad \text{{RT}} = {round(rt_prop, 2)} \quad (\text{{{'Cumple' if cumple_prop else 'No cumple'}}})")
            else:
                st.markdown(r"""
                **1. Datos y verificación de esbeltez:**
                * Carga factorizada actuante: $P_u = P_r$
                * Factor de resistencia por fluencia en tensión (LRFD): $\phi_t = 0.90$
                * Relación de esbeltez: $\frac{L}{r}$ (referencia de esbeltez $\le 300$, y radio mínimo por esbeltez $r_{\text{mín}} = \frac{L}{300}$)
                """)
                st.latex(rf"\frac{{L}}{{r}} = \frac{{{round(out_l(L_imp), 2)}\text{{ {unidad_long}}}}}{{{round(r_disp, 2)}\text{{ {unidad_long}}}}} = {round(esbeltez_lr, 2)} \quad (\text{{mín. requerido: }} r \ge {round(r_min_req_disp, 2)}\text{{ {unidad_long}}})")
                st.markdown("**2. Resistencia nominal y resistencia de diseño:**")
                st.latex(rf"P_n = F_y \cdot A_g = ({round(Fy_user, 2)}\text{{ {unidad_est}}}) \cdot ({round(ag_disp, 2)}\text{{ {unidad_area}}}) \rightarrow P_n = {round(pn_fluencia_disp, 2)}\text{{ {unidad_for}}}")
                st.latex(rf"\phi_t P_n = 0.90 \cdot {round(pn_fluencia_disp, 2)}\text{{ {unidad_for}}} = {round(cap_disp, 2)}\text{{ {unidad_for}}}")
                st.markdown("**3. Radio de trabajo y diseño / comprobación:**")
                st.latex(rf"\text{{Radio de trabajo}} = \frac{{P_u}}{{\phi_t P_n}} = \frac{{{round(carga_actuante, 2)}}}{{{round(cap_disp, 2)}}} = {round(radio_trabajo, 2)} \quad ({round(radio_pct, 1)}\%)")
                st.latex(rf"A_{{g,\text{{req}}}} \ge \frac{{P_u}}{{\phi_t \cdot F_y}} \implies A_{{g,\text{{req}}}} \ge {round(ag_req_disp, 2)}\text{{ {unidad_area}}}")
                st.latex(rf"\text{{Comprobación propuesta }} (A_{{g,\text{{prop}}}} = {round(propuesta_ag, 2)}\text{{ {unidad_area}}}): \quad \text{{Capacidad}} = {round(cap_prop_disp, 2)}\text{{ {unidad_for}}}, \quad \text{{RT}} = {round(rt_prop, 2)} \quad (\text{{{'Cumple' if cumple_prop else 'No cumple'}}})")

            st.markdown('</div>', unsafe_allow_html=True)

            pdf_bytes = generar_pdf_analisis(f"Tensión Axial ({metodo_actual}) - Capítulo D", resultado)
            st.download_button("📥 Descargar Reporte en PDF", data=pdf_bytes, file_name="reporte_tension.pdf", mime="application/pdf")

    # ==========================================
    # 1. MÓDULO DE COMPRESIÓN (Capítulo E)
    # ==========================================
    elif tipo_miembro == "Compresión (Capítulo E)":
        st.header(f"📌 Capítulo E: Diseño en Compresión ({metodo_actual})")
        st.caption("Planteamiento editable: ajusta longitud, factor K, esfuerzo de fluencia y carga actuante para evaluar el caso.")

        col_cp1, col_cp2 = st.columns(2)
        with col_cp1:
            carga_comp = st.number_input(
                f"Carga axial actuante ({'kN' if es_metrico else 'kips'}):",
                value=800.0 if es_metrico else 180.0,
                min_value=0.1,
                key="comp_carga_act"
            )
            L_user = st.number_input(
                f"Longitud sin arriostrar (L) ({'mm' if es_metrico else 'in'}):",
                value=4500.0 if es_metrico else 180.0,
                min_value=1.0,
                key="comp_L"
            )
        with col_cp2:
            Fy_user = st.number_input(
                f"Esfuerzo de fluencia (Fy) ({'MPa' if es_metrico else 'ksi'}):",
                value=345.0 if es_metrico else 50.0,
                min_value=1.0,
                key="comp_Fy"
            )
            K = st.number_input(
                "Factor de longitud efectiva (K):",
                value=1.0,
                min_value=0.1,
                key="comp_K"
            )

        modo_entrada = st.radio("Fuente de datos de la sección:", ["Seleccionar perfil comercial W", "Ingresar propiedades manualmente"], key="comp")

        d_val, bf_val, tw_val, tf_val = 14.2, 8.0, 0.34, 0.61
        if modo_entrada == "Seleccionar perfil comercial W" and lista_nombres_perfiles:
            perfil_sel = seleccionar_perfil_con_busqueda("compresion")
            fila = df_perfiles[df_perfiles["perfil"] == perfil_sel].iloc[0]
            Ag_imp = float(fila["Ag"])
            r_imp = float(fila["ry"])
            d_val, bf_val, tw_val, tf_val = float(fila["d"]), float(fila["bf"]), float(fila["tw"]), float(fila["tf"])
        else:
            col1, col2 = st.columns(2)
            with col1:
                Ag_user = st.number_input(f"Área gruesa (Ag) ({'cm²' if es_metrico else 'in²'}):", value=100.0 if es_metrico else 15.5, min_value=0.1, key="comp_Ag")
            with col2:
                r_user = st.number_input(f"Radio de giro (r) ({'mm' if es_metrico else 'in'}):", value=87.6 if es_metrico else 3.45, min_value=0.01, key="comp_r")
            Ag_imp = conv_a(Ag_user)
            r_imp = conv_l(r_user)

        st.plotly_chart(dibujar_esquema_perfil_w(d_val, bf_val, tw_val, tf_val), use_container_width=True)

        L_imp = conv_l(L_user)
        Fy_imp = conv_f(Fy_user)
        E_imp = 29000.0

        if st.button("Calcular Compresión"):
            resultado = calcular_compresion(Ag_imp, r_imp, L_imp, Fy_imp, E_imp, K, metodo=metodo_actual)
            st.subheader("Resultados del Análisis:")
            if "error" in resultado:
                st.error(resultado["error"])
            else:
                fcr_val = out_f(extraer_valor(resultado["Fcr"]))
                cap_val = out_p(extraer_valor(resultado["capacidad_final"]))
                unidad_for = 'kN' if es_metrico else 'kips'
                unidad_est = 'MPa' if es_metrico else 'ksi'
                rt_comp = carga_comp / cap_val if cap_val > 0 else 0.0

                mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                mcol1.metric("Esbeltez (Kl/r)", resultado["esbeltez"])
                mcol2.metric("Esfuerzo Crítico (Fcr)", f"{round(fcr_val, 2)} {unidad_est}")
                mcol3.metric(resultado["etiqueta_cap"], f"{round(cap_val, 2)} {unidad_for}")
                mcol4.metric("Radio de Trabajo", f"{round(rt_comp, 2)} ({round(rt_comp*100, 1)}%)")

                st.info(f"**Estado normativo:** {resultado['estado']} | {'Cumple' if cap_val >= carga_comp else 'No cumple'} frente a carga de {round(carga_comp, 2)} {unidad_for}")

                st.markdown("---")
                st.subheader("Memoria de Cálculo Didáctica (AISC Capítulo E)")
                st.markdown('<div class="apunte-box">', unsafe_allow_html=True)
                if metodo_actual == "LRFD":
                    st.markdown(r"""
                    1. **Esfuerzo de pandeo elástico de Euler ($F_e$):**
                       $$F_e = \frac{\pi^2 \cdot E}{(K \cdot L / r)^2}$$
                    2. **Criterio de esbeltez límite y Esfuerzo Crítico ($F_{cr}$):**
                       * Si $\frac{K \cdot L}{r} \le 4.71 \sqrt{\frac{E}{F_y}}$:  $$F_{cr} = [0.658^{\frac{F_y}{F_e}}] \cdot F_y$$
                       * Si $\frac{K \cdot L}{r} > 4.71 \sqrt{\frac{E}{F_y}}$:  $$F_{cr} = 0.877 \cdot F_e$$
                    3. **Resistencia de diseño y radio de trabajo ($\phi_c = 0.90$):**
                       $$\phi_c P_n = 0.90 \cdot F_{cr} \cdot A_g \quad \text{y} \quad \text{RT} = \frac{P_u}{\phi_c P_n}$$
                    """)
                else:
                    st.markdown(r"""
                    1. **Esfuerzo de pandeo elástico de Euler ($F_e$):**
                       $$F_e = \frac{\pi^2 \cdot E}{(K \cdot L / r)^2}$$
                    2. **Esfuerzo crítico por flexión ($F_{cr}$):**
                       $$F_{cr} = [0.658^{\frac{F_y}{F_e}}] \cdot F_y \quad (\text{según límite de esbeltez})$$
                    3. **Resistencia admisible y radio de trabajo ($\Omega_c = 1.67$):**
                       $$\frac{P_n}{\Omega_c} = \frac{F_{cr} \cdot A_g}{1.67} \quad \text{y} \quad \text{RT} = \frac{P_a}{P_n / \Omega_c}$$
                    """)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("📈 Curva de Comportamiento Estructural")
                fig_pandeo = generar_grafico_buckling(Fy_imp, E_imp, resultado["esbeltez"], extraer_valor(resultado["Fcr"]))
                st.plotly_chart(fig_pandeo, use_container_width=True)

                pdf_bytes = generar_pdf_analisis(f"Compresión Axial ({metodo_actual}) - Capítulo E", resultado)
                st.download_button("📥 Descargar Reporte en PDF", data=pdf_bytes, file_name="reporte_compresion.pdf", mime="application/pdf")

    # ==========================================
    # 2. MÓDULO DE FLEXIÓN (Capítulo F)
    # ==========================================
    elif tipo_miembro == "Flexión (Capítulo F)":
        st.header(f"📌 Capítulo F: Diseño en Flexión ({metodo_actual})")
        st.caption("Planteamiento editable: modifica el momento actuante, longitudes de arriostramiento, Cb y propiedades de la sección.")

        modo_entrada = st.radio("Fuente de datos de la sección:", ["Seleccionar perfil comercial W", "Ingresar propiedades manualmente"], key="flex")

        d_val, bf_val, tw_val, tf_val = 14.2, 8.0, 0.34, 0.61
        if modo_entrada == "Seleccionar perfil comercial W" and lista_nombres_perfiles:
            perfil_sel = seleccionar_perfil_con_busqueda("flexion")
            fila = df_perfiles[df_perfiles["perfil"] == perfil_sel].iloc[0]
            Zx_imp = float(fila["Zx"])
            Sx_imp = float(fila["Sx"])
            d_val, bf_val, tw_val, tf_val = float(fila["d"]), float(fila["bf"]), float(fila["tw"]), float(fila["tf"])
        else:
            col1, col2 = st.columns(2)
            with col1:
                Zx_user = st.number_input(f"Módulo plástico (Zx) ({'cm³' if es_metrico else 'in³'}):", value=1835.0 if es_metrico else 112.0, min_value=0.1, key="flex_Zx")
            with col2:
                Sx_user = st.number_input(f"Módulo elástico (Sx) ({'cm³' if es_metrico else 'in³'}):", value=1605.0 if es_metrico else 98.0, min_value=0.1, key="flex_Sx")
            Zx_imp = conv_s(Zx_user)
            Sx_imp = conv_s(Sx_user)

        st.plotly_chart(dibujar_esquema_perfil_w(d_val, bf_val, tw_val, tf_val), use_container_width=True)

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            Fy_user = st.number_input(f"Esfuerzo de fluencia (Fy) ({'MPa' if es_metrico else 'ksi'}):", value=345.0 if es_metrico else 50.0, min_value=1.0, key="flex_Fy")
            Lb_user = st.number_input(f"Longitud sin arriostrar (Lb) ({'mm' if es_metrico else 'in'}):", value=3000.0 if es_metrico else 120.0, min_value=0.0, key="flex_Lb")
        with col_f2:
            Lp_user = st.number_input(f"Límite Lp ({'mm' if es_metrico else 'in'}):", value=2400.0 if es_metrico else 95.0, min_value=0.0, key="flex_Lp")
            Lr_user = st.number_input(f"Límite Lr ({'mm' if es_metrico else 'in'}):", value=7100.0 if es_metrico else 280.0, min_value=0.0, key="flex_Lr")
        with col_f3:
            Cb = st.number_input("Coeficiente de momento (Cb):", value=1.0, min_value=0.5, key="flex_Cb")
            mom_actuante = st.number_input(
                f"Momento actuante ({'kN·m' if es_metrico else 'kips·in'}):",
                value=120.0 if es_metrico else 1060.0,
                min_value=0.0,
                key="flex_mom_act"
            )

        Fy_imp = conv_f(Fy_user)
        Lb_imp = conv_l(Lb_user)
        Lp_imp = conv_l(Lp_user)
        Lr_imp = conv_l(Lr_user)

        if st.button("Calcular Flexión"):
            resultado = calcular_flexion(Fy_imp, Zx_imp, Sx_imp, Lb_imp, Lp_imp, Lr_imp, Cb, metodo=metodo_actual)
            st.subheader("Resultados del Análisis:")
            mn_val = out_m(extraer_valor(resultado["Mn_nominal"]))
            cap_val = out_m(extraer_valor(resultado["capacidad_final"]))
            unidad_mom = 'kN·m' if es_metrico else 'kips·in'
            rt_flex = mom_actuante / cap_val if cap_val > 0 else 0.0

            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Momento Nominal (Mn)", f"{round(mn_val, 2)} {unidad_mom}")
            mcol2.metric(resultado["etiqueta_cap"], f"{round(cap_val, 2)} {unidad_mom}")
            mcol3.metric("Radio de Trabajo", f"{round(rt_flex, 2)} ({round(rt_flex*100, 1)}%)")

            st.info(f"**Condición de Zona:** {resultado['estado']} | {'Cumple' if cap_val >= mom_actuante else 'No cumple'} frente a momento actuante de {round(mom_actuante, 2)} {unidad_mom}")

            st.markdown("---")
            st.subheader("Memoria de Cálculo Didáctica (AISC Capítulo F)")
            st.markdown('<div class="apunte-box">', unsafe_allow_html=True)
            st.markdown(r"""
            1. **Fluencia del patín en flexión (Zona Compacta, $L_b \le L_p$):**
               $$M_n = M_p = F_y \cdot Z_x$$
            2. **Pandeo Lateral-Torsional Inelástico ($L_p < L_b \le L_r$):**
               $$M_n = C_b \left[ M_p - (M_p - 0.7 F_y S_x) \left( \frac{L_b - L_p}{L_r - L_p} \right) \right] \le M_p$$
            3. **Resistencia y radio de trabajo:**
               * LRFD: $\phi_b = 0.90 \implies \phi_b M_n$ | ASD: $\Omega_b = 1.67 \implies \frac{M_n}{\Omega_b}$
            """)
            st.markdown('</div>', unsafe_allow_html=True)

            pdf_bytes = generar_pdf_analisis(f"Flexión ({metodo_actual}) - Capítulo F", resultado)
            st.download_button("📥 Descargar Reporte en PDF", data=pdf_bytes, file_name="reporte_flexion.pdf", mime="application/pdf")

    # ==========================================
    # 3. MÓDULO DE CORTANTE (Capítulo G)
    # ==========================================
    elif tipo_miembro == "Cortante (Capítulo G)":
        st.header(f"📌 Capítulo G: Diseño por Cortante ({metodo_actual})")
        st.caption("Planteamiento editable: modifica dimensiones del alma, esfuerzo de fluencia y cortante actuante.")

        modo_entrada = st.radio("Fuente de datos de la sección:", ["Seleccionar perfil comercial W", "Ingresar propiedades manualmente"], key="cort")

        d_val, bf_val, tw_val, tf_val = 14.2, 8.0, 0.34, 0.61
        if modo_entrada == "Seleccionar perfil comercial W" and lista_nombres_perfiles:
            perfil_sel = seleccionar_perfil_con_busqueda("cortante")
            fila = df_perfiles[df_perfiles["perfil"] == perfil_sel].iloc[0]
            d_imp = float(fila["d"])
            tw_imp = float(fila["tw"])
            d_val, bf_val, tw_val, tf_val = float(fila["d"]), float(fila["bf"]), float(fila["tw"]), float(fila["tf"])
        else:
            col1, col2 = st.columns(2)
            with col1:
                d_user = st.number_input(f"Peralte total (d) ({'mm' if es_metrico else 'in'}):", value=360.0 if es_metrico else 14.2, min_value=1.0, key="cort_d")
            with col2:
                tw_user = st.number_input(f"Espesor del alma (tw) ({'mm' if es_metrico else 'in'}):", value=8.6 if es_metrico else 0.34, min_value=0.01, key="cort_tw")
            d_imp = conv_l(d_user)
            tw_imp = conv_l(tw_user)

        st.plotly_chart(dibujar_esquema_perfil_w(d_val, bf_val, tw_val, tf_val), use_container_width=True)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            Fy_user = st.number_input(f"Esfuerzo de fluencia (Fy) ({'MPa' if es_metrico else 'ksi'}):", value=345.0 if es_metrico else 50.0, min_value=1.0, key="cort_Fy")
        with col_g2:
            cort_actuante = st.number_input(
                f"Cortante actuante ({'kN' if es_metrico else 'kips'}):",
                value=180.0 if es_metrico else 40.0,
                min_value=0.0,
                key="cort_act"
            )

        Fy_imp = conv_f(Fy_user)
        E_imp = 29000.0

        if st.button("Calcular Cortante"):
            resultado = calcular_cortante(d_imp, tw_imp, Fy_imp, E_imp, metodo=metodo_actual)
            st.subheader("Resultados del Análisis:")
            vn_val = out_p(extraer_valor(resultado["Vn_nominal"]))
            cap_val = out_p(extraer_valor(resultado["capacidad_final"]))
            unidad_for = 'kN' if es_metrico else 'kips'
            rt_cort = cort_actuante / cap_val if cap_val > 0 else 0.0

            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Resistencia Nominal (Vn)", f"{round(vn_val, 2)} {unidad_for}")
            mcol2.metric(resultado["etiqueta_cap"], f"{round(cap_val, 2)} {unidad_for}")
            mcol3.metric("Radio de Trabajo", f"{round(rt_cort, 2)} ({round(rt_cort*100, 1)}%)")

            st.info(f"**Estado normativo:** {resultado['estado']} | {'Cumple' if cap_val >= cort_actuante else 'No cumple'} frente a cortante actuante de {round(cort_actuante, 2)} {unidad_for}")

            st.markdown("---")
            st.subheader("Memoria de Cálculo Didáctica (AISC Capítulo G)")
            st.markdown('<div class="apunte-box">', unsafe_allow_html=True)
            st.markdown(r"""
            1. **Área del alma ($A_w$):**
               $$A_w = d \cdot t_w$$
            2. **Resistencia nominal al cortante ($V_n$):**
               $$V_n = 0.6 \cdot F_y \cdot A_w \cdot C_v$$
            3. **Resistencia y radio de trabajo:**
               * LRFD: $\phi_v = 1.00 \implies \phi_v V_n$ | ASD: $\Omega_v = 1.50 \implies \frac{V_n}{\Omega_v}$
            """)
            st.markdown('</div>', unsafe_allow_html=True)

            pdf_bytes = generar_pdf_analisis(f"Cortante ({metodo_actual}) - Capítulo G", resultado)
            st.download_button("📥 Descargar Reporte en PDF", data=pdf_bytes, file_name="reporte_cortante.pdf", mime="application/pdf")

    # ==========================================
    # 4. MÓDULO DE FLEXOCOMPRESIÓN (Capítulo H)
    # ==========================================
    elif tipo_miembro == "Flexocompresión (Capítulo H)":
        st.header(f"📌 Capítulo H: Flexocompresión ({metodo_actual})")
        st.caption("Planteamiento editable: modifica las demandas y capacidades axiales y de flexión para evaluar la interacción.")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Fuerza Axial")
            Pr_user = st.number_input(f"Carga requerida (Pr) ({'kN' if es_metrico else 'kips'}):", value=650.0 if es_metrico else 150.0, min_value=0.0, key="flexo_Pr")
            Pc_user = st.number_input(f"Capacidad disponible (Pc) ({'kN' if es_metrico else 'kips'}):", value=1550.0 if es_metrico else 350.0, min_value=0.1, key="flexo_Pc")
        with col2:
            st.subheader("Flexión Eje Mayor")
            Mrx_user = st.number_input(f"Momento requerido (Mrx) ({'kN·m' if es_metrico else 'kips·in'}):", value=50.0 if es_metrico else 45.0, min_value=0.0, key="flexo_Mrx")
            Mcx_user = st.number_input(f"Capacidad a flexión (Mcx) ({'kN·m' if es_metrico else 'kips·in'}):", value=135.0 if es_metrico else 120.0, min_value=0.1, key="flexo_Mcx")

        Pr_imp = conv_p(Pr_user)
        Pc_imp = conv_p(Pc_user)
        Mrx_imp = conv_m(Mrx_user)
        Mcx_imp = conv_m(Mcx_user)

        if st.button("Evaluar Interacción"):
            resultado = calcular_flexocompresion(Pr_imp, Pc_imp, Mrx_imp, Mcx_imp)
            st.subheader("Resultados de Interacción:")
            if "error" in resultado:
                st.error(resultado["error"])
            else:
                mcol1, mcol2 = st.columns(2)
                mcol1.metric("Relación Axial (Pr/Pc)", resultado["relacion_axial"])
                mcol2.metric("Índice de Interacción", resultado["indice_interaccion"])
                st.info(f"**Ecuación AISC aplicada:** {resultado['ecuacion']}")
                st.success(f"**Estado:** {resultado['estado']}")

                st.markdown("---")
                st.subheader("Memoria de Cálculo Didáctica (AISC Capítulo H)")
                st.markdown('<div class="apunte-box">', unsafe_allow_html=True)
                st.markdown(r"""
                1. **Evaluación de la Relación Axial:**
                   * Si $\frac{P_r}{P_c} \ge 0.2$ (Ecuación AISC H1-1a):
                     $$\frac{P_r}{P_c} + \frac{8}{9}\left(\frac{M_{rx}}{M_{cx}}\right) \le 1.0$$
                   * Si $\frac{P_r}{P_c} < 0.2$ (Ecuación AISC H1-1b):
                     $$\frac{P_r}{2 P_c} + \left(\frac{M_{rx}}{M_{cx}}\right) \le 1.0$$
                """)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("📈 Envolvente de Interacción de Capacidades")
                relacion_momento_calc = Mrx_imp / Mcx_imp
                fig_interaccion = generar_grafico_flexocompresion(resultado["relacion_axial"], relacion_momento_calc)
                st.plotly_chart(fig_interaccion, use_container_width=True)

                pdf_bytes = generar_pdf_analisis(f"Flexocompresión ({metodo_actual}) - Capítulo H", resultado)
                st.download_button("📥 Descargar Reporte en PDF", data=pdf_bytes, file_name="reporte_flexion.pdf", mime="application/pdf")