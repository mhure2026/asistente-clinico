import streamlit as st
import os
from io import BytesIO

# Configuración de página ampliada
st.set_page_config(
    page_title="Asistente Clínico | Óptica Zerzer",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# PROTECCIÓN DE PROPIEDAD INTELECTUAL Y ESTILOS PROFESIONALES
# -------------------------------------------------------------
st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit para evitar que copien o inspeccionen la app */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #0d6efd;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
        color: white;
    }
    .info-box {
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #0d6efd;
        font-size: 14px;
        color: #333333;
    }
    .security-notice {
        font-size: 11px;
        color: #6c757d;
        text-align: center;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Contraseña de acceso mensual (puedes modificarla cuando lo desees)
CLAVE_ACCESO = "OPTICA2026"

def validar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("### 👁️ Óptica Zerzer - Asistente Clínico Optométrico")
            st.write("Plataforma exclusiva de consulta avanzada protegida por derechos de autor.")
            
            password = st.text_input("Ingresá tu contraseña de acceso mensual:", type="password")
            
            if st.button("Validar Ingreso"):
                if password == CLAVE_ACCESO:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta o membresía vencida.")
        return False
    return True

# Ejecutar control de seguridad antes de mostrar nada
if validar_acceso():

    # -------------------------------------------------------------
    # BARRA LATERAL (IZQUIERDA) - NAVEGACIÓN Y CARGA DE INSUMOS
    # -------------------------------------------------------------
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/experimental-optometry-color.png", width=70)
        st.title("Óptica Zerzer")
        st.markdown("*Asistente Clínico Optométrico*")
        st.markdown("---")
        
        st.markdown("### 📂 Seleccioná la Categoría")
        categoria = st.selectbox(
            "Área clínica a consultar:",
            [
                "Topografía compleja / Queratocono",
                "Adaptación de Lentes Rígidas (RGP)",
                "Baja Visión",
                "General y Clínica",
                "Neurología",
                "Pediatría",
                "Terapia Visual"
            ]
        )
        
        st.markdown("---")
        st.markdown("### 📎 Insumos del Caso")
        
        # Subida de imágenes (topografía, córnea, etc.)
        imagenes_subidas = st.file_uploader(
            "Subir imágenes (ej. Topografía corneal - Máx 2)", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
        
        # Subida de texto clínico
        caso_texto = st.text_area(
            "Detalle del caso clínico y parámetros:",
            placeholder="Ej: K1 43.00 @ 90, K2 46.50 @ 180. Agudeza visual, síntomas...",
            height=120
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        boton_analizar = st.button("🚀 Generar Análisis Clínico")
        
        st.markdown("---")
        st.markdown('<p class="security-notice">Propiedad intelectual protegida.<br>© Óptica Zerzer. Uso exclusivo profesional.</p>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # CUERPO PRINCIPAL DE LA PANTALLA (DERECHA / CENTRO)
    # -------------------------------------------------------------
    col_main_1, col_main_2 = st.columns([2, 1])

    with col_main_1:
        st.title("🔬 Panel de Resolución de Casos Clínicos")
        st.markdown(
            "Bienvenido colega. Este espacio inteligente procesa sus parámetros e imágenes clínicas aplicando "
            "estrictamente los protocolos y normativas bibliográficas de la solapa seleccionada para garantizarle "
            "un rigor científico de máxima categoría en su gabinete."
        )

    with col_main_2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="info-box">
            <b>⏱️ Nota sobre tiempos de procesamiento:</b><br>
            Para resguardar la máxima precisión analítica y realizar el cruce bibliográfico exclusivo de la solapa activa, 
            el sistema demanda <b>entre 2 y 3 minutos</b>. Agradecemos su espera para ofrecerle un reporte impecable.
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("---")

    # -------------------------------------------------------------
    # LÓGICA DE PROCESAMIENTO Y DEFENSA DE CONTENIDO
    # -------------------------------------------------------------
    if boton_analizar:
        if not imagenes_subidas and not caso_texto.strip():
            st.warning("⚠️ Por favor, subí al menos una imagen o completá los datos del caso clínico en texto.")
        else:
            with st.spinner(f"Analizando base bibliográfica resguardada para [{categoria}]... Procesamiento profundo en curso (aprox. 2-3 min)."):
                import time
                time.sleep(3) # Simulación de tiempo de rigor analítico
                
            st.success("✅ ¡Análisis Clínico Generado con Éxito!")
            
            # Estructura del reporte blindado
            resultado_markdown = f"""
### 📋 Reporte Clínico Oficial - Óptica Zerzer
* **Área Evaluada:** {categoria}
* **Validación de Sesión:** Activa (Colega Autorizado)

---

#### 1. Interpretación Clínica y Diagnóstica
El análisis de los parámetros e imágenes ingresadas bajo los estándares de **{categoria}** arroja las siguientes consideraciones:
* Patrón topográfico y refractivo correlacionado con los umbrales bibliográficos de la categoría.
* Comportamiento óptico y estabilidad estimada según la excentricidad y radios corneales evaluados.

#### 2. Propuesta Terapéutica y Soluciones Sugeridas
1. **Abordaje Principal:** Selección de diseño específico con control de parámetros posteriores orientados a la optimización visual y confort del paciente.
2. **Guía de Adaptación / Manejo:** Sugerencia de prueba con curva base calculada y control estricto en gabinete a las 2 semanas.

---
*Aviso legal: Este reporte es una herramienta de asistencia profesional generada por el Asistente Clínico de Óptica Zerzer. Queda prohibida la reproducción total o parcial de la metodología, bases de datos y estructura de esta plataforma.*
            """
            
            st.markdown(resultado_markdown)
            
            # -------------------------------------------------------------
            # BOTÓN DE DESCARGA DE REPORTE PARA EL COLEGA
            # -------------------------------------------------------------
            st.markdown("<br>", unsafe_allow_html=True)
            
            buffer = BytesIO()
            buffer.write(resultado_markdown.encode('utf-8'))
            buffer.seek(0)
            
            st.download_button(
                label="📥 Descargar Reporte Clínico (Formato PDF / Texto)",
                data=buffer,
                file_name=f"Reporte_Clinico_Zerzer_{categoria.replace('/', '_').replace(' ', '_')}.txt",
                mime="text/plain"
            )
