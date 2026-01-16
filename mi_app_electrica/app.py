import streamlit as st

st.set_page_config(page_title="Calculadora Eléctrica", page_icon="⚡")

st.title("⚡ Calculadora de Protecciones")
st.markdown("---")

# Inicializar la lista de equipos en la sesión
if 'equipos' not in st.session_state:
    st.session_state.equipos = []

# Formulario de entrada
with st.form("nuevo_equipo"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre del equipo", placeholder="Ej: Aire Acondicionado")
        voltaje = st.number_input("Voltaje (V)", min_value=1.0, value=120.0)
    with col2:
        unidad = st.selectbox("Unidad", ["Watts", "HP"])
        potencia = st.number_input("Valor de Potencia", min_value=0.0)
    
    es_continua = st.checkbox("¿Es carga continua? (>3 horas)")
    btn_agregar = st.form_submit_button("Agregar Equipo")

    if btn_agregar:
        watts_reales = potencia * 746 if unidad == "HP" else potencia
        corriente_base = watts_reales / voltaje
        corriente_final = corriente_base * 1.25 if es_continua else corriente_base
        
        st.session_state.equipos.append({
            "nombre": nombre,
            "amperios": corriente_final,
            "desc": f"{nombre} ({potencia} {unidad})"
        })

# Mostrar lista de equipos
if st.session_state.equipos:
    st.subheader("Equipos agregados:")
    for i, eq in enumerate(st.session_state.equipos):
        st.write(f"✅ {eq['desc']} -> **{eq['amperios']:.2f} A**")

    # Cálculos finales
    total_a = sum(e['amperios'] for e in st.session_state.equipos)
    breakers = [15, 20, 30, 40, 50, 60, 70, 80, 100, 125, 150]
    breaker_sugerido = next((b for b in breakers if b >= total_a), "Excede 150A")

    st.markdown("---")
    st.metric(label="Corriente Total Requerida", value=f"{total_a:.2f} A")
    st.success(f"### 🛡️ Breaker Recomendado: {breaker_sugerido}A")

    if st.button("Limpiar lista"):
        st.session_state.equipos = []
        st.rerun()