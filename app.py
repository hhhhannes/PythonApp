import streamlit as st

# Die Überschrift der App
st.title("🚀 Meine erste Streamlit App")

# Ein einfacher Text
st.write("Dies ist eine super simple App, um zu zeigen, wie Streamlit funktioniert.")

# Ein Eingabefeld für den Namen
name = st.text_input("Wie heißt du?", "Besucher")

# Ein Schieberegler für Zahlen
alter = st.slider("Wie alt bist du?", 0, 100, 25)

# Ein Button, der eine Aktion auslöst
if st.button("Sag Hallo!"):
    st.success(f"Hallo {name}! Du bist also {alter} Jahre alt.")
    st.balloons()