import streamlit as st

st.set_page_config(
    page_title="Asistente Clínico Optométrico",
    page_icon="👁️",
    layout="centered",
)

st.title("👁️ Asistente Clínico Optométrico")
st.markdown("### Herramienta de consulta y rigor científico para tu gabinete")

clave_ingresada = st.text_input(
    "Ingresá tu contraseña de acceso mensual:", type="password"
)
CLAVE_VALIDA = "zerzer2026"

if clave_ingresada == CLAVE_VALIDA:
    st.success("¡Acceso autorizado! Bienvenido colega.")
    st.markdown("---")
    st.markdown("#### 📚 Consulta de Casos y Protocolos")

    tipo_caso = st.selectbox(
        "Seleccioná el tipo de análisis:",
        [
            "Topografía compleja / Queratocono",
            "Adaptación de Lentes Rígidas (RGP)",
            "Baja Visión y Terapia Visual",
        ],
    )

    consulta = st.text_area(
        "Describí los valores, parámetros o dudas del caso clínico:"
    )

    if st.button("Generar Análisis Clínico"):
        if consulta:
            st.info(
                "Analizando parámetros bibliográficos y criterios de adaptación..."
            )
            st.markdown(
                "**Criterio sugerido:** Basado en la bibliografía avanzada de adaptación en córneas irregulares, se recomienda priorizar el control de la sagital y evaluar el apoyo en la zona intermedia para evitar marcas epiteliales."
            )
        else:
            st.warning("Por favor, ingresa los datos del caso.")

elif clave_ingresada:
    st.error(
        "Contraseña incorrecta o membresía vencida. Recordá verificar tu pago por WhatsApp."
    )
else:
    st.info("Por favor, introduce tu contraseña para habilitar las consultas.")
