import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC

# --- SEITE KONFIGURIEREN ---
st.set_page_config(page_title="Gold Terminal", layout="wide", page_icon="💰")

# --- FUNKTION: YAHOO SCRAPER ---
def scrape_yahoo_gold_page():
    url = "https://finance.yahoo.com/quote/GC=F/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": f"Yahoo blockiert (Status {response.status_code})", "price": "N/A", "news": []}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice", "data-symbol": "GC=F"})
        current_price = price_tag.text if price_tag else "Nicht gefunden"

        news_list = []
        for h3 in soup.find_all('h3'):
            title = h3.get_text(strip=True)
            if len(title) > 20 and len(news_list) < 15: 
                news_list.append(title)
        
        return {"timestamp": datetime.now().strftime('%d.%m. %H:%M'), "price": current_price, "news": news_list}
    except Exception as e:
        return {"error": str(e), "price": "Fehler", "news": []}

# --- FUNKTION: TRADINGVIEW KALENDER ---
def get_gold_calendar():
    url = "https://economic-calendar.tradingview.com/events"
    today = datetime.now(UTC)
    params = {
        "from": today.strftime('%Y-%m-%dT00:00:00.000Z'),
        "to": (today + timedelta(days=7)).strftime('%Y-%m-%dT23:59:59.000Z'),
        "countries": "US,CN,EU,DE,IN,GB,JP",
        "importance": "1" 
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        events = response.json().get('result', [])
        return [{
            "Zeit (UTC)": datetime.fromisoformat(e['date'].replace('Z', '+00:00')).strftime('%d.%m. %H:%M'),
            "Land": e.get('country', '??'),
            "Event": e.get('title', 'Kein Titel'),
            "Actual": e.get('actual', '-'),
            "Forecast": e.get('forecast', '-'),
            "Previous": e.get('previous', '-')
        } for e in events]
    except:
        return []

# --- STREAMLIT UI ---
st.title("💰 Gold Market Terminal")

# Sidebar für manuelle Updates
if st.sidebar.button("Daten aktualisieren"):
    st.rerun()

# --- SEKTION 1: PREIS & NEWS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Live Preis (Yahoo)")
    data = scrape_yahoo_gold_page()
    if "error" in data and data["price"] == "Fehler":
        st.error(data["error"])
    else:
        st.metric(label="Gold Future (GC=F)", value=f"${data['price']}", delta_color="normal")
        st.caption(f"Stand: {data.get('timestamp')}")

with col2:
    st.subheader("Gold News")
    if data["news"]:
        for n in data["news"]:
            st.write(f"• {n}")
    else:
        st.write("Keine News gefunden oder Yahoo blockiert.")

st.divider()

# --- SEKTION 2: KALENDER ---
st.subheader("📅 Wirtschaftskalender (Nächste 7 Tage)")
cal_data = get_gold_calendar()
if cal_data:
    df = pd.DataFrame(cal_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("Kalenderdaten konnten nicht geladen werden.")