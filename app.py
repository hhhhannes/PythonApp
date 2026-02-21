import streamlit as st
import pandas as pd
import numpy as np
import time

# Seitenkonfiguration (Tab-Titel und Icon)
st.set_page_config(page_title="Streamlit Power-Demo", page_icon="⚡")

st.title("🧪 Das Streamlit Labor")
st.markdown("Hier sind fast alle gängigen Elemente auf einen Blick.")

# --- SEITENLEISTE (Sidebar) ---
st.sidebar.header("Einstellungen")
user_role = st.sidebar.selectbox("Deine Rolle", ["Admin", "Gast", "Entwickler"])
st.sidebar.info(f"Eingeloggt als: {user_role}")

# --- LAYOUT: Spalten (Columns) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Eingaben")
    name = st.text_input("Name")
    datum = st.date_input("Wähle ein Datum")
    farbe = st.color_picker("Lieblingsfarbe", "#00f900")

with col2:
    st.subheader("Auswahl")
    level = st.slider("Level", 0, 100, 50)
    check = st.checkbox("Ich stimme zu")
    status = st.radio("Status", ["Aktiv", "Inaktiv", "Pause"])

with col3:
    st.subheader("Multimedia")
    st.image("https://placekitten.com/200/200", caption="Ein Test-Kätzchen")

# --- DATEN & DIAGRAMME ---
st.divider()
st.subheader("📊 Datenvisualisierung")

# Erstelle zufällige Daten
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)

tab1, tab2 = st.tabs(["Liniendiagramm", "Tabelle"])

with tab1:
    st.line_chart(chart_data)

with tab2:
    st.dataframe(chart_data, use_container_width=True) # Interaktive Tabelle

# --- INTERAKTION & FEEDBACK ---
st.divider()
if st.button("Starte Prozess"):
    with st.status("Verarbeite Daten...", expanded=True) as status:
        st.write("Suche Dateien...")
        time.sleep(1)
        st.write("Analysiere Inhalte...")
        time.sleep(1)
        status.update(label="Fertig!", state="complete", expanded=False)
    st.balloons()

# --- CODE ANZEIGEN ---
with st.expander("Quellcode anzeigen"):
    st.code("print('Hallo Welt!')", language='python')

# --- CHAT-INTERFACE (Sehr beliebt) ---
st.divider()
st.chat_message("assistant").write("Hey! Ich bin ein Chat-Element. Wie kann ich helfen?")