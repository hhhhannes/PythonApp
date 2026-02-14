import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, UTC

# Seite konfigurieren
st.set_page_config(page_title="Gold Calendar", layout="wide")

def get_global_gold_calendar_data():
    url = "https://economic-calendar.tradingview.com/events"
    today = datetime.now(UTC)
    end_date = today + timedelta(days=7)
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://www.tradingview.com",
        "Referer": "https://www.tradingview.com/"
    }
    
    params = {
        "from": today.strftime('%Y-%m-%dT00:00:00.000Z'),
        "to": end_date.strftime('%Y-%m-%dT23:59:59.000Z'),
        "countries": "US,CN,EU,DE,IN,GB,JP",
        "importance": "1" 
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        events = data.get('result', [])
        
        # Daten für Tabelle aufbereiten
        rows = []
        for event in events:
            date_str = event.get('date', '')
            dt_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            rows.append({
                "Zeit (UTC)": dt_obj.strftime('%d.%m. %H:%M'),
                "Land": event.get('country', '??'),
                "Event": event.get('title', 'Kein Titel'),
                "Actual": event.get('actual', '-'),
                "Forecast": event.get('forecast', '-'),
                "Previous": event.get('previous', '-')
            })
        return rows
    except Exception as e:
        st.error(f"Fehler beim Abruf: {e}")
        return []

# Streamlit UI
st.title("--- GLOBAL GOLD CALENDAR ---")

if st.button('Daten jetzt aktualisieren'):
    data = get_global_gold_calendar_data()
    if data:
        # Erstellt eine schöne interaktive Tabelle
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Keine Daten gefunden.")
else:
    st.info("Klicke auf den Button, um die aktuellen Gold-Events zu laden.")