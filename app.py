import streamlit as st

st.title("Meine erste Python-Webseite! 🚀")
st.write("Hallo Welt! Dies ist ein Streamlit-Dashboard.")

name = st.text_input("Wie heißt du?")
if name:
    st.success(f"Freut mich, {name}! Dein Skript läuft live.")