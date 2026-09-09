
               import os
import time
import streamlit as st
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from google import genai
from PIL import Image
from fpdf import FPDF
from io import BytesIO

st.set_page_config(
    page_title="Asistente Clínico de Optometría Avanzada",
    page_icon="👁️‍🗨️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🔒 BLINDAJE Y PROTECCIÓN INTELECTUAL (CSS)
# ==========================================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {
        width: 100%;
        background-color: #0d6efd;
        color: white;
        font-weight: bold;
        border-radius: 6px;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔒 SISTEMA DE ACCESO PRIVADO (CONTRASEÑA)
# ==========================================
CONTRASENIA_VALIDA = "zerzer2026"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔐 Óptica Zerzer - Acceso Colegas")
        st.info("Sistema exclusivo para profesionales suscriptores. Ingrese su contraseña mensual.")
        
        input_pass = st.text_input("Contraseña de acceso:", type="password")
        if st.button("Ingresar al Sistema"):
            if input_pass == CONTRASENIA_VALIDA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta. Verifique sus datos.")
    st.stop()

# ==========================================
# 🛠️ PANEL LATERAL Y NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/experimental-optometry-color.png", width=60)
    st.title("Óptica Zerzer")
    st.markdown("*Asistente Clínico Profesional*")
    
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
        "📷 Subir imágenes clínicas (Máx. 2)", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True,
        help="Subí hasta 2 imágenes clave de topografía o córnea."
    )
    
    if uploaded_images and len(uploaded_images) > 2:
        st.warning("⚠️ Máximo 2 fotos permitidas.")
        uploaded_images = uploaded_images[:2]
    
    paciente_info = st.text_area(
        "📝 Datos cuantitativos / Caso clínico:",
        placeholder="Ej: K1: 44.00 @ 90, K2: 47.50 @ 180...",
        height=140
    )
    st.markdown("---")
    st.caption("© Óptica Zerzer - Propiedad Protegida")

# ==========================================
# CUERPO PRINCIPAL
# ==========================================
st.title("👁️‍🗨️ Panel de Resolución de Casos Clínicos")

st.info(
    "💡 **Nota sobre el análisis de imágenes clínicas:**\n\n"
    "Para garantizar un diagnóstico de alta precisión basado exclusivamente en la bibliografía de la solapa activa, "
    "el sistema demanda entre **2 a 3 minutos** de procesamiento profundo. ¡Agradecemos su paciencia!",
    icon="⏱️"
)

api_key = api_key_input if api_key_input else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ Por favor, ingresá tu Gemini API Key en la barra lateral para comenzar.")
    st.stop()

# Inicialización correcta del cliente de Gemini
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
        with st.spinner("🔍 Analizando mapas topográficos y contrastando con literatura científica (2-3 minutos)..."):
            
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
                    # Corrección clave para la SDK moderna de google-genai
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

            # --- GENERACIÓN DE PDF Y DESCARGA ---
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
                        file_name="informe_optometrico_zerzer.pdf",
                        mime="application/pdf"
                    )
