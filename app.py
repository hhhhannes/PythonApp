import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC
import feedparser
import time

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

# --- FUNKTION: FINANZEN.CH RSS ---
def get_finanzen_ch_news_data():
    rss_url = "https://www.finanzen.ch/rss/news"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        news_items = []
        for entry in feed.entries[:8]:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                date_str = time.strftime('%d.%m.%y | %H:%M', entry.published_parsed)
            else:
                date_str = "Heute"
            
            soup = BeautifulSoup(entry.get('description', ''), 'html.parser')
            clean_desc = soup.get_text(separator=" ").strip()
            
            news_items.append({
                "date": date_str,
                "title": entry.get('title', 'Kein Titel').upper(),
                "desc": clean_desc,
                "link": entry.get('link', '#')
            })
        return news_items
    except:
        return []
    
# --- FUNKTION: TRADINGVIEW KALENDER ---
def get_gold_calendar():
    url = "https://economic-calendar.tradingview.com/events"
    today = datetime.now(UTC)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://www.tradingview.com",
        "Referer": "https://www.tradingview.com/"
    }
    params = {
        "from": today.strftime('%Y-%m-%dT00:00:00.000Z'),
        "to": (today + timedelta(days=7)).strftime('%Y-%m-%dT23:59:59.000Z'),
        "countries": "US,CN,EU,DE,IN,GB,JP",
        "importance": "1" 
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
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

# 1. Titel & Update-Button ganz oben
col_title, col_btn = st.columns([4, 1])

with col_title:
    st.title("💰 Gold Market Terminal")

with col_btn:
    # Button bündig zum Titel platzieren
    st.write("##") # Kleiner Platzhalter für die Ausrichtung
    if st.button("🔄 Aktualisieren", use_container_width=True):
        st.rerun()

st.divider()

# --- SEKTION 1: PREIS & NEWS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Live Preis (Yahoo)")
    data = scrape_yahoo_gold_page()
    if "error" in data and data["price"] == "Fehler":
        st.error(data["error"])
    else:
        # Große Anzeige des Preises
        st.metric(label="Gold Future (GC=F)", value=f"${data['price']}")
        st.caption(f"Stand: {data.get('timestamp')}")

with col2:
    st.subheader("Gold News")
    if data["news"]:
        for n in data["news"]:
            st.markdown(f"**•** {n}")
    else:
        st.info("Keine News gefunden oder Yahoo blockiert.")

st.divider()

# --- MITTE: FINANZEN.CH RSS FEED ---
st.subheader("📰 Finanzen.ch - Ausführliche Marktnachrichten")
f_news = get_finanzen_ch_news_data()
if f_news:
    for item in f_news:
        with st.expander(f"{item['date']} | {item['title']}"):
            st.write(item['desc'])
            st.markdown(f"[Zum Artikel]({item['link']})")
else:
    st.info("Keine Nachrichten von finanzen.ch verfügbar.")

st.divider()

# --- SEKTION 2: KALENDER ---
st.subheader("📅 Wirtschaftskalender (Nächste 7 Tage)")
cal_data = get_gold_calendar()

if cal_data:
    df = pd.DataFrame(cal_data)
    # Interaktive Tabelle anzeigen
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.error("Kalenderdaten konnten nicht geladen werden. Bitte versuche es in wenigen Minuten erneut.")