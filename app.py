import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from streamlit_calendar import calendar

# --- TEMA NOTION ---
st.set_page_config(page_title="— journal", layout="wide", page_icon="📓")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0e1117; }
    .notion-header { font-size: 45px; font-weight: 700; color: white; letter-spacing: -1px; margin-bottom: 0px; }
    .notion-quote { border-left: 3px solid #37352f; padding-left: 14px; color: #9b9b9b; font-style: italic; margin-bottom: 30px; }
    div[data-testid="stDataFrame"] { border: none; }
    .stButton>button { background-color: #2383e2; color: white; border-radius: 4px; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="notion-header">— journal</div>', unsafe_allow_html=True)
st.markdown('<div class="notion-quote">"Trading is the hardest way to make easy money"</div>', unsafe_allow_html=True)

# --- LOGIKA DATABASE ---
if 'trades' not in st.session_state:
    st.session_state.trades = pd.DataFrame(columns=[
        'ENTRY', 'Date', 'Pair', 'Key Level', 'Result', 'PNL', 'RR', 'Direction', 'Setup'
    ])

# --- NAVIGASI TAB ---
tab1, tab2, tab3 = st.tabs(["📊 Trade", "📅 Trading Calendar", "📈 Chart"])

with tab1:
    with st.expander("+ New Trade Entry"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            tr_date = st.date_input("Date", datetime.now())
            pair = st.selectbox("Pair", ["MNQ1!", "NAS100", "XAUUSD", "BTCUSD"])
        with c2:
            direction = st.selectbox("Direction", ["BUY", "SELL"])
            setup = st.text_input("Setup", "A+")
        with c3:
            pnl = st.number_input("PNL ($)", value=0.0)
            rr = st.number_input("RR", value=0.0)
        with c4:
            result = st.selectbox("Result", ["WIN", "LOSS", "FLAT"])
            key_level = st.text_input("Key Level", "Fair Value Gap")
            
        if st.button("Add to Journal"):
            new_trade = {
                'ENTRY': '📄', 'Date': tr_date.strftime("%b %d"), 'Pair': pair,
                'Key Level': key_level, 'Result': result, 'PNL': pnl,
                'RR': rr, 'Direction': direction, 'Setup': setup
            }
            st.session_state.trades = pd.concat([st.session_state.trades, pd.DataFrame([new_trade])], ignore_index=True)
            st.rerun()

    st.dataframe(st.session_state.trades, use_container_width=True, hide_index=True)

with tab2:
    events = []
    for _, row in st.session_state.trades.iterrows():
        color = "#2ecc71" if row['PNL'] > 0 else "#e74c3c" if row['PNL'] < 0 else "#808080"
        events.append({
            "title": f"{row['Pair']} (${row['PNL']})",
            "start": datetime.now().strftime("%Y-%m-%d"),
            "backgroundColor": color
        })
    calendar(events=events, options={"initialView": "dayGridMonth"})

with tab3:
    if not st.session_state.trades.empty:
        equity = st.session_state.trades['PNL'].cumsum()
        fig = go.Figure(go.Scatter(y=equity, mode='lines+markers', line=dict(color='#2383e2')))
        fig.update_layout(template="plotly_dark", title="Equity Curve")
        st.plotly_chart(fig, use_container_width=True)
