import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="🎄 Amigo Secreto 🎅", page_icon="🎁", layout="centered")

# --- ENLACE A TU GOOGLE SHEET ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/12tQaIKfalMhcKjv_Z6Ymw4rqdPY94GB6T6V2cyl4xC0/edit?usp=sharing"

# --- CSS: MODO OSCURO FORZADO AGRESIVO ---
st.markdown("""
    <style>
    /* 1. FORZAR FONDO Y TEXTO GLOBAL */
    .stApp {
        background-color: #8B0000; /* Rojo Navideño */
        background-image: url("https://www.transparenttextures.com/patterns/snow.png");
        color: white !important;
    }
    
    /* 2. FORZAR TODOS LOS TEXTOS A BLANCO (Títulos, párrafos, etiquetas) */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, small, strong {
        color: #FFFFFF !important;
    }
    
    /* 3. INPUTS Y TEXTAREAS (Donde escribes nombres) */
    /* Forzamos el fondo gris oscuro y texto blanco */
    .stTextInput input, .stTextArea textarea {
        background-color: #333333 !important; 
        color: white !important;
        border: 1px solid #555 !important;
    }
    /* El placeholder (texto de ayuda) un poco más gris */
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #cccccc !important;
    }

    /* 4. SELECTBOX (Menú desplegable) - EL MÁS DIFÍCIL */
    /* La caja cerrada */
    div[data-baseweb="select"] > div {
        background-color: #333333 !important;
        color: white !important;
        border-color: #555 !important;
    }
    /* El texto seleccionado */
    div[data-baseweb="select"] span {
        color: white !important;
    }
    /* El ícono de la flechita */
    div[data-baseweb="select"] svg {
        fill: white !important;
    }
    
    /* EL MENÚ DESPLEGABLE (Cuando le das clic) */
    /* Fondo del menú flotante */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul {
        background-color: #222222 !important;
    }
    /* Las opciones de la lista */
    li[id^="bui-"] {
        color: white !important; 
    }
    /* Opción al pasar el mouse (hover) */
    li[aria-selected="false"]:hover {
        background-color: #444444 !important;
    }
    
    /* 5. TARJETAS PERSONALIZADAS */
    .status-card {
        background-color: #2b2b2b !important;
        border: 1px solid #444;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #1D6F42;
        color: white !important;
    }

    .secret-result {
        background-color: #2b2b2b !important;
        border: 2px dashed #D42426;
        padding: 30px; 
        border-radius: 15px;
        text-align: center;
        color: white !important; 
    }

    /* 6. BOTONES */
    .stButton button {
        background-color: #1D6F42 !important;
        color: white !important;
        border: 1px solid white !important;
    }
    
    /* 7. EXPANDER (Sección borrar) */
    div[data-testid="stExpander"] {
        background-color: #2b2b2b !important;
        border: 1px solid #444;
        color: white !important;
    }
    div[data-testid="stExpander"] p {
        color: white !important;
    }
    div[data-testid="stExpander"] svg {
        fill: white !important;
    }
    
    /* CABECERA */
    .main-header {
        font-family: 'Helvetica Neue', sans-serif; 
        color: #FFFFFF !important; 
        text-align: center; 
        font-size: 3.5em; 
        font-weight: bold;
        text-shadow: 2px 2px 4px #000000;
        padding-bottom: 20px;
        margin-bottom: 20px;
        border-bottom: 2px dashed #FFFFFF;
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
    """
    Sorteo con truco: Flores -> Lucho siempre.
    """
    givers = names.copy()
    receivers = names.copy()
    assignment = {}

    # --- LÓGICA TRUCADA ---
    # Buscamos "Flores" y "Lucho" (quitamos espacios extra por si acaso)
    # Convertimos a lista limpia para comparar
    
    # Verificamos si ambos están en la lista (búsqueda exacta)
    if "Flores" in names and "Lucho" in names:
        # Asignación forzada
        assignment["Flores"] = "Lucho"
        
        # Los sacamos de las bolsas
        givers.remove("Flores")
        receivers.remove("Lucho")
    
    # --- SORTEO DEL RESTO ---
    while True:
        random.shuffle(receivers)
        
        # Verificamos conflictos
        conflict = False
        for g, r in zip(givers, receivers):
            if g == r:
                conflict = True
                break
        
        if not conflict:
            break
            
    # Agregamos los resultados
    for g, r in zip(givers, receivers):
        assignment[g] = r
        
    df = pd.DataFrame(list(assignment.items()), columns=["Participante", "Amigo"])
    df["Visto"] = [False] * len(df)
    return df

# --- APP LÓGICA ---
df = cargar_datos()
juego_iniciado = not df.empty and "Participante" in df.columns and len(df) > 0

if not juego_iniciado:
    with st.container():
        # Fondo oscuro manual para contenedor
        st.markdown('<div style="background-color: rgba(40, 40, 40, 0.9); padding: 20px; border-radius: 10px; border: 1px solid #555;">', unsafe_allow_html=True)
        st.info("👋 Configuración del juego")
        
        st.markdown("<h3>🛠️ Crear Nuevo Sorteo</h3>", unsafe_allow_html=True)
        
        input_names = st.text_area(
            "Nombres (uno por línea):",
            height=150,
            placeholder="Martin\nDiego\nLucho"
        )
        
        if st.button("🎲 Sortear y Guardar", type="primary"):
            names_list = [n.strip() for n in input_names.replace(',', '\n').split('\n') if n.strip()]
            
            if len(names_list) < 3:
                st.error("Mínimo 3 personas.")
            elif len(names_list) != len(set(names_list)):
                st.error("Hay nombres duplicados.")
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
                        <span style="font-size: 2.5em; color: #00ff00 !important; text-shadow: 0px 0px 10px #00ff00;">✨ {amigo_secreto} ✨</span>
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
        st.markdown("<p>⚠️ Zona de peligro: Borrar todo.</p>", unsafe_allow_html=True)
        pass_check = st.text_input("Escribe 'BORRAR' para confirmar:", key="reset_pass")
        if st.button("🗑️ Reiniciar Sorteo"):
            if pass_check == "BORRAR": 
                df_vacio = pd.DataFrame(columns=["Participante", "Amigo", "Visto"])
                guardar_datos(df_vacio)
                st.success("Borrado.")
                time.sleep(1)
                st.rerun()




