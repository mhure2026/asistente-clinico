import os
import time
import json
import base64
import urllib.request
import re
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
            st.write("Plataforma exclusiva de consulta avanzada protegida por derechos de autor. Validación mensual requerida.")
            
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
    # Inicialización de estados de sesión
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    if "categoria_anterior" not in st.session_state:
        st.session_state.categoria_anterior = ""

    # BARRA LATERAL: Presentación, Solapas, Insumos y Datos Clínicos
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/experimental-optometry-color.png", width=70)
        st.title("Óptica Zerzer")
        st.markdown("*Asistente Clínico Optométrico Profesional*")
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.mensajes = []
            st.rerun()

        st.markdown("### 📂 Seleccioná la Especialidad")
        
        categoria = st.selectbox(
            "Área clínica a consultar:",
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
        st.markdown("### 📎 Fotografías del Caso")
        imagenes_subidas = st.file_uploader(
            "Subir hasta 2 imágenes (Topografía, córnea, mapas...):", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True,
            key="imgs_caso"
        )
        if imagenes_subidas and len(imagenes_subidas) > 2:
            st.warning("⚠️ Máximo 2 fotos permitidas.")
            imagenes_subidas = imagenes_subidas[:2]

        st.markdown("### 📝 Datos Clínicos del Paciente")
        caso_texto = st.text_area(
            "Ingrese los parámetros y detalles del caso:",
            placeholder="Ej: K1, K2, AV, síntomas, excentricidad, observaciones...",
            height=120,
            key="txt_caso"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        boton_analizar = st.button("🚀 Generar Análisis Clínico Profundo")

        st.markdown("---")
        if st.button("🗑️ Limpiar Conversación / Nuevo Caso"):
            st.session_state.mensajes = []
            st.rerun()
        
        st.markdown('<p class="security-notice">Propiedad intelectual protegida.<br>© Óptica Zerzer. Uso exclusivo profesional.</p>', unsafe_allow_html=True)

    # PANEL PRINCIPAL: Presentación institucional, tiempos de análisis y reporte interactivo
    col_p1, col_p2 = st.columns([2, 1])

    with col_p1:
        st.title("🔬 Panel de Resolución de Casos Clínicos")
        st.markdown(
            "Bienvenido colega a la plataforma avanzada de **Óptica Zerzer**. Este entorno exclusivo "
            "cruza la bibliografía internacional y los modelos de IA más avanzados para brindarle un soporte "
            "diagnóstico y terapéutico de máxima jerarquía en su gabinete."
        )

    with col_p2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="info-box">
            <b>⏱️ Tiempo de procesamiento profundo:</b><br>
            Para garantizar un reporte exhaustivo basado en bibliografía exhaustiva, el motor inteligente 
            demora de <b>1 a 3 minutos</b> en procesar el caso en profundidad. Agradecemos su aguardo.
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ACCIÓN DE GENERAR REPORTE INICIAL
    if boton_analizar:
        if not API_KEY_SECRETA.strip():
            st.warning("⚠️ No se detectó la API Key en los secretos de Streamlit.")
        elif not imagenes_subidas and not caso_texto.strip():
            st.warning("⚠️ Por favor, suba al menos una fotografía o complete los datos clínicos del paciente.")
        else:
            with st.spinner(f"🔍 [Análisis Académico Profundo] Cruzando bibliografía y evaluando insumos para [{categoria}] (Esto puede demorar entre 1 y 3 minutos)..."):
                
                prompt_sistema = f"""
                Actúa como un profesor universitario de optometría de máxima jerarquía internacional y optómetra clínico especialista experto en {categoria}.
                Tu tarea es realizar un análisis exhaustivo, altamente detallado, estructurado y de rigor clínico absoluto para un colega profesional.

                Área Clínica Seleccionada: {categoria}
                Datos Clínicos Ingresados por el Optómetra: {caso_texto}

                El informe debe redactarse con un tono formal, médico-optométrico y sumamente claro. Debe contener obligatoriamente:
                1. 📋 **Especificación y Descripción Detallada del Caso**: Análisis pormenorizado de los datos y parámetros aportados para que el optómetra entienda la base del cuadro.
                2. 🔍 **Diagnóstico Clínico y Biomecánica Ocular**: Interpretación profunda del estado corneal, refractivo, acomodativo, binocular o neurológico según corresponda. Explicación de por qué se origina el problema.
                3. 🛠️ **Opciones de Solución Terapéutica y Plan de Abordaje**: Varias opciones o alternativas basadas en bibliografía especializada (Opción Primaria y Alternativas).
                4. 📅 **Control, Seguimiento y Pronóstico en Gabinete**: Pautado específico de revisiones y pronóstico visual esperado.
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
                            respuesta_modelo = f"⚠️ Ocurrió un inconveniente temporal con la API de IA. Detalle técnico: {e}"
                        else:
                            time.sleep(2)

            if respuesta_modelo and not "⚠️" in respuesta_modelo:
                st.session_state.mensajes.append({"role": "user", "content": f"Caso clínico presentado:\n{caso_texto}"})
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_modelo})
                st.rerun()
            else:
                st.error(respuesta_modelo)

    # VISUALIZACIÓN DE LA CONVERSACIÓN Y CHAT CONTINUO DE SEGUIMIENTO
    if len(st.session_state.mensajes) > 0:
        st.markdown("### 💬 Reporte Clínico y Conversación del Caso")
        
        for mensaje in st.session_state.mensajes:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])

        # Generador de HTML limpio para descarga de PDF al pie del reporte
        ultimo_reporte = st.session_state.mensajes[-1]["content"] if st.session_state.mensajes else ""
        
        # Limpieza de código Markdown y LaTeX para impresión perfecta en HTML
        texto_limpio_html = ultimo_reporte
        texto_limpio_html = re.sub(r'#{1,6}\s*', '', texto_limpio_html)
        texto_limpio_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto_limpio_html)
        texto_limpio_html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', texto_limpio_html)
        texto_limpio_html = texto_limpio_html.replace(r'\text{D}', 'D')
        texto_limpio_html = texto_limpio_html.replace(r'\mu', 'µ')
        texto_limpio_html = texto_limpio_html.replace(r'^\circ', '°')
        texto_limpio_html = texto_limpio_html.replace(r'^{\circ}', '°')
        texto_limpio_html = texto_limpio_html.replace('$', '')
        
        lineas_html = []
        for l in texto_limpio_html.split('\n'):
            l_trim = l.strip()
            if l_trim.startswith('* ') or l_trim.startswith('- '):
                lineas_html.append('&bull; ' + l_trim[2:])
            else:
                lineas_html.append(l)
        texto_final_html = '<br>'.join(lineas_html)

        html_contenido = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte Clínico Oficial - Óptica Zerzer</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 30px; background: #fff; color: #2b2b2b; line-height: 1.6; border: 1px solid #e0e0e0; border-radius: 8px; }}
                .header {{ background-color: #0d6efd; color: white; padding: 20px; border-radius: 6px; margin-bottom: 25px; }}
                h1 {{ margin: 0; font-size: 22px; }}
                h3 {{ color: #0d6efd; border-bottom: 2px solid #e9ecef; padding-bottom: 5px; margin-top: 25px; }}
                .footer {{ margin-top: 40px; font-size: 11px; color: #6c757d; text-align: center; border-top: 1px solid #dee2e6; padding-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📋 Reporte Clínico Oficial - Óptica Zerzer</h1>
                <p><strong>Especialidad:</strong> {categoria}</p>
            </div>
            <div>
                {texto_final_html}
            </div>
            <div class="footer">
                Aviso legal: Este reporte es una herramienta de asistencia profesional generada por el Asistente Clínico de Óptica Zerzer. Uso exclusivo profesional.
            </div>
        </body>
        </html>
        """
        
        b64 = base64.b64encode(html_contenido.encode('utf-8')).decode('utf-8')
        nombre_archivo = f"Reporte_Clinico_Zerzer_{categoria.replace('/', '_').replace(' ', '_').replace('🔬 ', '').replace('🎯 ', '').replace('👁️ ', '').replace('👶 ', '').replace('🧠 ', '').replace('📚 ', '')}.html"
        
        href = f'''
        <a href="data:text/html;base64,{b64}" download="{nombre_archivo}" style="text-decoration: none;">
            <div style="background-color: #0d6efd; color: white; padding: 0.7rem; text-align: center; font-weight: bold; border-radius: 6px; width: 100%; margin-top: 20px; margin-bottom: 20px;">
                📥 Descargar Reporte Clínico Completo (Formato PDF / Impresión)
            </div>
        </a>
        '''
        st.markdown(href, unsafe_allow_html=True)
        st.info("💡 **Tip para imprimir:** Al abrir el archivo descargado en tu navegador, presioná **Ctrl + P** (o Cmd + P) y seleccioná **'Guardar como PDF'**.")

        st.markdown("---")
        st.markdown("### 🔄 Debate y Seguimiento Continuo del Caso")
        st.write("Podés seguir escribiendo aquí abajo para debatir dudas, consultar detalles o llegar a una conclusión clínica definitiva con el asistente.")

        pregunta_usuario = st.chat_input("Escribí tu consulta de seguimiento sobre este paciente...")

        if pregunta_usuario:
            if not API_KEY_SECRETA.strip():
                st.warning("⚠️ No se detectó la API Key en los secretos de Streamlit.")
            else:
                st.session_state.mensajes.append({"role": "user", "content": pregunta_usuario})
                with st.chat_message("user"):
                    st.markdown(pregunta_usuario)

                with st.spinner("🔍 [Analizando respuesta en gabinete]..."):
                    prompt_sistema = f"""
                    Actúa como un profesor universitario de optometría y especialista experto en {categoria}.
                    Responde al colega manteniendo coherencia total con el caso clínico analizado previamente y el historial de la conversación.
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
    else:
        st.info("👈 Completá los datos clínicos y las fotografías en la barra lateral, seleccioná la especialidad y hacé clic en **'Generar Análisis Clínico Profundo'** para iniciar el reporte.")
