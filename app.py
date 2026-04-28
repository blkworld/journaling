import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_calendar import calendar
from datetime import datetime

# --- CONFIG & UI STYLE ---
st.set_page_config(page_title="Pro Trader Journal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { color: #00ff00; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #2ecc71; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE SIMULATION ---
# Nantinya data ini bisa disimpan di CSV atau database beneran
if 'journal_data' not in st.session_state:
    st.session_state.journal_data = pd.DataFrame(columns=['Date', 'Pair', 'Type', 'Result', 'Profit'])

# --- SIDEBAR: QUICK INPUT ---
with st.sidebar:
    st.header("📝 Quick Entry")
    date = st.date_input("Trade Date", datetime.now())
    pair = st.selectbox("Pair", ["XAUUSD", "NAS100", "EURUSD", "GBPUSD"])
    trade_type = st.radio("Side", ["BUY", "SELL"], horizontal=True)
    profit = st.number_input("Profit/Loss ($)", value=0.0)
    
    if st.button("Add to Journal"):
        new_data = pd.DataFrame([[date, pair, trade_type, "Win" if profit > 0 else "Loss", profit]], 
                               columns=['Date', 'Pair', 'Type', 'Result', 'Profit'])
        st.session_state.journal_data = pd.concat([st.session_state.journal_data, new_data], ignore_index=True)
        st.success("Trade Recorded!")

# --- MAIN DASHBOARD ---
st.title("📊 Trading Performance")

col1, col2, col3 = st.columns(3)
total_profit = st.session_state.journal_data['Profit'].sum()
win_rate = (len(st.session_state.journal_data[st.session_state.journal_data['Result'] == 'Win']) / len(st.session_state.journal_data) * 100) if len(st.session_state.journal_data) > 0 else 0

col1.metric("Total P/L", f"${total_profit:,.2f}")
col2.metric("Win Rate", f"{win_rate:.1f}%")
col3.metric("Total Trades", len(st.session_state.journal_data))

# --- CALENDAR VIEW ---
st.subheader("🗓️ Trade Calendar")
calendar_events = []
for index, row in st.session_state.journal_data.iterrows():
    color = "#2ecc71" if row['Profit'] > 0 else "#e74c3c"
    calendar_events.append({
        "title": f"{row['Pair']} ({'+' if row['Profit'] > 0 else ''}{row['Profit']})",
        "start": str(row['Date']),
        "backgroundColor": color
    })

calendar_options = {
    "initialView": "dayGridMonth",
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
}
calendar(events=calendar_events, options=calendar_options)

# --- CHART VIEW ---
st.subheader("📈 Equity Curve")
if not st.session_state.journal_data.empty:
    st.session_state.journal_data['Cumulative'] = st.session_state.journal_data['Profit'].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.journal_data['Date'], 
                             y=st.session_state.journal_data['Cumulative'],
                             mode='lines+markers',
                             line=dict(color='#00ff00', width=3),
                             fill='tozeroy'))
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)
