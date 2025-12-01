import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="🎄 Amigo Secreto 🎅", page_icon="🎁", layout="centered")

# --- ENLACE A TU GOOGLE SHEET ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/12tQaIKfalMhcKjv_Z6Ymw4rqdPY94GB6T6V2cyl4xC0/edit?usp=sharing"

# --- CSS PERSONALIZADO (MODO OSCURO TOTAL) ---
st.markdown("""
    <style>
    /* FONDO ROJO NAVIDEÑO */
    .stApp {
        background-color: #8B0000;
        background-image: url("https://www.transparenttextures.com/patterns/snow.png");
        background-size: auto;
    }
    
    /* CABECERA */
    .main-header {
        font-family: 'Helvetica Neue', sans-serif; 
        color: #FFFFFF; 
        text-align: center; 
        font-size: 3.5em; 
        font-weight: bold;
        text-shadow: 2px 2px 4px #000000;
        padding-bottom: 20px;
        margin-bottom: 20px;
        border-bottom: 2px dashed #FFFFFF;
    }

    /* TARJETAS DE ESTADO */
    .status-card {
        background-color: #2b2b2b;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        margin-bottom: 10px;
        border-left: 5px solid #1D6F42;
        color: #FFFFFF;
    }

    /* TARJETA DE RESULTADO */
    .secret-result {
        background-color: #2b2b2b;
        color: #ffffff;
        padding: 30px; 
        border-radius: 15px;
        text-align: center; 
        font-size: 1.8em;
        font-weight: bold; 
        margin-top: 20px;
        border: 2px dashed #D42426;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    
    /* FORZAR TODOS LOS TEXTOS DE LA UI A BLANCO */
    h1, h2, h3, h4, h5, h6, p, span, label, div, li, small {
        color: white !important;
    }

    /* --- CAMBIO SOLICITADO: INPUTS GRISES CON TEXTO BLANCO --- */
    
    /* Área de texto (Nombres) y Inputs (Contraseña) */
    .stTextArea textarea, .stTextInput input {
        background-color: #555555 !important; /* Fondo gris para el input */
        color: #FFFFFF !important;             /* Texto blanco al escribir */
        -webkit-text-fill-color: #FFFFFF !important;
        caret-color: #FFFFFF !important;       /* Cursor blanco */
        border: 1px solid #777 !important;
    }
    
    /* Selectbox (Menú desplegable) */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #555555 !important;
        color: white !important;
        border: 1px solid #777 !important;
    }
    
    /* El texto seleccionado dentro del selectbox */
    .stSelectbox div[data-baseweb="select"] span {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
    
    /* Opciones del menú desplegable (cuando se abre) */
    ul[data-baseweb="menu"] {
        background-color: #333333 !important;
    }
    
    /* --- FIN CAMBIO SOLICITADO --- */

    /* Corrección para expander */
    div[data-testid="stExpander"] details summary p, 
    div[data-testid="stExpander"] details summary svg {
        color: white !important;
        fill: white !important;
    }
    
    /* Botones Verdes */
    .stButton button {
        background-color: #1D6F42 !important;
        color: white !important;
        font-weight: bold;
        border: 1px solid #ffffff;
    }
    .stButton button:hover {
        background-color: #268c54 !important;
        border-color: #8B0000;
    }
    </style>
    
    <div class="main-header">🎅 Amigo Secreto 🎄</div>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        try:
            return conn.read(spreadsheet=SHEET_URL, worksheet="Hoja1", ttl=0)
        except:
            return conn.read(spreadsheet=SHEET_URL, worksheet="Hoja 1", ttl=0)
    except Exception:
        return pd.DataFrame(columns=["Participante", "Amigo", "Visto"])

def guardar_datos(df):
    try:
        conn.update(spreadsheet=SHEET_URL, worksheet="Hoja1", data=df)
    except:
        conn.update(spreadsheet=SHEET_URL, worksheet="Hoja 1", data=df)
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

# --- APP ---
df = cargar_datos()
juego_iniciado = not df.empty and "Participante" in df.columns and len(df) > 0

if not juego_iniciado:
    with st.container():
        st.markdown('<div style="background-color: rgba(40, 40, 40, 0.9); padding: 20px; border-radius: 10px; border: 1px solid #555;">', unsafe_allow_html=True)
        st.info("👋 Configuración del juego")
        
        st.markdown("<h3>🛠️ Crear Nuevo Sorteo</h3>", unsafe_allow_html=True)
        # El texto que escribas aquí ahora será BLANCO sobre fondo GRIS
        input_names = st.text_area(
            "Nombres (uno por línea):",
            height=150,
            placeholder="Juan\nMaría\nPedro"
        )
        
        if st.button("🎲 Sortear y Guardar", type="primary"):
            names_list = [n.strip() for n in input_names.replace(',', '\n').split('\n') if n.strip()]
            if len(names_list) < 3:
                st.error("Mínimo 3 personas.")
            elif len(names_list) != len(set(names_list)):
                st.error("Nombres duplicados.")
            else:
                with st.spinner("Sorteando..."):
                    nuevo_df = realizar_sorteo(names_list)
                    guardar_datos(nuevo_df)
                    st.success("¡Listo!")
                    time.sleep(1)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

else:
    participantes = df["Participante"].tolist()
    if df["Visto"].dtype == object:
        df["Visto"] = df["Visto"].map({'TRUE': True, 'FALSE': False, True: True, False: False})
    df["Visto"] = df["Visto"].fillna(False).astype(bool)
    estado_visto = dict(zip(df["Participante"], df["Visto"]))
    
    with st.container():
        st.markdown('<div style="background-color: rgba(40, 40, 40, 0.95); padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid #555;">', unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center;'>🔍 Descubre tu Amigo Secreto</h3>", unsafe_allow_html=True)
        
        usuario = st.selectbox("👇 Busca tu nombre:", ["Elige tu nombre..."] + participantes)

        if usuario != "Elige tu nombre...":
            fila_usuario = df[df["Participante"] == usuario].iloc[0]
            ya_lo_vio = bool(fila_usuario["Visto"])
            
            if ya_lo_vio:
                st.warning(f"⚠️ {usuario}, ya has visto tu amigo secreto.")
            else:
                st.info("Solo puedes verlo una vez.")
                if st.button(f"🎁 ¡ABRIR MI REGALO!", use_container_width=True):
                    amigo_secreto = fila_usuario["Amigo"]
                    idx = df.index[df["Participante"] == usuario].tolist()[0]
                    df.at[idx, "Visto"] = True
                    guardar_datos(df)
                    st.balloons()
                    st.markdown(f"""
                    <div class="secret-result">
                        🤫 Tu Amigo Secreto es:<br><br>
                        <span style="font-size: 2.5em; color: #00ff00; text-shadow: 0px 0px 10px #00ff00;">✨ {amigo_secreto} ✨</span>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    st.subheader("📊 ¿Quiénes faltan?")
    
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, (nombre, visto) in enumerate(estado_visto.items()):
        c = cols[i % 3]
        icon = "✅" if visto else "⏳"
        color_borde = "#00ff00" if visto else "#ffffff"
        status = "Listo" if visto else "Pendiente"
        
        c.markdown(f"""
        <div class="status-card" style="border-left: 5px solid {color_borde};">
            <strong>{nombre}</strong><br>
            <span>{icon} {status}</span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("⚙️ Administrar / Borrar Todo"):
        st.markdown("<p style='color: white;'>⚠️ <strong>Zona de peligro:</strong> Esto borrará todos los datos.</p>", unsafe_allow_html=True)
        # El texto que escribas aquí ahora será BLANCO sobre fondo GRIS
        pass_check = st.text_input("Escribe 'BORRAR' para confirmar:", key="reset_pass")
        if st.button("🗑️ Reiniciar Sorteo"):
            if pass_check == "BORRAR": 
                df_vacio = pd.DataFrame(columns=["Participante", "Amigo", "Visto"])
                guardar_datos(df_vacio)
                st.success("Borrado.")
                time.sleep(1)
                st.rerun()
