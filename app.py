import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="🎄 Amigo Secreto 🎅", page_icon="🎁", layout="centered")

# --- ENLACE A TU GOOGLE SHEET ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/12tQaIKfalMhcKjv_Z6Ymw4rqdPY94GB6T6V2cyl4xC0/edit?usp=sharing"

# --- CSS: MODO OSCURO FORZADO Y ESTILOS ---
st.markdown("""
    <style>
    /* 1. FORZAR ESQUEMA DE COLOR OSCURO AL NAVEGADOR */
    :root {
        color-scheme: dark;
    }
    
    /* 2. FONDO DE LA PÁGINA (Rojo Oscuro Navideño) */
    .stApp {
        background-color: #8B0000;
        background-image: url("https://www.transparenttextures.com/patterns/snow.png");
        background-size: auto;
    }
    
    /* 3. CABECERA */
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

    /* 4. TARJETAS (Fondo Gris Oscuro para que resalte el texto blanco) */
    .status-card, .secret-result, div[data-testid="stExpander"] {
        background-color: #2b2b2b !important;
        color: #FFFFFF !important;
        border: 1px solid #444;
    }
    
    .status-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #1D6F42; /* Borde verde */
    }

    .secret-result {
        padding: 30px; 
        border-radius: 15px;
        text-align: center; 
        border: 2px dashed #D42426;
    }
    
    /* 5. FORZAR TEXTOS A BLANCO (Arregla el problema del Modo Claro en celulares) */
    h1, h2, h3, h4, h5, h6, p, span, label, div, li, small, strong {
        color: #FFFFFF !important;
    }

    /* 6. INPUTS (Donde se escribe): Fondo Gris y Texto Blanco */
    .stTextArea textarea, .stTextInput input {
        background-color: #555555 !important;
        color: #FFFFFF !important;
        caret-color: #FFFFFF !important;
        border: 1px solid #777 !important;
    }
    
    /* 7. SELECTBOX (El menú desplegable) */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #555555 !important;
        color: white !important;
        border: 1px solid #777 !important;
    }
    
    /* Opciones del menú */
    ul[data-baseweb="menu"] {
        background-color: #333333 !important;
    }
    
    /* 8. BOTONES */
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
    
    /* Corrección extra para textos en webkit (iOS) */
    * {
        -webkit-text-fill-color: initial;
    }
    .stTextArea textarea, .stTextInput input, .stSelectbox span {
        -webkit-text-fill-color: #FFFFFF !important;
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
    Realiza el sorteo con una condición especial:
    Si existen 'Flores' y 'Lucho', Flores SIEMPRE le regala a Lucho.
    """
    givers = names.copy()
    receivers = names.copy()
    assignment = {}

    # --- LÓGICA TRUCADA ---
    # Normalizamos un poco para buscar sin importar mayúsculas exactas si fuera necesario,
    # pero aquí buscamos match exacto según tu pedido.
    
    # Verificamos si ambos están en la lista
    if "Flores" in names and "Lucho" in names:
        # Asignación forzada
        assignment["Flores"] = "Lucho"
        
        # Los sacamos de las listas para sortear al resto
        # Flores ya dio regalo (lo sacamos de givers)
        givers.remove("Flores")
        # Lucho ya recibió regalo (lo sacamos de receivers)
        receivers.remove("Lucho")
    
    # --- SORTEO DEL RESTO ---
    # Intentamos barajar hasta que nadie se toque a sí mismo
    # Nota: Como quitamos gente, las listas pueden no coincidir en índice, 
    # así que verificamos por valor.
    while True:
        random.shuffle(receivers)
        
        # Verificamos conflictos (que alguien se regale a sí mismo)
        conflict = False
        for g, r in zip(givers, receivers):
            if g == r:
                conflict = True
                break
        
        if not conflict:
            break
            
    # Agregamos los resultados del resto al diccionario de asignaciones
    for g, r in zip(givers, receivers):
        assignment[g] = r
        
    # Convertimos a DataFrame para guardar
    df = pd.DataFrame(list(assignment.items()), columns=["Participante", "Amigo"])
    df["Visto"] = [False] * len(df)
    return df

# --- APP LÓGICA ---
df = cargar_datos()
juego_iniciado = not df.empty and "Participante" in df.columns and len(df) > 0

if not juego_iniciado:
    with st.container():
        st.markdown('<div style="background-color: rgba(40, 40, 40, 0.9); padding: 20px; border-radius: 10px; border: 1px solid #555;">', unsafe_allow_html=True)
        st.info("👋 Configuración del juego")
        
        st.markdown("<h3>🛠️ Crear Nuevo Sorteo</h3>", unsafe_allow_html=True)
        # Input con estilo forzado oscuro
        input_names = st.text_area(
            "Nombres (uno por línea):",
            height=150,
            placeholder="Martin\nDiego\nLucho"
        )
        
        if st.button("🎲 Sortear y Guardar", type="primary"):
            names_list = [n.strip() for n in input_names.replace(',', '\n').split('\n') if n.strip()]
            
            # Validaciones básicas
            if len(names_list) < 3:
                st.error("Mínimo 3 personas para jugar.")
            elif len(names_list) != len(set(names_list)):
                st.error("Hay nombres duplicados. Usa apellidos si es necesario.")
            else:
                with st.spinner("Realizando sorteo..."):
                    nuevo_df = realizar_sorteo(names_list)
                    guardar_datos(nuevo_df)
                    st.success("¡Sorteo realizado con éxito!")
                    time.sleep(1)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

else:
    participantes = df["Participante"].tolist()
    # Limpieza de datos
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
                    
                    # Resultado en verde neón para resaltar
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

    # SECCIÓN DE BORRADO
    with st.expander("⚙️ Administrar / Borrar Todo"):
        st.markdown("<p style='color: white;'>⚠️ <strong>Zona de peligro:</strong> Esto borrará todos los datos.</p>", unsafe_allow_html=True)
        pass_check = st.text_input("Escribe 'BORRAR' para confirmar:", key="reset_pass")
        if st.button("🗑️ Reiniciar Sorteo"):
            if pass_check == "BORRAR": 
                df_vacio = pd.DataFrame(columns=["Participante", "Amigo", "Visto"])
                guardar_datos(df_vacio)
                st.success("Borrado.")
                time.sleep(1)
                st.rerun()



