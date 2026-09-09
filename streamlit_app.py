import os
import time
import streamlit as st
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from google import genai
from PIL import Image
from fpdf import FPDF

st.set_page_config(
    page_title="Asistente Clínico de Optometría Avanzada",
    page_icon="👁️‍🗨️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🔒 SISTEMA DE ACCESO PRIVADO (CON CONTRASEÑA)
# ==========================================
# Definí tu contraseña activa (la que le pasás al colega tras el pago mensual)
# Podés cambiarla fácilmente o adaptarla mes a mes (ej: "zerzer2026", "optica30", etc.)
CONTRASENIA_VALIDA = "zerzer2026"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔐 Acceso Restringido - Profesionales")
        st.info("Este sistema es de uso exclusivo para colegas suscriptores de Óptica Zerzer. Ingrese su contraseña mensual para continuar.")
        
        input_pass = st.text_input("Contraseña de acceso:", type="password")
        if st.button("Ingresar al Sistema", use_container_width=True):
            if input_pass == CONTRASENIA_VALIDA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta. Verifique sus datos o comuníquese con Óptica Zerzer.")
    st.stop() # Detiene la ejecución aquí si no está autenticado

# ==========================================
# 🛠️ APLICACIÓN PRINCIPAL (UNA VEZ ADENTRO)
# ==========================================

with st.sidebar:
    st.title("Panel Clínico")
    
    # Botón para cerrar sesión si lo deseas
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
        
    api_key_input = st.text_input("🔑 Gemini API Key", type="password")
    
    st.markdown("---")
    modo_consulta = st.selectbox(
        "🧠 Área Clínica / Colección:",
        [
            "🔬 Adaptación de Rígidas y Topografía",
            "🎯 Terapia Visual",
            "👁️ Baja Visión",
            "👶 Pediatria",
            "🧠 Neurología",
            "📚 General y Clínica"
        ]
    )
    
    uploaded_images = st.file_uploader(
        "📷 Subir imágenes clínicas (Máximo 2 fotos)", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True,
        help="Subí hasta 2 imágenes clave."
    )
    
    if uploaded_images and len(uploaded_images) > 2:
        st.warning("⚠️ Máximo 2 fotos permitidas para evitar colapsos.")
        uploaded_images = uploaded_images[:2]
    
    paciente_info = st.text_area(
        "📝 Datos cuantitativos / Caso clínico:",
        placeholder="Ej: K1: 44.00 @ 90, K2: 47.50 @ 180...",
        height=140
    )

st.title("👁️‍🗨️ Sistema Experto de Apoyo Clínico en Optometría")

# --- CARTEL AMIGABLE EXPLICATIVO ---
st.info(
    "💡 **Nota sobre el análisis de imágenes clínicas y topografías:**\n\n"
    "Debido a la alta complejidad y densidad de datos que contienen los mapas topográficos y las imágenes oculares, "
    "el sistema realiza una inspección visual detallada que puede tomar entre **2 a 3 minutos** en procesar la consulta. "
    "¡La precisión del diagnóstico y los parámetros sugeridos valen totalmente la espera!",
    icon="⏱️"
)

api_key = api_key_input if api_key_input else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ Por favor, ingresá tu Gemini API Key en la barra lateral para comenzar.")
    st.stop()

client = genai.Client(api_key=api_key)

@st.cache_resource
def obtener_motor_chroma():
    chroma_client = chromadb.PersistentClient(path="./base_datos_optometria")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    return chroma_client, emb_fn

chroma_client, emb_fn = obtener_motor_chroma()

mapeo_colecciones = {
    "🔬 Adaptación de Rígidas y Topografía": "colleccion_rigidas",
    "🎯 Terapia Visual": "colleccion_terapia",
    "👁️ Baja Visión": "colleccion_baja_vision",
    "👶 Pediatria": "colleccion_pediatria",
    "🧠 Neurología": "colleccion_neurologia",
    "📚 General y Clínica": "colleccion_general"
}

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Escribí tu consulta sobre el caso o las imágenes...")

if prompt or uploaded_images:
    user_input_display = prompt if prompt else "Analizar las imágenes clínicas adjuntas junto con el caso."
    st.session_state.messages.append({"role": "user", "content": user_input_display})
    
    with st.chat_message("user"):
        st.markdown(user_input_display)
        if uploaded_images:
            cols = st.columns(len(uploaded_images))
            for idx, img_file in enumerate(uploaded_images):
                with cols[idx]:
                    st.image(Image.open(img_file), caption=f"Foto {idx+1}", width=200)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Analizando mapas topográficos y contrastando con literatura científica (Esto puede tomar unos minutos)..."):
            
            nombre_col_actual = mapeo_colecciones.get(modo_consulta, "colleccion_general")
            coleccion_activa = chroma_client.get_or_create_collection(name=nombre_col_actual, embedding_function=emb_fn)
            
            query_texto = f"{prompt if prompt else ''} {paciente_info}"
            resultados = coleccion_activa.query(query_texts=[query_texto], n_results=1)
            documentos = resultados.get("documents", [[]])[0]
            contexto = "\n\n".join(documentos) if documentos else "Sin contexto específico en libros."
            
            prompt_sistema = f"""
            Actúa como un profesor universitario de optometría y optómetra clínico especialista.
            Sé riguroso, profundo y estructurado. Analiza detalladamente las imágenes subidas (topografías/fotos), los datos aportados y la bibliografía de referencia para redactar una guía clínica exhaustiva.

            Área: {modo_consulta}
            Datos: {paciente_info}
            Bibliografía: {contexto}
            Consulta: {prompt if prompt else "Análisis integral de las imágenes clínicas aportadas."}
            """
            
            contents_payload = [prompt_sistema]
            if uploaded_images:
                for img_file in uploaded_images:
                    img = Image.open(img_file)
                    img.thumbnail((500, 500)) 
                    contents_payload.append(img)

            respuesta_modelo = None
            for intento in range(3):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=contents_payload,
                    )
                    respuesta_modelo = response.text
                    break
                except Exception as e:
                    if intento == 2:
                        respuesta_modelo = f"⚠️ Alta demanda temporal. Por favor, reintentá. Detalle: {e}"
                    else:
                        time.sleep(1)

            st.markdown(respuesta_modelo)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_modelo})

            # --- GENERACIÓN DE PDF ---
            if respuesta_modelo and not "⚠️" in respuesta_modelo:
                class PDF(FPDF):
                    def header(self):
                        self.set_font("Arial", "B", 12)
                        self.cell(0, 10, "Informe Clínico - Óptica Zerzer", 0, 1, "C")
                        self.ln(5)

                pdf = PDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                
                texto_limpio = respuesta_modelo.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 6, texto_limpio)
                
                pdf_output_path = "informe_clinico_optometria.pdf"
                pdf.output(pdf_output_path)

                with open(pdf_output_path, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Descargar Informe en PDF para Imprimir",
                        data=pdf_file,
                        file_name="informe_optometrico.pdf",
                        mime="application/pdf"
                    )
