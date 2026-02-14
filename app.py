import streamlit as st
import requests
import pandas as pd
import feedparser
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC
from google import genai

# --- KONFIGURATION & INITIALISIERUNG ---
st.set_page_config(page_title="Gold Intelligence Terminal", layout="wide", page_icon="🤖")

# Nutze Streamlit Secrets oder direkte Eingabe (für GitHub/Streamlit Cloud empfohlen)
# Falls du es lokal testest, kannst du den Key hier eintragen oder st.secrets nutzen
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

# --- FUNKTIONEN ---

def get_exact_model_name():
    """Findet den exakten Namen für Gemini 3 Flash in deinem Account."""
    try:
        for m in client.models.list():
            # Suche nach gemini-3 und flash im Namen
            if "gemini-3" in m.name.lower() and "flash" in m.name.lower():
                return m.name
        # Fallback auf Standard, falls Liste scheitert
        return "gemini-2.0-flash" 
    except Exception:
        return "gemini-1.5-flash"

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
            if len(title) > 20: 
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
        for entry in feed.entries:
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

# --- UI ---
st.title("🤖 Gold AI Intelligence Terminal")

if st.button("🚀 Markt-Analyse starten", use_container_width=True):
    with st.spinner("Sammle Daten und generiere KI-Analyse..."):

        news_yahoo = scrape_yahoo_gold_page()
        news_finanzen_ch= get_finanzen_ch_news_data()
        calendar_output = get_gold_calendar()

        # Dynamische Modellfindung
        model_name = get_exact_model_name()

        prompt = f"""
        1. Analysiere folgende News zum aktuellen Goldpreis. 
        Bewerte jede Nachricht ob sie sich bullisch oder bärisch auf den Goldpreis auswirkt. 
        Zwischenbewrtung des Einflusses auf den Goldpreis.
        {news_yahoo}

        2. Analysiere folgende News. 
        Bewerte jede Nachricht ob sie sich bullisch oder bärisch auf den Goldpreis auswirkt. 
        Zwischenbewrtung des Einflusses auf den Goldpreis.
        {news_finanzen_ch}

        3. Werte die Daten aus dem Wirtschaftskalender aus.
        Bewerte jedes Ereignis ob es sich bullisch oder bärisch auf den Goldpreis auswirkt.
        Zwischenbewrtung des Einflusses auf den Goldpreis.
        {calendar_output}

        4. Gib am Ende eine Gesamtbewertung ab, ob der Goldpreis wahrscheinlich steigen oder fallen wird.
        """


        try:
            response = client.models.generate_content(model=model_name.replace("models/", ""), contents=prompt)
            
            # Anzeige der Analyse
            st.success("Analyse abgeschlossen!")
            st.markdown("### Gemini KI Markt-Einschätzung")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"KI Fehler: {e}")

        st.divider()
        st.write("### Rohdaten") 
        st.write("Yahoo:") 
        st.write(news_yahoo) 
        st.write("Finanzen.ch:") 
        st.write(news_finanzen_ch) 
        st.write("Wirtschaftskalender:") 
        st.write(calendar_output) 

    st.divider()
    

else:
    st.info("Klicke auf den Button oben, um die Datenquellen abzufragen und die Gemini-Analyse zu starten.")