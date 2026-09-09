import os
import time
import streamlit as st
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from google import genai
from PIL import Image
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

# Contraseña de acceso mensual
CLAVE_ACCESO = "optica2026"

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
        
        # Opción para cerrar sesión si se requiere
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

        api_key_input = st.text_input("🔑 Gemini API Key", type="password", help="Ingresá tu clave de API para procesar con IA.")
        
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
        
        # Subida de imágenes (topografía, córnea, etc. - Máximo 2)
        imagenes_subidas = st.file_uploader(
            "Subir imágenes (ej. Topografía corneal - Máx 2)", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
        
        if imagenes_subidas and len(imagenes_subidas) > 2:
            st.warning("⚠️ Máximo 2 fotos permitidas.")
            imagenes_subidas = imagenes_subidas[:2]
        
        # Subida de texto clínico
        caso_texto = st.text_area(
            "Detalle del caso clínico y parámetros:",
            placeholder="Ej: K1 43.00 @ 90, K2 46.50 @ 180. Agudeza visual, síntomas...",
            height=120
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        boton_analizar = st.button("🚀 Generar Análisis Clínico Profundo")
        
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
            el sistema demanda <b>entre 2 y 3 minutos</b> de pensamiento profundo. Agradecemos su espera para ofrecerle un reporte impecable.
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("---")

    # Configuración de API Key
    api_key = api_key_input if api_key_input else os.environ.get("GEMINI_API_KEY")

    # Inicialización de motor ChromaDB local (con manejo seguro si no existe la carpeta aún)
    @st.cache_resource
    def obtener_motor_chroma():
        try:
            chroma_client = chromadb.PersistentClient(path="./base_datos_optometria")
            emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            return chroma_client, emb_fn
        except Exception:
            return None, None

    chroma_client, emb_fn = obtener_motor_chroma()

    # Mapeo exacto de colecciones según la solapa elegida (aisladas para que la app sea rápida)
    mapeo_colecciones = {
        "Topografía compleja / Queratocono": "colleccion_topografia",
        "Adaptación de Lentes Rígidas (RGP)": "colleccion_rigidas",
        "Baja Visión": "colleccion_baja_vision",
        "General y Clínica": "colleccion_general",
        "Neurología": "colleccion_neurologia",
        "Pediatría": "colleccion_pediatria",
        "Terapia Visual": "colleccion_terapia"
    }

    # -------------------------------------------------------------
    # LÓGICA DE PROCESAMIENTO CON INTELIGENCIA ARTIFICIAL PROFUNDA
    # -------------------------------------------------------------
    if boton_analizar:
        if not api_key:
            st.warning("⚠️ Por favor, ingresá tu Gemini API Key en la barra lateral para permitir que la app procese el caso.")
        elif not imagenes_subidas and not caso_texto.strip():
            st.warning("⚠️ Por favor, subí al menos una imagen o completá los datos del caso clínico en texto.")
        else:
            with st.spinner(f"🔍 [Proceso Profundo] Analizando base bibliográfica específica para [{categoria}], cruzando topografías y evaluando parámetros (Aprox. 2-3 min)..."):
                
                # 1. Búsqueda en la colección vectorial correspondiente (Aislamiento por solapa)
                contexto = "Sin contexto específico adicional en la base local."
                if chroma_client and emb_fn:
                    try:
                        nombre_col = mapeo_colecciones.get(categoria, "colleccion_general")
                        coleccion_activa = chroma_client.get_or_create_collection(name=nombre_col, embedding_function=emb_fn)
                        resultados = coleccion_activa.query(query_texts=[caso_texto if caso_texto else "Análisis general de imágenes"], n_results=1)
                        documentos = resultados.get("documents", [[]])[0]
                        if documentos:
                            contexto = "\n\n".join(documentos)
                    except Exception:
                        contexto = "Base de datos local en inicialización estándar."

                # 2. Construcción del Prompt Experto y Riguroso
                prompt_sistema = f"""
                Actúa como un profesor universitario de optometría de máxima jerarquía internacional y optómetra clínico especialista.
                Tu tarea es realizar un análisis exhaustivo, altamente detallado, estructurado y de rigor clínico absoluto para un colega profesional.

                Área Clínica Seleccionada: {categoria}
                Parámetros y Datos Ingresados por el Colega: {caso_texto}
                Literatura Científica de Referencia (Exclusiva de esta solapa): {contexto}

                Estructura obligatoria y detallada que debe contener tu respuesta:
                1. 📋 **Resumen y Evaluación del Caso Clínico**: Análisis pormenorizado de los datos cuantitativos y cualitativos aportados.
                2. 🔍 **Diagnóstico Diferencial y Biomecánica Ocular**: Interpretación profunda del problema visual, estado corneal, excentricidades o anomalías detectadas según las imágenes y valores.
                3. 🛠️ **Opciones de Solución Terapéutica y Plan de Abordaje**:
                   - Opción Primaria / Ideal (Parámetros exactos sugeridos, diseños, materiales o pautas de trabajo).
                   - Opción Alternativa o de Respaldo.
                4. 📅 **Control, Seguimiento y Pronóstico en Gabinete**: Pautas clave para la evaluación del paciente a corto y mediano plazo.

                Sé sumamente claro, técnico, profesional y profundo. Evita respuestas superficiales.
                """

                # 3. Preparación de contenidos (Texto + Imágenes adjuntas)
                contents_payload = [prompt_sistema]
                if imagenes_subidas:
                    for img_file in imagenes_subidas:
                        img = Image.open(img_file)
                        img.thumbnail((800, 800)) # Optimización de tamaño para el motor
                        contents_payload.append(img)

                # 4. Invocación al modelo con reintentos para garantizar estabilidad
                client = genai.Client(api_key=api_key)
                respuesta_modelo = None
                
                for intento in range(3):
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash', # o el modelo activo configurado
                            contents=contents_payload,
                        )
                        respuesta_modelo = response.text
                        break
                    except Exception as e:
                        if intento == 2:
                            respuesta_modelo = f"⚠️ Ocurrió un inconveniente temporal al procesar la alta demanda con el motor de IA. Por favor, reintentá en unos segundos. Detalle técnico: {e}"
                        else:
                            time.sleep(2)

            if respuesta_modelo and not "⚠️" in respuesta_modelo:
                st.success("✅ ¡Análisis Clínico Generado con Éxito!")
                
                # Enmarcar el reporte oficial
                resultado_markdown = f"""
### 📋 Reporte Clínico Oficial - Óptica Zerzer
* **Área Evaluada:** {categoria}
* **Validación de Sesión:** Activa (Colega Autorizado)

---
{respuesta_modelo}
---
*Aviso legal: Este reporte es una herramienta de asistencia profesional generada por el Asistente Clínico de Óptica Zerzer. Queda prohibida la reproducción total o parcial de la metodología, bases de datos y estructura de esta plataforma.*
                """
                
                st.markdown(resultado_markdown)
                
                # -------------------------------------------------------------
                # BOTÓN DE DESCARGA DE REPORTE
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
            else:
                st.error(respuesta_modelo)
