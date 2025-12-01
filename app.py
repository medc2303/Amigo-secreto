import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="🎄 Amigo Secreto Remoto 🎅", page_icon="🎁")

# --- ENLACE A TU GOOGLE SHEET ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/12tQaIKfalMhcKjv_Z6Ymw4rqdPY94GB6T6V2cyl4xC0/edit?usp=sharing"

# --- CSS NAVIDEÑO ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif; 
        color: #D42426; text-align: center; 
        font-size: 3em; font-weight: bold;
        text-shadow: 2px 2px 4px #00000020;
    }
    .status-card {
        background-color: white; padding: 15px;
        border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px; border-left: 5px solid #1D6F42;
    }
    .secret-result {
        background-color: #ffcccb; color: #8b0000;
        padding: 20px; border-radius: 10px;
        text-align: center; font-size: 1.5em;
        font-weight: bold; margin-top: 20px;
        border: 2px dashed #D42426;
    }
    </style>
    <div class="main-header">🎅 Amigo Secreto Remoto 🎄</div>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    """Carga los datos asegurando que no usa caché vieja (ttl=0)"""
    try:
        # Usamos explícitamente tu URL aquí
        return conn.read(spreadsheet=SHEET_URL, worksheet="Hoja1", ttl=0)
    except Exception:
        return pd.DataFrame(columns=["Participante", "Amigo", "Visto"])

def guardar_datos(df):
    """Escribe los datos en la hoja de cálculo específica"""
    conn.update(spreadsheet=SHEET_URL, worksheet="Hoja1", data=df)
    st.cache_data.clear()

def realizar_sorteo(names):
    givers = names.copy()
    receivers = names.copy()
    while True:
        random.shuffle(receivers)
        if not any(g == r for g, r in zip(givers, receivers)):
            break
    
    df = pd.DataFrame({
        "Participante": givers,
        "Amigo": receivers,
        "Visto": [False] * len(givers)
    })
    return df

# --- LÓGICA PRINCIPAL ---
df = cargar_datos()

# Verificamos si ya hay un juego creado
juego_iniciado = not df.empty and "Participante" in df.columns and len(df) > 0

if not juego_iniciado:
    st.info("👋 No hay un sorteo activo en esta hoja. Configura uno nuevo abajo.")
    
    with st.expander("🛠️ Zona de Administrador (Crear Sorteo)", expanded=True):
        input_names = st.text_area(
            "Nombres de los participantes (uno por línea):",
            height=150,
            placeholder="Juan\nMaría\nPedro"
        )
        
        if st.button("🎲 Sortear y Guardar en la Nube", type="primary"):
            names_list = [n.strip() for n in input_names.replace(',', '\n').split('\n') if n.strip()]
            
            if len(names_list) < 3:
                st.error("Mínimo 3 personas.")
            elif len(names_list) != len(set(names_list)):
                st.error("Nombres duplicados.")
            else:
                with st.spinner("Conectando con tu Google Sheet..."):
                    nuevo_df = realizar_sorteo(names_list)
                    guardar_datos(nuevo_df)
                    st.success("¡Sorteo guardado! Recarga la página.")
                    time.sleep(2)
                    st.rerun()

else:
    st.write("---")
    
    # 1. Selector de usuario
    participantes = df["Participante"].tolist()
    # Mapeo seguro de booleanos para evitar errores de lectura
    df["Visto"] = df["Visto"].astype(bool)
    estado_visto = dict(zip(df["Participante"], df["Visto"]))
    
    st.subheader("🔍 Descubre tu Amigo Secreto")
    usuario = st.selectbox("Selecciona tu nombre:", ["Elige..."] + participantes)

    if usuario != "Elige...":
        fila_usuario = df[df["Participante"] == usuario].iloc[0]
        ya_lo_vio = bool(fila_usuario["Visto"])
        
        if ya_lo_vio:
            st.warning(f"⚠️ {usuario}, ya has visto tu amigo secreto.")
        else:
            st.info("Presiona el botón para revelar. Solo podrás hacerlo una vez.")
            if st.button(f"🎁 Revelar a quién me toca"):
                amigo_secreto = fila_usuario["Amigo"]
                
                # Actualizar base de datos
                idx = df.index[df["Participante"] == usuario].tolist()[0]
                df.at[idx, "Visto"] = True
                guardar_datos(df)
                
                st.balloons()
                st.markdown(f"""
                <div class="secret-result">
                    🤫 Tu Amigo Secreto es:<br>
                    <span style="font-size: 2.5em; color: #1D6F42;">✨ {amigo_secreto} ✨</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.warning("⚠️ Guarda este nombre. No podrás verlo de nuevo.")

    # 2. Tabla de Estado
    st.write("---")
    st.subheader("📊 Estado del Grupo")
    
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, (nombre, visto) in enumerate(estado_visto.items()):
        c = cols[i % 3]
        icon = "✅" if visto else "⏳"
        color = "#e6fffa" if visto else "white"
        status = "Listo" if visto else "Pendiente"
        
        c.markdown(f"""
        <div class="status-card" style="background-color: {color};">
            <strong>{nombre}</strong><br>
            {icon} {status}
        </div>
        """, unsafe_allow_html=True)

    # 3. Reinicio
    with st.expander("⚙️ Administrar / Reiniciar"):
        st.write("Zona peligrosa: Borrar todo.")
        pass_check = st.text_input("Escribe 'BORRAR' para confirmar:", key="reset_pass")
        if st.button("🗑️ Reiniciar Base de Datos"):
            if pass_check == "BORRAR": 
                df_vacio = pd.DataFrame(columns=["Participante", "Amigo", "Visto"])
                guardar_datos(df_vacio)
                st.success("Base de datos reiniciada.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Escribe BORRAR en el campo de texto.")
