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
    # Inicializar el historial de chat en la sesión
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
        
        # Si cambia de categoría, limpiamos el chat anterior para enfocar al nuevo especialista
        if st.session_state.categoria_anterior != categoria:
            st.session_state.categoria_anterior = categoria
            st.session_state.mensajes = []

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
        
        if st.button("🗑️ Limpiar Conversación del Caso"):
            st.session_state.mensajes = []
            st.rerun()
        
        st.markdown("---")
        st.markdown('<p class="security-notice">Propiedad intelectual protegida.<br>© Óptica Zerzer. Uso exclusivo profesional.</p>', unsafe_allow_html=True)

    # Panel Principal de Conversación Continua
    st.title("🔬 Panel de Discusión de Casos Clínicos")
    st.markdown(
        f"**Especialidad Activa:** {categoria} — Realice sus consultas iniciales o continúe debatiendo "
        "el diagnóstico, parámetros y opciones terapéuticas en tiempo real con el asistente experto."
    )
    st.markdown("---")

    # Mostrar el historial completo de mensajes en pantalla
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])

    # Entrada de texto inferior para chatear permanentemente (estilo chat moderno)
    pregunta_usuario = st.chat_input("Escribí tu consulta, evolución del paciente o duda sobre el caso clínico...")

    if pregunta_usuario:
        if not API_KEY_SECRETA.strip():
            st.warning("⚠️ No se detectó la API Key en los secretos de Streamlit.")
        else:
            # Guardar y mostrar el mensaje del usuario de inmediato
            st.session_state.mensajes.append({"role": "user", "content": pregunta_usuario})
            with st.chat_message("user"):
                st.markdown(pregunta_usuario)

            with st.spinner("🔍 [Analizando caso en gabinete] Cruzando fundamentos bibliográficos..."):
                
                # Construir el historial y contexto para enviar a Gemini
                prompt_sistema = f"""
                Actúa como un profesor universitario de optometría de máxima jerarquía internacional y optómetra clínico especialista experto en {categoria}.
                Tu tarea es responder y debatir con un colega profesional de manera exhaustiva, detallada, estructurada y de rigor clínico absoluto.
                Mantén la coherencia con los mensajes previos de la conversación.
                """

                contents = [{"parts": [{"text": prompt_sistema}]}]

                # Si es el primer mensaje y subió imágenes, las añadimos
                if len(st.session_state.mensajes) == 1 and imagenes_subidas:
                    for img_file in imagenes_subidas:
                        img_bytes = img_file.read()
                        encoded = base64.b64encode(img_bytes).decode('utf-8')
                        contents[0]["parts"].append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": encoded
                            }
                        })

                # Agregar todo el historial de la charla para mantener memoria
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
                            respuesta_modelo = f"⚠️ Ocurrió un inconveniente temporal con la API de IA. Detalle técnico: {e}"
                        else:
                            time.sleep(2)

            if respuesta_modelo and not "⚠️" in respuesta_modelo:
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_modelo})
                with st.chat_message("assistant"):
                    st.markdown(respuesta_modelo)
                st.rerun()
            else:
                st.error(respuesta_modelo)
