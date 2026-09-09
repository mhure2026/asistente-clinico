import os
import time
import json
import base64
import urllib.request
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Asistente Clínico | Óptica Zerzer",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# CONFIGURACIÓN DE SEGURIDAD Y CREDENCIALES
# ----------------------------------------------------
CLAVE_ACCESO = "optica2026"

try:
    API_KEY_SECRETA = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY_SECRETA = os.environ.get("GEMINI_API_KEY", "")
# ----------------------------------------------------

# Estética y blindaje profesional
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
    # Inicializar variables de sesión
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    if "categoria_anterior" not in st.session_state:
        st.session_state.categoria_anterior = ""

    with st.sidebar:
        st.image("https://img.icons8.com/color/96/experimental-optometry-color.png", width=70)
        st.title("Óptica Zerzer")
        st.markdown("*Asistente Clínico Optométrico*")
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.mensajes = []
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
        
        if st.session_state.categoria_anterior != categoria:
            st.session_state.categoria_anterior = categoria
            st.session_state.mensajes = []

        st.markdown("---")
        if st.button("🗑️ Limpiar Conversación / Nuevo Caso"):
            st.session_state.mensajes = []
            st.rerun()
        
        st.markdown("---")
        st.markdown('<p class="security-notice">Propiedad intelectual protegida.<br>© Óptica Zerzer. Uso exclusivo profesional.</p>', unsafe_allow_html=True)

    # Panel Principal
    st.title("🔬 Panel de Resolución de Casos Clínicos")
    st.markdown(
        f"**Especialidad Activa:** {categoria} — Cargue los datos iniciales y las imágenes del paciente abajo, "
        "o continúe debatiendo en el chat de seguimiento."
    )
    st.markdown("---")

    # Si el chat está vacío, mostramos el formulario inicial de carga de caso (Fotos + Texto)
    if len(st.session_state.mensajes) == 0:
        st.markdown("### 📎 Carga inicial del caso clínico")
        
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            imagenes_subidas = st.file_uploader(
                "Subir imágenes (ej. Topografía, mapas, córnea - Máx 2)", 
                type=["png", "jpg", "jpeg"], 
                accept_multiple_files=True,
                key="imagenes_inicio"
            )
            if imagenes_subidas and len(imagenes_subidas) > 2:
                st.warning("⚠️ Máximo 2 fotos permitidas.")
                imagenes_subidas = imagenes_subidas[:2]
        
        caso_texto = st.text_area(
            "Detalle del caso clínico y parámetros del paciente:",
            placeholder="Ej: K1: 43.00 @ 90, K2: 46.50 @ 180, AV, síntomas, excentricidad...",
            height=130,
            key="texto_inicio"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Generar Análisis Clínico Profundo"):
            if not API_KEY_SECRETA.strip():
                st.warning("⚠️ No se detectó la API Key en los secretos de Streamlit.")
            elif not imagenes_subidas and not caso_texto.strip():
                st.warning("⚠️ Por favor, subí al menos una imagen o completá los datos del caso clínico.")
            else:
                with st.spinner(f"🔍 [Análisis Académico en Curso] Cruzando parámetros para [{categoria}] (Aprox. 1-2 min)..."):
                    
                    prompt_sistema = f"""
                    Actúa como un profesor universitario de optometría de máxima jerarquía internacional y optómetra clínico especialista experto en {categoria}.
                    Tu tarea es realizar un análisis exhaustivo, altamente detallado, estructurado y de rigor clínico absoluto para un colega profesional.

                    Área Clínica Seleccionada: {categoria}
                    Parámetros e Insumos Ingresados: {caso_texto}

                    El informe debe redactarse con un tono formal, médico-optométrico y claro, conteniendo obligatoriamente:
                    1. 📋 **Resumen y Evaluación del Caso Clínico**
                    2. 🔍 **Diagnóstico Clínico y Biomecánica Ocular**
                    3. 🛠️ **Opciones de Solución Terapéutica y Plan de Abordaje** (Primaria y Alternativa)
                    4. 📅 **Control, Seguimiento y Pronóstico en Gabinete**
                    """

                    contents = [{"parts": [{"text": prompt_sistema}]}]
                    if imagenes_subidas:
                        for img_file in imagenes_subidas:
                            img_bytes = img_file.read()
                            encoded = base64.b64encode(img_bytes).decode('utf-8')
                            contents[0]["parts"].append({
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": encoded
                                }
                            })

                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_SECRETA}"
                    payload = {"contents": contents}
                    
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
                                respuesta_modelo = f"⚠️ Ocurrió un inconveniente temporal con la API. Detalle: {e}"
                            else:
                                time.sleep(2)

                if respuesta_modelo and not "⚠️" in respuesta_modelo:
                    # Guardamos el prompt inicial y la respuesta en el historial
                    st.session_state.mensajes.append({"role": "user", "content": f"Caso clínico ingresado:\n{caso_texto}"})
                    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_modelo})
                    st.rerun()
                else:
                    st.error(respuesta_modelo)

    # Si ya hay historial de chat, mostramos la conversación y la barra para seguir escribiendo abajo
    else:
        for mensaje in st.session_state.mensajes:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])

        pregunta_usuario = st.chat_input("Escribí tu consulta de seguimiento, evolución o duda sobre este paciente...")

        if pregunta_usuario:
            if not API_KEY_SECRETA.strip():
                st.warning("⚠️ No se detectó la API Key en los secretos de Streamlit.")
            else:
                st.session_state.mensajes.append({"role": "user", "content": pregunta_usuario})
                with st.chat_message("user"):
                    st.markdown(pregunta_usuario)

                with st.spinner("🔍 [Analizando seguimiento en gabinete]..."):
                    prompt_sistema = f"""
                    Actúa como un profesor universitario de optometría y especialista experto en {categoria}.
                    Responde al colega manteniendo la coherencia total con el caso clínico analizado previamente en la conversación.
                    """

                    contents = [{"parts": [{"text": prompt_sistema}]}]
                    for msg in st.session_state.mensajes:
                        rol_gemini = "user" if msg["role"] == "user" else "model"
                        contents.append({
                            "role": rol_gemini,
                            "parts": [{"text": msg["content"]}]
                        })

                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY_SECRETA}"
                    payload = {"contents": contents}
                    
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
                                respuesta_modelo = f"⚠️ Error temporal: {e}"
                            else:
                                time.sleep(2)

                if respuesta_modelo and not "⚠️" in respuesta_modelo:
                    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_modelo})
                    with st.chat_message("assistant"):
                        st.markdown(respuesta_modelo)
                    st.rerun()
                else:
                    st.error(respuesta_modelo)
