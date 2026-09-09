import os
import time
import json
import base64
import urllib.request
import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="Asistente Clínico | Óptica Zerzer",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CLAVE_ACCESO = "optica2026"

# Aquí el sistema busca la clave de forma invisible en el cofre seguro
try:
    API_KEY_SECRETA = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY_SECRETA = os.environ.get("GEMINI_API_KEY", "")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        background-color: #0d6efd;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.6rem;
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

if validar_acceso():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/experimental-optometry-color.png", width=70)
        st.title("Óptica Zerzer")
        st.markdown("*Asistente Clínico Optométrico*")
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

        st.markdown("### 📂 Seleccioná la Categoría / Solapa")
        
        categoria = st.selectbox(
            "Área especializada a consultar:",
            [
                "🔬 Adaptación de Rígidas y Topografía",
                "🎯 Terapia Visual",
                "👁️ Baja Visión",
                "👶 Pediatría",
                "🧠 Neurología",
                "📚 General y Clínica"
            ]
        )
        
        st.markdown("---")
        st.markdown("### 📎 Insumos del Caso")
        
        imagenes_subidas = st.file_uploader(
            "Subir imágenes (ej. Topografía, mapas, córnea - Máx 2)", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
        
        if imagenes_subidas and len(imagenes_subidas) > 2:
            st.warning("⚠️ Máximo 2 fotos permitidas.")
            imagenes_subidas = imagenes_subidas[:2]
        
        caso_texto = st.text_area(
            "Detalle del caso clínico y parámetros:",
            placeholder="Ej: K1: 43.00 @ 90, K2: 46.50 @ 180, AV, síntomas, excentricidad...",
            height=130
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        boton_analizar = st.button("🚀 Generar Análisis Clínico Profundo")
        
        st.markdown("---")
        st.markdown('<p class="security-notice">Propiedad intelectual protegida.<br>© Óptica Zerzer. Uso exclusivo profesional.</p>', unsafe_allow_html=True)

    col_main_1, col_main_2 = st.columns([2, 1])

    with col_main_1:
        st.title("🔬 Panel de Resolución de Casos Clínicos")
        st.markdown(
            "Bienvenido colega. Este asistente inteligente procesa los parámetros y las imágenes clínicas aplicando "
            "rigurosos protocolos universitarios y bibliografía avanzada de la solapa seleccionada para ofrecerle "
            "un diagnóstico clínico profundo, preciso y con opciones terapéuticas claras para su gabinete."
        )

    with col_main_2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="info-box">
            <b>⏱️ Nota sobre el análisis profundo:</b><br>
            Para garantizar un reporte exhaustivo, fundamentado y de máxima calidad académica, 
            el sistema procesa el caso en profundidad durante <b>1 a 2 minutos</b>. Agradecemos su espera.
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("---")

    if boton_analizar:
        if not API_KEY_SECRETA.strip():
            st.warning("⚠️ No se detectó la API Key en los secretos de Streamlit. Configurá los secretos en tu panel de Streamlit Cloud.")
        elif not imagenes_subidas and not caso_texto.strip():
            st.warning("⚠️ Por favor, subí al menos una imagen o completá los datos del caso clínico en texto.")
        else:
            with st.spinner(f"🔍 [Análisis Académico en Curso] Cruzando parámetros bibliográficos para [{categoria}] (Aprox. 1-2 min)..."):
                
                prompt_sistema = f"""
                Actúa como un profesor universitario de optometría de máxima jerarquía internacional y optómetra clínico especialista experto en {categoria}.
                Tu tarea es realizar un análisis exhaustivo, altamente detallado, estructurado y de rigor clínico absoluto para un colega profesional.

                Área Clínica Seleccionada: {categoria}
                Parámetros y Datos Cuantitativos/Cualitativos Ingresados: {caso_texto}

                El informe debe redactarse con un tono formal, médico-optométrico y sumamente claro. Debe contener obligatoriamente la siguiente estructura profesional:

                1. 📋 **Resumen y Evaluación del Caso Clínico**: Análisis pormenorizado de los datos aportados, correlacionándolos con la alteración visual o patológica de la solapa.
                2. 🔍 **Diagnóstico Clínico y Biomecánica Ocular**: Interpretación profunda del estado corneal, refractivo, acomodativo, binocular o neurológico según corresponda. Explicación de por qué se origina el problema.
                3. 🛠️ **Opciones de Solución Terapéutica y Plan de Abordaje**:
                   - **Opción Primaria / Ideal**: Diseño exacto sugerido, parámetros geométricos, materiales, prescripción o pautas de intervención detalladas.
                   - **Opción Alternativa**: Plan de respaldo o variante clínica ante posibles intolerancias o variaciones.
                4. 📅 **Control, Seguimiento y Pronóstico en Gabinete**: Pautado específico de las revisiones a corto y mediano plazo, signos de alerta y pronóstico visual esperado.
                """

                parts = [{"text": prompt_sistema}]
                if imagenes_subidas:
                    for img_file in imagenes_subidas:
                        img_bytes = img_file.read()
                        encoded = base64.b64encode(img_bytes).decode('utf-8')
                        parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": encoded
                            }
                        })

                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_SECRETA}"
                payload = {"contents": [{"parts": parts}]}
                
                respuesta_modelo = None
                for intento in range(3):
                    try:
                        req = urllib.request.Request(
                            url,
                            data=json.dumps(payload).encode('utf-8'),
                            headers={'Content-Type': 'application/json'}
                        )
                        with urllib.request.urlopen(req) as response:
                            res_data = json.loads(response.read().decode('utf-8'))
                            respuesta_modelo = res_data['candidates'][0]['content']['parts'][0]['text']
                            break
                    except Exception as e:
                        if intento == 2:
                            respuesta_modelo = f"⚠️ Ocurrió un inconveniente temporal con la API de IA. Detalle técnico: {e}"
                        else:
                            time.sleep(2)

            if respuesta_modelo and not "⚠️" in respuesta_modelo:
                st.success("✅ ¡Análisis Clínico Profundo Generado con Éxito!")
                
                resultado_markdown = f"""
### 📋 Reporte Clínico Oficial - Óptica Zerzer
* **Área / Solapa Evaluada:** {categoria}
* **Validación de Sesión:** Activa (Colega Autorizado)

---
{respuesta_modelo}
---
*Aviso legal: Este reporte es una herramienta de asistencia profesional generada por el Asistente Clínico de Óptica Zerzer. Queda prohibida la reproducción total o parcial de la metodología, bases de datos y estructura de esta plataforma.*
                """
                
                st.markdown(resultado_markdown)
                
                st.markdown("<br>", unsafe_allow_html=True)
                buffer = BytesIO()
                buffer.write(resultado_markdown.encode('utf-8'))
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Descargar Reporte Clínico (Formato Texto / PDF)",
                    data=buffer,
                    file_name=f"Reporte_Clinico_Zerzer_{categoria.replace('/', '_').replace(' ', '_').replace('🔬 ', '').replace('🎯 ', '').replace('👁️ ', '').replace('👶 ', '').replace('🧠 ', '').replace('📚 ', '')}.txt",
                    mime="text/plain"
                )
            else:
                st.error(respuesta_modelo)
