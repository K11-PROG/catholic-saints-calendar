import streamlit as st
from datetime import date, datetime
import requests
import pandas as pd
import json
import os

# === Configuration ===
BASE_API = "https://calapi.inadiutorium.cz/api/v0"
DEFAULT_COUNTRY = "default"
DEFAULT_LANG = "en"
NOTES_FILE = "notes.json"

# === Helper functions ===
def fetch_daily_celebration(year, month, day, country, lang):
    url = f"{BASE_API}/{lang}/calendars/{country}/{year}/{month:02}/{day:02}"
    res = requests.get(url)
    if res.status_code != 200:
        return ["Error fetching data"]
    data = res.json()
    return [d.get("title", "Unknown") for d in data.get("celebrations", [])]

def fetch_month_calendar(year, month, country, lang):
    url = f"{BASE_API}/{lang}/calendars/{country}/{year}/{month:02}"
    res = requests.get(url)
    if res.status_code != 200:
        return {}
    return res.json().get("calendar", {})

def fetch_daily_meditation(date_str):
    return (
        "Trust in God's providence today. Reflect on the life of the saint commemorated and offer your day to Christ."
    )

def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_notes(notes_data):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes_data, f, indent=4)

# === Main App ===
def main():
    st.set_page_config(page_title="Catholic Saints Calendar", layout="wide")
    st.title("📅 Catholic Saints Calendar & Liturgical Feasts")

    today = date.today()
    st.sidebar.header("Settings")
    year = st.sidebar.number_input("Year", value=today.year, min_value=2000, max_value=2100)
    month = st.sidebar.selectbox("Month", list(range(1, 13)), index=today.month - 1)
    country = st.sidebar.selectbox("National calendar", ["default", "US", "PL", "IT", "FR"])
    lang = st.sidebar.selectbox("Language", ["en", "la", "it", "fr"])

    st.subheader(f"Liturgical Calendar for {datetime(year, month, 1).strftime('%B %Y')}")
    calendar_data = fetch_month_calendar(year, month, country, lang)

    rows = []
    for day_str, celebrations in calendar_data.items():
        day_num = int(day_str)
        feast_titles = ", ".join([c["title"] for c in celebrations.get("celebrations", [])])
        rows.append({"Date": f"{year}-{month:02}-{day_num:02}", "Celebration": feast_titles})

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    selected_date = st.date_input("Select a date to view celebrations", today)
    saints = fetch_daily_celebration(selected_date.year, selected_date.month, selected_date.day, country, lang)
    st.subheader(f"Feast(s) on {selected_date.strftime('%B %d')}")
    for s in saints:
        st.markdown(f"- {s}")

    meditation = fetch_daily_meditation(selected_date.strftime("%Y-%m-%d"))
    st.markdown("---")
    st.subheader("🕯️ Daily Catholic Meditation")
    st.markdown(f"> {meditation}")

    st.markdown("---")
    st.subheader("📖 Personal Notes")
    notes_data = load_notes()
    note_key = selected_date.strftime("%Y-%m-%d")
    note_text = notes_data.get(note_key, "")
    updated_note = st.text_area("Write your reflection or notes:", note_text, height=200)
    if st.button("Save Note"):
        notes_data[note_key] = updated_note
        save_notes(notes_data)
        st.success("Note saved successfully.")

    st.markdown("---")
    st.subheader("📅 Export Liturgical Calendar")
    st.markdown(f"[Download ICS for {year} - {country.upper()}]({BASE_API}/{lang}/calendars/{country}/{year}?format=ics)")

    st.markdown("""
    ---
    Built with Streamlit • [GitHub Repo](https://github.com/your-username/saints-calendar-app)
    """)

if __name__ == "__main__":
    main()
