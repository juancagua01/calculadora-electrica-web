import streamlit as st
from PIL import Image 

# Configuración de la página
st.set_page_config(page_title="Calculadora Eléctrica Pro", page_icon="⚡", layout="centered")

# --- Función para obtener calibre (sin cambios) ---
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

# --- IMAGEN LATERAL (Sidebar) ---
# Colocamos una imagen en la barra lateral
with st.sidebar:
    st.image("logo_lateral.png", caption="", use_column_width=True)
    st.markdown("---") # Separador visual en la sidebar
    st.write("Calculadora Profesional para Electricistas")
    st.write("Versión 1.0")


# --- Título y Imagen Superior Derecha (en columnas) ---
col_titulo, col_imagen_sup = st.columns([0.7, 0.3]) # Proporción para el título y la imagen

with col_titulo:
    st.title("⚡ Calculadora de Carga y Protecciones")
    st.markdown("Cálculo basado en corriente nominal ")

with col_imagen_sup:
    st.image("icono_superior.png", width=200, caption="") # Ajusta el width a tu gusto

st.markdown("---") # Separador visual principal

# Inicializar lista de equipos (sin cambios)
if 'equipos' not in st.session_state:
    st.session_state.equipos = []

# --- Formulario de Entrada (sin cambios) ---
with st.expander("➕ Agregar Nuevo Equipo", expanded=True):
    with st.form("nuevo_equipo", clear_on_submit=True):
        nombre = st.text_input("Descripción del equipo", placeholder="Ej: Motor Bomba")

        col1, col2, col3 = st.columns(3)
        with col1:
            voltaje = st.number_input("Voltaje (V)", min_value=1, value=120)
        with col2:
            unidad = st.selectbox("Unidad", ["Watts (W)", "HP"])
        with col3:
            potencia = st.number_input("Potencia", min_value=0.01)

        col_a, col_b = st.columns(2)
        with col_a:
            es_continua = st.checkbox("Carga Continua ")
        with col_b:
            eficiencia = st.slider("Eficiencia (solo para HP)", 50, 100, 85) / 100

        btn_agregar = st.form_submit_button("Agregar a la lista")

        if btn_agregar:
            if unidad == "HP":
                watts_reales = (potencia * 746) / eficiencia
            else:
                watts_reales = potencia

            corriente_base = watts_reales / voltaje
            corriente_final = corriente_base * 1.25 if es_continua or unidad == "HP" else corriente_base

            st.session_state.equipos.append({
                "nombre": nombre if nombre else "Equipo Genérico",
                "watts": watts_reales,
                "amperios": corriente_final,
                "unidad_orig": f"{potencia} {unidad}"
            })

# --- Mostrar Tabla de Equipos (sin cambios) ---
if st.session_state.equipos:
    st.subheader("📋 Detalle del Circuito")

    for i, eq in enumerate(st.session_state.equipos):
        st.write(f"**{i+1}. {eq['nombre']}** | {eq['unidad_orig']} | Corriente calculada: `{eq['amperios']:.2f} A`")

    st.markdown("---")

    # Métricas principales (sin cambios)
    total_a = sum(e['amperios'] for e in st.session_state.equipos)
    breakers = [15, 20, 30, 40, 50, 60, 70, 80, 100, 125, 150, 175, 200]
    breaker_sugerido = next((b for b in breakers if b >= total_a), "Excede 200A")

    c1, c2, c3 = st.columns(3)
    c1.metric("Carga Total", f"{total_a:.2f} A")
    c2.metric("Breaker", f"{breaker_sugerido} A")
    c3.metric("Cable Sugerido", obtener_calibre(total_a))

    # --- Generar Reporte para Descarga (sin cambios) ---
    resumen_txt = f"REPORTE TÉCNICO ELÉCTRICO\n"
    resumen_txt += "="*30 + "\n"
    for eq in st.session_state.equipos:
        resumen_txt += f"- {eq['nombre']}: {eq['amperios']:.2f} A\n"
    resumen_txt += "="*30 + "\n"
    resumen_txt += f"TOTAL AMPERIOS: {total_a:.2f} A\n"
    resumen_txt += f"BREAKER RECOMENDADO: {breaker_sugerido} A\n"
    resumen_txt += f"CABLE RECOMENDADO: {obtener_calibre(total_a)}\n"

    st.download_button(
        label="📥 Descargar Reporte (TXT)",
        data=resumen_txt,
        file_name="memoria_tecnica.txt",
        mime="text/plain"
    )

    if st.button("🗑️ Borrar Todo"):
        st.session_state.equipos = []
        st.rerun()

else:
    st.info("Agregue su primer equipo para comenzar el cálculo.")