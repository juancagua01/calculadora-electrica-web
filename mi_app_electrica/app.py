import streamlit as st
from PIL import Image
import os
from fpdf import FPDF

# 1. Configuración de la página
st.set_page_config(page_title="Calculadora Eléctrica Pro", page_icon="⚡", layout="centered")

# --- Función para obtener calibre ---
def obtener_calibre(amperios):
    if amperios <= 15: return "14 AWG"
    elif amperios <= 20: return "12 AWG"
    elif amperios <= 30: return "10 AWG"
    elif amperios <= 55: return "8 AWG"
    elif amperios <= 75: return "6 AWG"
    elif amperios <= 95: return "4 AWG"
    elif amperios <= 115: return "3 AWG"
    elif amperios <= 130: return "2 AWG"
    else: return "Consultar Tablas Especiales (> 2 AWG)"

# --- Función para generar el PDF con CORRECCIÓN DE IMAGEN ---
def generar_pdf(equipos, total_a, breaker, cable):
    pdf = FPDF()
    pdf.add_page()
    
    # PROCESAMIENTO SEGURO DEL LOGO
    if os.path.exists("logo_lateral.png"):
        try:
            # Convertimos la imagen a un formato compatible (RGB) para evitar errores de PNG
            img = Image.open("logo_lateral.png").convert("RGB")
            temp_path = "temp_logo_pdf.png"
            img.save(temp_path)
            
            # x=80 para centrar en A4
            pdf.image(temp_path, x=80, y=10, w=50)
            pdf.ln(45)
        except Exception as e:
            st.warning(f"Aviso: El logo no se incluyó en el PDF por compatibilidad: {e}")
            pdf.ln(10)
    
    pdf.set_font("Arial", "B", 16)
    # Usamos un codificado seguro para evitar errores con acentos o la 'ñ'
    pdf.cell(200, 10, txt="MEMORIA TÉCNICA ELÉCTRICA".encode('latin-1', 'ignore').decode('latin-1'), ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Detalle de Cargas:".encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.set_font("Arial", size=11)
    
    for i, eq in enumerate(equipos):
        txt_eq = f"{i+1}. {eq['nombre']} | Potencia: {eq['unidad_orig']} | Corriente: {eq['amperios']:.2f} A"
        pdf.cell(200, 8, txt=txt_eq.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="RESULTADOS DEL CÁLCULO:".encode('latin-1', 'ignore').decode('latin-1'), ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, txt=f"Corriente Total Requerida: {total_a:.2f} A", ln=True)
    pdf.cell(200, 8, txt=f"Capacidad del Breaker: {breaker} A", ln=True)
    pdf.cell(200, 8, txt=f"Calibre del Conductor Sugerido: {cable}", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

# --- BARRA LATERAL (Sidebar) ---
with st.sidebar:
    if os.path.exists("logo_lateral.png"):
        st.image("logo_lateral.png", use_container_width=True)
    st.markdown("---")
    st.write("Calculadora Profesional para Electricistas")
    st.info("Versión 1.1 - PDF Fix")

# --- Título y Imagen Superior Derecha ---
col_titulo, col_imagen_sup = st.columns([0.7, 0.3])

with col_titulo:
    st.title("⚡ Calculadora de Carga y Protecciones")
    st.markdown("Cálculo técnico basado en capacidad de conducción.")

with col_imagen_sup:
    if os.path.exists("icono_superior.png"):
        st.image("icono_superior.png", width=250)

st.markdown("---")

if 'equipos' not in st.session_state:
    st.session_state.equipos = []

# --- Formulario de Entrada ---
with st.expander("➕ Agregar Nuevo Equipo", expanded=True):
    with st.form("nuevo_equipo", clear_on_submit=True):
        nombre = st.text_input("Descripción del equipo", placeholder="Ej: Aire Acondicionado")
        col1, col2, col3 = st.columns(3)
        with col1:
            voltaje = st.number_input("Voltaje (V)", min_value=1.0, value=120.0)
        with col2:
            unidad = st.selectbox("Unidad", ["Watts (W)", "HP"])
        with col3:
            potencia = st.number_input("Potencia", min_value=1.0)

        col_a, col_b = st.columns(2)
        with col_a:
            es_continua = st.checkbox("Carga Continua (>3 horas)")
        with col_b:
            eficiencia = st.slider("Eficiencia del Motor (%)", 50, 100, 85) / 100

        if st.form_submit_button("Agregar a la lista"):
            watts_reales = (potencia * 746) / eficiencia if unidad == "HP" else potencia
            corriente_base = watts_reales / voltaje
            corriente_final = corriente_base * 1.25 if es_continua or unidad == "HP" else corriente_base

            st.session_state.equipos.append({
                "nombre": nombre if nombre else "Equipo Genérico",
                "amperios": corriente_final,
                "unidad_orig": f"{potencia} {unidad}"
            })

# --- Resultados y Tabla ---
if st.session_state.equipos:
    st.subheader("📋 Resumen del Cálculo")
    for i, eq in enumerate(st.session_state.equipos):
        st.write(f"**{i+1}. {eq['nombre']}** ({eq['unidad_orig']}) → `{eq['amperios']:.2f} A`")

    st.markdown("---")

    total_a = sum(e['amperios'] for e in st.session_state.equipos)
    breakers = [15, 20, 30, 40, 50, 60, 70, 80, 100, 125, 150, 175, 200]
    breaker_sugerido = next((b for b in breakers if b >= total_a), "Excede 200A")
    cable_sugerido = obtener_calibre(total_a)

    c1, c2, c3 = st.columns(3)
    c1.metric("Carga Total", f"{total_a:.2f} A")
    c2.metric("Breaker", f"{breaker_sugerido} A")
    c3.metric("Cable AWG", cable_sugerido)

    st.markdown("---")
    
    col_pdf, col_reset = st.columns(2)
    
    with col_pdf:
        try:
            pdf_bytes = generar_pdf(st.session_state.equipos, total_a, breaker_sugerido, cable_sugerido)
            st.download_button(
                label="📄 Descargar Reporte en PDF",
                data=pdf_bytes,
                file_name="Memoria_Tecnica_Electrica.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error crítico al generar el archivo: {e}")

    with col_reset:
        if st.button("🗑️ Limpiar Lista"):
            st.session_state.equipos = []
            st.rerun()
else:
    st.info("La lista está vacía.")