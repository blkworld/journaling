import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from streamlit_calendar import calendar

# --- NOTION THEME ENGINE ---
st.set_page_config(page_title="— journal", layout="wide", page_icon="📓")

st.markdown("""
    <style>
    /* Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
    }

    /* Notion Style Header */
    .notion-header {
        font-size: 45px;
        font-weight: 700;
        margin-bottom: 0px;
        color: #ffffff;
        letter-spacing: -1px;
    }
    
    .notion-quote {
        border-left: 3px solid #37352f;
        padding-left: 14px;
        color: #9b9b9b;
        font-style: italic;
        margin-bottom: 30px;
    }

    /* Table Styling like your Screenshot */
    div[data-testid="stDataFrame"] {
        border: none;
    }
    
    /* Buttons & Inputs */
    .stButton>button {
        background-color: #2383e2;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 5px 15px;
        font-weight: 500;
    }
    
    /* Metrics like Notion Callouts */
    [data-testid="stMetric"] {
        background-color: #1a1c23;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown('<div class="notion-header">— journal</div>', unsafe_allow_html=True)
st.markdown('<div class="notion-quote">"Trading is the hardest way to make easy money"</div>', unsafe_allow_html=True)

# --- DATABASE LOGIC ---
if 'trades' not in st.session_state:
    # Mengikuti kolom pada screenshot Notion kamu
    st.session_state.trades = pd.DataFrame(columns=[
        'ENTRY', 'Date', 'Pair', 'Key Level', 'Result', 'PNL', 'RR', 'Direction', 'Setup'
    ])

# --- TOP NAVIGATION & METRICS ---
tab1, tab2, tab3 = st.tabs(["📊 Trade", "📅 Trading Calendar", "📈 Chart"])

# --- TAB 1: DATA TABLE (NOTION STYLE) ---
with tab1:
    # Quick Input Row
    with st.expander("+ New Trade Entry"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            date = st.date_input("Date", datetime.now())
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
                'ENTRY': '📄',
                'Date': date.strftime("%b %d"),
                'Pair': pair,
                'Key Level': key_level,
                'Result': result,
                'PNL': f"${pnl:,.2f}",
                'RR': rr,
                'Direction': direction,
                'Setup': setup
            }
            st.session_state.trades = pd.concat([st.session_state.trades, pd.DataFrame([new_trade])], ignore_index=True)
            st.rerun()

    # The Table Display
    st.dataframe(
        st.session_state.trades,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Result": st.column_config.SelectboxColumn("Result", options=["WIN", "LOSS", "FLAT"], required=True),
            "Direction": st.column_config.TextColumn("Direction"),
        }
    )

# --- TAB 2: CALENDAR ---
with tab2:
    events = []
    for i, row in st.session_state.trades.iterrows():
        pnl_val = float(row['PNL'].replace('$', '').replace(',', ''))
        color = "#2ecc71" if pnl_val > 0 else "#e74c3c" if pnl_val < 0 else "#808080"
        events.append({
            "title": f"{row['Pair']} {row['PNL']}",
            "start": datetime.now().strftime("%Y-%m-%d"), # Contoh dummy date
            "backgroundColor": color
        })
    
    calendar(events=events, options={"initialView": "dayGridMonth"})

# --- TAB 3: CHART ---
with tab3:
    if not st.session_state.trades.empty:
        # Simple Equity Curve logic
        pnl_series = st.session_state.trades['PNL'].str.replace('$', '').replace(',', '').astype(float)
        equity = pnl_series.cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=equity, mode='lines+markers', line=dict(color='#2383e2', width=3)))
        fig.update_layout(template="plotly_dark", title="Account Growth", margin=dict(l=0,r=0,b=0,t=40))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to display yet.")
