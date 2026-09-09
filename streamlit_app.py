import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Asistente Clínico Optométrico",
    page_icon="👁️",
    layout="centered"
)

# Contraseña de acceso mensual (puedes cambiarla cuando gustes)
CLAVE_ACCESO = "OPTICA2026"

def validar_acceso():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.subheader("🔒 Asistente Clínico Optométrico")
        st.write("Herramienta de consulta y rigor científico para tu gabinete")
        
        password = st.text_input("Ingresá tu contraseña de acceso mensual:", type="password")
        
        if st.button("Ingresar"):
            if password == CLAVE_ACCESO:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta. Verificá los datos.")
        return False
    return True

# Ejecutar validación de seguridad
if validar_acceso():
    st.title("👁️ Asistente Clínico Optométrico")
    st.write("Herramienta de consulta y rigor científico para tu gabinete")

    st.markdown("---")

    # Selección de categorías correspondientes a las carpetas de la biblioteca
    opcion = st.selectbox(
        "Seleccioná el tipo de análisis:",
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

    if st.button("Generar Análisis Clínico"):
        st.success(f"Cargando protocolos y documentación para la sección: **{opcion}**...")
        # Acá se procesarían los documentos de la carpeta correspondiente
