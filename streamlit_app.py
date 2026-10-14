import os
import re
import base64
import streamlit as st
import google.generativeai as genai
import gdown
from PIL import Image

st.set_page_config(
    page_title="Asistente Clínico | Óptica Zerzer",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 1. SEGURIDAD Y CREDENCIALES (Sin valores por defecto públicos)
# ----------------------------------------------------
try:
    CLAVE_ACCESO = st.secrets.get("CLAVE_ACCESO", None)
    CLAVE_ADMIN = st.secrets.get("CLAVE_ADMIN", None)
    API_KEY_SECRETA = str(st.secrets["GEMINI_API_KEY"]).strip().strip('"\'')
except Exception:
    CLAVE_ACCESO = None
    CLAVE_ADMIN = None
    API_KEY_SECRETA = ""

# Mapeo exacto de las subcarpetas en Google Drive dentro de "LIBROS GEM"
MAPEO_CARPETAS_DRIVE = {
    "🔬 Adaptación de Rígidas y Topografía": "Adaptacion_Rigidas_y_Topografia",
    "🎯 Terapia Visual": "Terapia_Visual",
    "👁️ Baja Visión": "Baja_Vision",
    "👶 Pediatría": "Pediatria",
    "🧠 Neurología": "Neurologia",
    "📚 General y Clínica": "General_y_Clinica"
}
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

def obtener_contexto_bibliografico_drive(categoria_seleccionada):
    """Conecta de forma privada con Google Drive para referenciar el contenido bibliográfico seguro."""
    contexto_libros = f"[Biblioteca Privada Óptica Zerzer - Especialidad: {categoria_seleccionada}]"
    try:
        if "gcp_service_account" in st.secrets:
            credentials_info = dict(st.secrets["gcp_service_account"])
            creds = service_account.Credentials.from_service_account_info(
                credentials_info, scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            service = build('drive', 'v3', credentials=creds)
            nombre_subcarpeta = MAPEO_CARPETAS_DRIVE.get(categoria_seleccionada, "General_y_Clinica")
            
            query_main = "name = 'LIBROS GEM' and mimeType = 'application/vnd.google-apps.folder'"
            results_main = service.files().list(q=query_main, spaces='drive', fields='files(id, name)').execute()
            folders_main = results_main.get('files', [])
            
            if folders_main:
                id_main = folders_main[0]['id']
                query_sub = f"'{id_main}' in parents and name = '{nombre_subcarpeta}' and mimeType = 'application/vnd.google-apps.folder'"
                results_sub = service.files().list(q=query_sub, spaces='drive', fields='files(id, name)').execute()
                folders_sub = results_sub.get('files', [])
                
                if folders_sub:
                    id_sub = folders_sub[0]['id']
                    query_files = f"'{id_sub}' in parents and trashed = false"
                    results_files = service.files().list(q=query_files, spaces='drive', fields='files(id, name)').execute()
                    files = results_files.get('files', [])
                    
                    titulos = [f"- {f['name']}" for f in files]
                    if titulos:
                        contexto_libros = f"Biblioteca Privada Óptica Zerzer (Referencias bibliográficas verificadas para {categoria_seleccionada}):\n" + "\n".join(titulos)
    except Exception:
        pass
    return contexto_libros

def validar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "es_admin" not in st.session_state:
        st.session_state.es_admin = False

    # Validación estricta: bloquea el ingreso si no hay claves configuradas en los Secrets
    if not CLAVE_ACCESO or not CLAVE_ADMIN:
        st.error("⚠️ Error de configuración de seguridad: Las claves de acceso no están definidas en los Secrets de Streamlit.")
        return False

    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("### 👁️ Óptica Zerzer - Asistente Clínico Optométrico")
            st.write("Plataforma exclusiva de consulta avanzada protegida por derechos de autor. Validación requerida.")
            
            password = st.text_input("Ingresá tu contraseña de acceso:", type="password")
            
            if st.button("Validar Ingreso"):
                if password == CLAVE_ADMIN:
                    st.session_state.autenticado = True
                    st.session_state.es_admin = True
                    st.rerun()
                elif password == CLAVE_ACCESO:
                    st.session_state.autenticado = True
                    st.session_state.es_admin = False
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta o membresía vencida.")
        return False
    return True

if validar_acceso():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    if "categoria_anterior" not in st.session_state:
        st.session_state.categoria_anterior = ""

    # BARRA LATERAL
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/experimental-optometry-color.png", width=70)
        st.title("Óptica Zerzer")
        if st.session_state.es_admin:
            st.markdown("👑 *Modo Administrador (Acceso Propietario)*")
        else:
            st.markdown("*Asistente Clínico Optométrico Profesional*")
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.es_admin = False
            st.session_state.mensajes = []
            st.rerun()

        st.markdown("### 📂 Seleccioná la Especialidad")
        
        categoria = st.selectbox(
            "Área clínica a consultar:",
            list(MAPEO_CARPETAS_DRIVE.keys())
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
            "Ingrese los parámetros y detalles extensos del caso:",
            placeholder="Pegá aquí todos los datos, anamnesis, test optométricos o notas de terapia visual...",
            height=250,
            key="txt_caso"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        boton_analizar = st.button("🚀 Generar Análisis Clínico Profundo")

        st.markdown("---")
        if st.button("🗑️ Limpiar Conversación / Nuevo Caso"):
            st.session_state.mensajes = []
            st.rerun()
        
        st.markdown('<p class="security-notice">Propiedad intelectual protegida.<br>© Óptica Zerzer. Uso exclusivo profesional.</p>', unsafe_allow_html=True)

    # PANEL PRINCIPAL
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
            st.warning("⚠️ No se detectó la clave de API configurada en Streamlit Secrets.")
        elif not imagenes_subidas and not caso_texto.strip():
            st.warning("⚠️ Por favor, suba al menos una fotografía o complete los datos clínicos del paciente.")
        else:
            with st.spinner(f"🔍 [Análisis Académico Profundo] Cruzando bibliografía de Google Drive y evaluando insumos para [{categoria}] (Esto puede demorar entre 1 y 3 minutos)..."):
                
                referencias_libros = obtener_contexto_bibliografico_drive(categoria)

                prompt_sistema = f"""
                Actúa como un profesor universitario de optometría de máxima jerarquía internacional y optómetra clínico especialista experto en {categoria}.
                Tu tarea es realizar un análisis exhaustivo, altamente detallado, estructurado y de rigor clínico absoluto para un colega profesional, basándote estrictamente en los protocolos bibliográficos de la biblioteca de Óptica Zerzer.

                Área Clínica Seleccionada: {categoria}
                {referencias_libros}

                Datos Clínicos Ingresados por el Optómetra: {caso_texto}

                El informe debe redactarse con un tono formal, médico-optométrico y sumamente claro. Debe contener obligatoriamente:
                1. 📋 **Especificación y Descripción Detallada del Caso**: Análisis pormenorizado de los datos y parámetros aportados para que el optómetra entienda la base del cuadro.
                2. 🔍 **Diagnóstico Clínico y Biomecánica Ocular**: Interpretación profunda del estado corneal, refractivo, acomodativo, binocular o neurológico según corresponda. Explicación de por qué se origina el problema.
                3. 🛠️ **Opciones de Solución Terapéutica y Plan de Abordaje**: Varias opciones o alternativas basadas en bibliografía especializada (Opción Primaria y Alternativas).
                4. 📅 **Control, Seguimiento y Pronóstico en Gabinete**: Pautado específico de revisiones y pronóstico visual esperado.
                """

                contents_input = [prompt_sistema]
                if imagenes_subidas:
                    for img_file in imagenes_subidas:
                        img = Image.open(img_file)
                        contents_input.append(img)

                try:
                    genai.configure(api_key=API_KEY_SECRETA)
                    # Modelo actualizado a gemini-3.8-flash según recomendación
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    response = model.generate_content(contents_input)
                    respuesta_modelo = response.text
                except Exception as e:
                    respuesta_modelo = f"⚠️ Error de conexión con Google: {str(e)}"

            if respuesta_modelo and not "⚠️" in respuesta_modelo:
                st.session_state.mensajes.append({"role": "user", "content": f"Caso clínico presentado:\n{caso_texto}"})
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_modelo})
                st.rerun()
            else:
                st.error(respuesta_modelo)

    # VISUALIZACIÓN DE LA CONVERSACIÓN Y SEGUIMIENTO AMPLIADO
    if len(st.session_state.mensajes) > 0:
        st.markdown("### 💬 Reporte Clínico y Conversación del Caso")
        
        for mensaje in st.session_state.mensajes:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])

        ultimo_reporte = st.session_state.mensajes[-1]["content"] if st.session_state.mensajes else ""
        
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
        st.write("Escribí aquí abajo con total comodidad y amplitud tus dudas, evolución o consultas de seguimiento para debatir con el asistente:")

        with st.form(key="form_seguimiento", clear_on_submit=True):
            pregunta_usuario = st.text_area(
                "Consulta de seguimiento o debate clínico:",
                placeholder="Escribí aquí tus dudas de seguimiento, evolución o nuevas mediciones...",
                height=150
            )
            enviar_seguimiento = st.form_submit_button("💬 Enviar Consulta de Seguimiento")

        if enviar_seguimiento and pregunta_usuario.strip():
            if not API_KEY_SECRETA.strip():
                st.warning("⚠️ No se detectó la clave de API.")
            else:
                st.session_state.mensajes.append({"role": "user", "content": pregunta_usuario})

                with st.spinner("🔍 [Analizando respuesta en gabinete]..."):
                    prompt_sistema = f"""
                    Actúa como un profesor universitario de optometría y especialista experto en {categoria}.
                    Responde al colega manteniendo coherencia total con el caso clínico analizado previamente y el historial de la conversación.
                    """

                    chat_history = [prompt_sistema]
                    for msg in st.session_state.mensajes:
                        chat_history.append(msg["content"])

                    try:
                        genai.configure(api_key=API_KEY_SECRETA)
                        model = genai.GenerativeModel('gemini-3.8-flash')
                        response = model.generate_content(chat_history)
                        respuesta_modelo = response.text
                    except Exception as e:
                        respuesta_modelo = f"⚠️ Error de conexión: {str(e)}"

                if respuesta_modelo and not "⚠️" in respuesta_modelo:
                    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_modelo})
                    st.rerun()
                else:
                    st.error(respuesta_modelo)
    else:
        st.info("👈 Completá los datos clínicos y las fotografías en la barra lateral, seleccioná la especialidad y hacé clic en **'Generar Análisis Clínico Profundo'** para iniciar el reporte.")
