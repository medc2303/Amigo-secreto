Entiendo, disculpa. Al parecer el formato de archivo no se está mostrando correctamente en tu dispositivo.

Aquí te pego el código directamente en el chat (sin formato de archivo descargable) para que puedas copiarlo y pegarlo tú mismo:

Python

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="🎄 Amigo Secreto 🎅", page_icon="🎁", layout="centered")

# --- ENLACE A TU GOOGLE SHEET ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/12tQaIKfalMhcKjv_Z6Ymw4rqdPY94GB6T6V2cyl4xC0/edit?usp=sharing"

# --- CSS MEJORADO (FONDO Y CONTRASTE) ---
st.markdown("""
    <style>
    /* FONDO DE LA PÁGINA: Rojo Navideño Elegante */
    .stApp {
        background-color: #8B0000;
        background-image: url("https://www.transparenttextures.com/patterns/snow.png");
        background-size: auto;
    }
    
    /* CABECERA PRINCIPAL */
    .main-header {
        font-family: 'Helvetica Neue', sans-serif; 
        color: #FFFFFF; /* Texto blanco */
        text-align: center; 
        font-size: 3.5em; 
        font-weight: bold;
        text-shadow: 2px 2px 4px #000000;
        padding-bottom: 20px;
        margin-bottom: 20px;
        border-bottom: 2px dashed #FFFFFF;
    }

    /* CONTENEDORES BLANCOS (TARJETAS) PARA LEER BIEN */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Estilo para los mensajes de éxito/info para que resalten */
    .stAlert {
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* TARJETAS DE ESTADO (Los cuadritos de nombres) */
    .status-card {
        background-color: rgba(255, 255, 255, 0.95); /* Blanco casi sólido */
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        margin-bottom: 10px;
        border-left: 5px solid #1D6F42; /* Verde pino */
        color: #333333;
    }

    /* TARJETA DE RESULTADO (Cuando sale el nombre) */
    .secret-result {
        background-color: #fff0f0; 
        color: #8b0000;
        padding: 30px; 
        border-radius: 15px;
        text-align: center; 
        font-size: 1.8em;
        font-weight: bold; 
        margin-top: 20px;
        border: 3px dashed #D42426;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    
    /* Títulos dentro de la app */
    h1, h2, h3, p, span, label {
        color: white !important; /* Forzar texto blanco fuera de tarjetas */
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* Excepción: Texto dentro de inputs y tarjetas debe ser oscuro */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        color: #333;
    }
    
    /* Estilo para el botón principal */
    .stButton button {
        background-color: #1D6F42 !important;
        color: white !important;
        font-weight: bold;
        border: 2px solid #145231;
    }
    .stButton button:hover {
        background-color: #268c54 !important;
    }
    </style>
    
    <div class="main-header">🎅 Amigo Secreto 🎄</div>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    """Carga los datos asegurando que no usa caché vieja (ttl=0)"""
    try:
        # Busca Hoja 1 o Hoja1 (intenta ambas por seguridad)
        try:
            return conn.read(spreadsheet=SHEET_URL, worksheet="Hoja1", ttl=0)
        except:
            return conn.read(spreadsheet=SHEET_URL, worksheet="Hoja 1", ttl=0)
    except Exception:
        return pd.DataFrame(columns=["Participante", "Amigo", "Visto"])

def guardar_datos(df):
    """Escribe los datos"""
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

# --- LÓGICA PRINCIPAL ---
df = cargar_datos()

# Verificamos si ya hay un juego creado
juego_iniciado = not df.empty and "Participante" in df.columns and len(df) > 0

if not juego_iniciado:
    # --- PANTALLA DE CONFIGURACIÓN ---
    # Usamos un contenedor para ponerle fondo blanco al formulario y que se lea
    with st.container():
        st.markdown('<div style="background-color: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px;">', unsafe_allow_html=True)
        st.info("👋 ¡Bienvenido! No hay un sorteo activo.")
        
        st.markdown("<h3 style='color: #8B0000 !important;'>🛠️ Crear Nuevo Sorteo</h3>", unsafe_allow_html=True)
        input_names = st.text_area(
            "Escribe los nombres aquí (uno por línea):",
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
                with st.spinner("Creando la magia... ❄️"):
                    nuevo_df = realizar_sorteo(names_list)
                    guardar_datos(nuevo_df)
                    st.success("¡Listo! Recarga la página.")
                    time.sleep(2)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- PANTALLA DE JUEGO ---
    
    # 1. Selector de usuario
    participantes = df["Participante"].tolist()
    # Limpieza de datos bool
    if df["Visto"].dtype == object:
        df["Visto"] = df["Visto"].map({'TRUE': True, 'FALSE': False, True: True, False: False})
    df["Visto"] = df["Visto"].fillna(False).astype(bool)
    
    estado_visto = dict(zip(df["Participante"], df["Visto"]))
    
    # Contenedor blanco para la zona de interacción
    with st.container():
        st.markdown('<div style="background-color: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
        
        st.markdown("<h3 style='color: #8B0000 !important; text-align: center;'>🔍 Descubre tu Amigo Secreto</h3>", unsafe_allow_html=True)
        
        usuario = st.selectbox("👇 Busca tu nombre en la lista:", ["Elige tu nombre..."] + participantes)

        if usuario != "Elige tu nombre...":
            fila_usuario = df[df["Participante"] == usuario].iloc[0]
            ya_lo_vio = bool(fila_usuario["Visto"])
            
            if ya_lo_vio:
                st.warning(f"⚠️ {usuario}, ya has visto tu amigo secreto antes.")
            else:
                st.info("Solo puedes verlo una vez. Asegúrate de que nadie esté mirando tu pantalla.")
                if st.button(f"🎁 ¡ABRIR MI REGALO!", use_container_width=True):
                    amigo_secreto = fila_usuario["Amigo"]
                    
                    # Actualizar base de datos
                    idx = df.index[df["Participante"] == usuario].tolist()[0]
                    df.at[idx, "Visto"] = True
                    guardar_datos(df)
                    
                    st.balloons()
                    st.markdown(f"""
                    <div class="secret-result">
                        🤫 Tu Amigo Secreto es:<br><br>
                        <span style="font-size: 2.5em; color: #1D6F42; text-shadow: 1px 1px 0px #fff;">✨ {amigo_secreto} ✨</span>
                        <br><br><span style="font-size: 0.5em; color: #555;">(Cierra esta ventana o recarga para ocultarlo)</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. Tabla de Estado
    st.write("---")
    st.subheader("📊 ¿Quiénes faltan?")
    
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, (nombre, visto) in enumerate(estado_visto.items()):
        c = cols[i % 3]
        icon = "✅" if visto else "⏳"
        color = "#e6fffa" if visto else "white" # Verde claro si ya vio
        status = "Listo" if visto else "Pendiente"
        
        # Inyectamos HTML para la tarjetita
        c.markdown(f"""
        <div class="status-card" style="background-color: {color};">
            <strong style="color: #333;">{nombre}</strong><br>
            <span style="color: #555;">{icon} {status}</span>
        </div>
        """, unsafe_allow_html=True)

    # 3. Reinicio
    with st.expander("⚙️ Administrar / Borrar Todo"):
        st.write("Zona de peligro: Esto borra todo el sorteo.")
        pass_check = st.text_input("Escribe 'BORRAR' para confirmar:", key="reset_pass")
        if st.button("🗑️ Reiniciar Sorteo"):
            if pass_check == "BORRAR": 
                df_vacio = pd.DataFrame(columns=["Participante", "Amigo", "Visto"])
                guardar_datos(df_vacio)
                st.success("Sorteo eliminado.")
                time.sleep(1)
                st.rerun()
