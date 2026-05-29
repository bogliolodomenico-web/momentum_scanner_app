"""
MOMENTUM SETUP SCANNER — App Streamlit Integrata
Basata su regime_classifier_v3.6.1
Parametri fissi (pre-ottimizzati) — nessuna WFO ad ogni avvio.
Avvio: streamlit run momentum_scanner_app.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import warnings
import time
from datetime import datetime
import pytz
import json
import os


from datetime import timedelta
start_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIGURAZIONE PAGINA (con menu nascosto)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Momentum Setup Scanner",
    page_icon="📡",
    layout="wide",
    menu_items={
        'Get help': None,
        'Report a bug': None,
        'About': None,
    }
)

# ─────────────────────────────────────────────
# CSS per nascondere elementi superflui di Streamlit
# e per personalizzare sfondo, pulsanti e card
# ─────────────────────────────────────────────
hide_streamlit_style = """
    <style>
        /* Nasconde il footer "Built with Streamlit" */
        footer {visibility: hidden;}
        
        /* Nasconde il pulsante "Deploy" e altri pulsanti della toolbar */
        .stDeployButton {display: none;}
        
        /* Nasconde la barra decorativa rossa superiore */
        [data-testid="stDecoration"] {display: none;}
        
        /* Nasconde la toolbar (Fork, GitHub, ecc.) */
        [data-testid="stToolbar"] {display: none;}
        
        /* Nasconde il menu hamburger (tre puntini) */
        #MainMenu {visibility: hidden;}
        
        /* ========== RIMOZIONE COMPLETA BANDA BIANCA SUPERIORE ========== */
        /* Rimuove il padding e margine predefinito del container principale */
        .main .block-container {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }
        /* Nasconde l'header di Streamlit (barra vuota) */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        /* Forza il primo elemento della pagina a non avere margine superiore */
        .scanner-header {
            margin-top: 0rem !important;
            padding-top: 1rem !important;  /* mantiene un po' di spazio interno */
        }
        /* Rimuove eventuale spazio aggiunto dal body */
        body {
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Assicura che l'app parta da 0 */
        .stApp {
            margin-top: 0rem !important;
            padding-top: 0rem !important;
        }
        /* Elimina spazi residui in cima a qualsiasi elemento */
        .element-container, .stMarkdown, .stVerticalBlock {
            margin-top: 0 !important;
        }

        /* ========== SFONDO PERSONALIZZATO ========== */
        .stApp {
            background: #87CEEB;
        }
        .main {
            background: transparent;
        }
        
        /* ========== PULSANTI EVIDENZIATI ========== */
        /* Pulsante ANALIZZA SEGNALI (colore rosso tenue) */
        .stButton > button {
            background: linear-gradient(135deg, #c96a6a, #b04e4e) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.6rem 2rem !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            font-family: 'DM Sans', sans-serif !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(192, 80, 80, 0.3) !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            background: linear-gradient(135deg, #d47a7a, #c25c5c) !important;
            box-shadow: 0 8px 20px rgba(192, 80, 80, 0.5) !important;
        }
        /* Pulsante Aggiorna ora nella sidebar */
        .sidebar .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #238636, #2ea043) !important;
            box-shadow: 0 2px 8px rgba(35,134,54,0.3) !important;
        }
        .sidebar .stButton > button:hover {
            background: linear-gradient(135deg, #2ea043, #3fb950) !important;
            box-shadow: 0 4px 12px rgba(35,134,54,0.5) !important;
        }
        
        /* ========== CARD BUY (sfondo chiaro verde) ========== */
        .card-buy {
            background: linear-gradient(135deg, #e6f4ea 0%, #d0ebd6 100%);
            border: 2px solid #238636 !important;
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 2px 8px rgba(35,134,54,0.2);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card-buy:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(35,134,54,0.4);
        }
        
        /* ========== CARD SELL (sfondo chiaro rosso) ========== */
        .card-sell {
            background: linear-gradient(135deg, #fce8e6 0%, #f8d7d5 100%);
            border: 2px solid #da3633 !important;
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 2px 8px rgba(218,54,51,0.2);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card-sell:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(218,54,51,0.3);
        }
        
        /* CARD per titoli illiquidi (ambrato) */
        .card-illiquid {
            background: linear-gradient(135deg, #fff3e0 0%, #ffe6b3 100%);
            border: 2px solid #d29922 !important;
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 0.8rem;
        }
        
        /* Classe aggiuntiva per cambio stato (bordo pulsante blu) */
        .card-changed {
            animation: pulse-blue 1s ease-in-out;
            border-width: 3px !important;
        }
        @keyframes pulse-blue {
            0% { border-color: #1f6feb; box-shadow: 0 0 0 0 rgba(31,111,235,0.4); }
            70% { border-color: #58a6ff; box-shadow: 0 0 0 6px rgba(31,111,235,0); }
            100% { border-color: #1f6feb; box-shadow: 0 0 0 0 rgba(31,111,235,0); }
        }
        
        /* Migliora leggibilità testo nelle card */
        .ticker-name {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.2rem;
            font-weight: 600;
            color: #1a1a1a;
        }
        .badge-buy, .badge-sell, .badge-warn, .badge-changed {
            font-weight: 700;
            letter-spacing: 0.5px;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-left: 10px;
        }
        .badge-buy {
            background-color: #238636;
            color: white;
        }
        .badge-sell {
            background-color: #da3633;
            color: white;
        }
        .badge-warn {
            background-color: #d29922;
            color: #1a1a1a;
        }
        .badge-changed {
            background-color: #1f6feb;
            color: white;
        }
        
        /* Riquadro header (avorio) */
        .scanner-header {
            background: #f5f5dc;
            border: 1px solid #c0a080;
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .scanner-header h1 {
            color: #3a2a1f;
        }
        .scanner-header p {
            color: #5a4a3a;
        }
        
        /* Testo prezzi su sfondo chiaro */
        .card-buy .ticker-name, .card-sell .ticker-name {
            color: #1a1a1a;
        }
        .card-buy [style*="font-family:IBM Plex Mono"], 
        .card-sell [style*="font-family:IBM Plex Mono"] {
            color: #1a1a1a !important;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARICAMENTO TICKER DA FILE JSON
# ─────────────────────────────────────────────
def load_tickers_from_json(file_path="Titoli_Marco.json"):
    """Carica la lista dei ticker dal file JSON."""
    if not os.path.exists(file_path):
        # Fallback di default se il file non esiste
        return {
            "A2A.MI": "A2A",            
        }
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

ALL_TICKERS = load_tickers_from_json()

# ─────────────────────────────────────────────
# PARAMETRI FISSI (indicatori — non modificabili dall'utente)
# ─────────────────────────────────────────────
CFG_BASE = {
    "MACD_FAST": 12, "MACD_SLOW": 26, "MACD_SIGNAL": 9,
    "W_MACD_FAST": 6, "W_MACD_SLOW": 13, "W_MACD_SIGNAL": 9,
    "RSI_PERIOD": 14, "STOCH_K_PERIOD": 14, "STOCH_SMOOTH": 3,
    "EMA_PERIOD": 35, "EMA_MAX_DIST": 25.0, "LIM_TRENDSCORE": 0.8,
    "STOCH_MIN": 3, "STOCH_MAX": 65,
    "RSI_MIN": 3, "RSI_MAX": 60, "RSI_SLOPE_BARS": 6,
    "VOL_TREND_RATIO": 1.0, "PRICE_MOM_BARS": 3, "W_MACD_MA_PERIOD": 5,
    "VOL_SHORT_PERIOD": 7, "VOL_MA_PERIOD": 20, "TURNOVER_MA_PERIOD": 20,
    "MIN_TURNOVER_EUR": 2_000_000,
    "RSI_OB_LEVEL": 90, "PSAR_STEP": 0.0012, "PSAR_MAX_STEP": 0.010,
}

# ─────────────────────────────────────────────
# CALCOLO GIORNI NECESSARI — dinamico su CFG_BASE
# ─────────────────────────────────────────────
def calc_required_days(cfg: dict, buffer_pct: float = 0.25) -> int:
    daily_bars = [
        cfg["MACD_SLOW"] + cfg["MACD_SIGNAL"],
        cfg["RSI_PERIOD"] + cfg["RSI_SLOPE_BARS"],
        cfg["STOCH_K_PERIOD"] + cfg["STOCH_SMOOTH"],
        cfg["EMA_PERIOD"] * 3,
        cfg["VOL_MA_PERIOD"],
        cfg["TURNOVER_MA_PERIOD"],
        cfg["PRICE_MOM_BARS"],
        30,
    ]
    max_daily_cal  = max(daily_bars) / 5 * 7
    weekly_bars    = cfg["W_MACD_SLOW"] + cfg["W_MACD_SIGNAL"] + cfg["W_MACD_MA_PERIOD"]
    max_weekly_cal = weekly_bars * 7 * 1.4
    return int(max(max_daily_cal, max_weekly_cal) * (1 + buffer_pct))

REQUIRED_DAYS = calc_required_days(CFG_BASE)

# ─────────────────────────────────────────────
# ORARIO BORSA ITALIANA
# ─────────────────────────────────────────────
def is_market_open() -> tuple[bool, str]:
    tz_it  = pytz.timezone("Europe/Rome")
    now_it = datetime.now(tz_it)
    wd     = now_it.weekday()
    hhmm   = now_it.hour * 60 + now_it.minute
    if wd >= 5:
        return False, f"🔴 CHIUSO — weekend  {now_it.strftime('%H:%M')} CET"
    if hhmm < 9 * 60:
        return False, f"🔴 PRE-MARKET — apertura 09:00 CET"
    if hhmm >= 17 * 60 + 30:
        return False, f"🔴 CHIUSO — chiusura 17:30 CET"
    return True, f"🟢 APERTO — {now_it.strftime('%H:%M')} CET"

# ─────────────────────────────────────────────
# FUNZIONI CORE (invariate)
# ─────────────────────────────────────────────
def _add_psar(d: pd.DataFrame) -> pd.DataFrame:
    psar_ind    = ta.trend.PSARIndicator(
        d['High'], d['Low'], d['Close'],
        step=CFG_BASE["PSAR_STEP"], max_step=CFG_BASE["PSAR_MAX_STEP"]
    )
    d = d.copy()
    d['PSAR']       = psar_ind.psar()
    d['PSAR_TREND'] = np.where(d['Close'] > d['PSAR'], 1, -1)
    return d

def build_indicators(df_d: pd.DataFrame, df_w: pd.DataFrame) -> pd.DataFrame:
    d = df_d.copy()
    w = df_w.copy()

    macd_obj    = ta.trend.MACD(d['Close'],
                                window_fast=CFG_BASE["MACD_FAST"],
                                window_slow=CFG_BASE["MACD_SLOW"],
                                window_sign=CFG_BASE["MACD_SIGNAL"])
    d['MACD']       = macd_obj.macd()       / d['Close'] * 100
    d['MACD_SIG']   = macd_obj.macd_signal()/ d['Close'] * 100
    d['MACD_HIST']  = d['MACD'] - d['MACD_SIG']
    d['MACD_ACCEL'] = d['MACD_HIST'] - d['MACD_HIST'].shift(1)

    d['RSI']     = ta.momentum.rsi(d['Close'], window=CFG_BASE["RSI_PERIOD"])
    stoch        = ta.momentum.StochasticOscillator(
        d['High'], d['Low'], d['Close'],
        window=CFG_BASE["STOCH_K_PERIOD"], smooth_window=CFG_BASE["STOCH_SMOOTH"])
    d['STOCH_K'] = stoch.stoch()
    d['STOCH_D'] = stoch.stoch_signal()

    d['EMA']     = d['Close'].ewm(span=CFG_BASE["EMA_PERIOD"], adjust=False).mean()
    d['EMA_DIST']= (d['Close'] - d['EMA']) / d['EMA'] * 100

    ema_diff      = d['EMA'].diff() / d['EMA'].shift(1) * 100
    s1            = ema_diff.ewm(span=3, adjust=False).mean()
    s2            = s1.diff().ewm(span=3, adjust=False).mean()
    def _norm10(s):
        s  = s.astype(float).replace([float('inf'), float('-inf')], float('nan'))
        mx = s.dropna().abs().max()
        return (s / mx * 10).clip(-10, 10) if mx and mx > 0 else s * 0
    d['TREND_SCORE']     = _norm10(_norm10(s1) * (1 + _norm10(s2) / 10))

    d['VOL_MA_SHORT']    = d['Volume'].rolling(CFG_BASE["VOL_SHORT_PERIOD"]).mean()
    d['VOL_MA_LONG']     = d['Volume'].rolling(CFG_BASE["VOL_MA_PERIOD"]).mean()
    d['VOL_TREND']       = d['VOL_MA_SHORT'] / d['VOL_MA_LONG']
    d['TURNOVER_EUR_MA'] = (d['Volume'] * d['Close']).rolling(CFG_BASE["TURNOVER_MA_PERIOD"]).mean()

    w_macd       = ta.trend.MACD(w['Close'],
                                 window_fast=CFG_BASE["W_MACD_FAST"],
                                 window_slow=CFG_BASE["W_MACD_SLOW"],
                                 window_sign=CFG_BASE["W_MACD_SIGNAL"])
    w['W_MACD']  = w_macd.macd() / w['Close'] * 100
    w['W_MACD_MA']   = w['W_MACD'].rolling(CFG_BASE["W_MACD_MA_PERIOD"]).mean()
    wfd          = w.reindex(d.index, method='ffill')
    d['W_MACD']      = wfd['W_MACD']
    d['W_MACD_MA']   = wfd['W_MACD_MA']

    d = d.dropna(subset=['MACD', 'RSI', 'STOCH_K', 'EMA', 'W_MACD', 'TURNOVER_EUR_MA'])
    d = _add_psar(d)
    return d.dropna(subset=['PSAR'])

def apply_conditions(df: pd.DataFrame, min_conditions: int) -> pd.DataFrame:
    d = df.copy()
    d['RSI_SLOPE'] = d['RSI'] - d['RSI'].shift(CFG_BASE["RSI_SLOPE_BARS"])
    d['PRICE_MOM'] = d['Close'] / d['Close'].shift(CFG_BASE["PRICE_MOM_BARS"]) - 1

    d['LIQUIDITY_OK'] = (d['TURNOVER_EUR_MA'] >= CFG_BASE["MIN_TURNOVER_EUR"]).fillna(False)
    d['C1_MACD']   = ((d['MACD_HIST'] > 0) & (d['MACD_ACCEL'] > 0)).fillna(False)
    d['C2_W_MACD'] = (d['W_MACD'] >= d['W_MACD_MA']).fillna(False)
    d['C3_STOCH']  = ((d['STOCH_K'] > d['STOCH_D']) &
                      (d['STOCH_K'] < CFG_BASE["STOCH_MAX"]) &
                      (d['STOCH_K'] > CFG_BASE["STOCH_MIN"])).fillna(False)
    d['C4_RSI']    = ((d['RSI'] >= CFG_BASE["RSI_MIN"]) &
                      (d['RSI'] <= CFG_BASE["RSI_MAX"]) &
                      (d['RSI_SLOPE'] > 0)).fillna(False)
    d['C5_EMA']    = ((d['Close'] > d['EMA']) &
                      (d['EMA_DIST'] <= CFG_BASE["EMA_MAX_DIST"])).fillna(False)
    d['C6_VOL']    = (d['VOL_TREND'] >= CFG_BASE["VOL_TREND_RATIO"]).fillna(False)
    d['C7_MOM']    = (d['PRICE_MOM'] > 0).fillna(False)
    d['C8_TREND']  = (d['TREND_SCORE'] > CFG_BASE["LIM_TRENDSCORE"]).fillna(False)

    d['SCORE'] = (d['C1_MACD'].astype(int) + d['C2_W_MACD'].astype(int) +
                  d['C3_STOCH'].astype(int) + d['C4_RSI'].astype(int) +
                  d['C6_VOL'].astype(int)   + d['C7_MOM'].astype(int))

    d['SETUP_ACTIVE'] = (
        d['LIQUIDITY_OK'] & d['C5_EMA'] & d['C8_TREND'] &
        (d['SCORE'] >= min_conditions) &
        (d['PSAR_TREND'].fillna(1) != -1)
    )
    return d

@st.cache_data(ttl=3600, show_spinner=False)
def download_and_analyze(ticker: str, min_conditions: int) -> dict:
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        df_d = yf.download(ticker, start_date, end=end_date,
                   progress=False, auto_adjust=False, interval='1d')
        df_w = yf.download(ticker, start_date, end=end_date,
                   progress=False, auto_adjust=False, interval='1wk')

        for df in [df_d, df_w]:
            if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.dropna(subset=['High', 'Low', 'Close', 'Volume'], inplace=True)

        if df_d.empty or df_w.empty or len(df_d) < 60:
            return {"error": "Dati insufficienti"}

        df = build_indicators(df_d, df_w)
        if df.empty:
            return {"error": "Indicatori vuoti"}

        df   = apply_conditions(df, min_conditions)
        last = df.iloc[-1]

        # YTD
        ytd_start = df[df.index >= pd.Timestamp(f"{datetime.now().year}-01-01")]
        ytd_ret   = None
        if not ytd_start.empty:
            ytd_ret = round((float(last['Close']) / float(ytd_start.iloc[0]['Close']) - 1) * 100, 2)

        # Max 52 settimane
        w52_high = float(df_d['High'].tail(252).max()) if len(df_d) >= 252 else None

        # Prezzo live: ultimi 2 giorni a 1 minuto
        rt_price, rt_time = None, None
        try:
            df_live = yf.download(ticker, period="2d", interval="1m",
                                  progress=False, auto_adjust=False)
            if isinstance(df_live.columns, pd.MultiIndex):
                df_live.columns = df_live.columns.get_level_values(0)
            if not df_live.empty:
                df_live  = df_live.dropna(subset=['Close'])
                rt_price = round(float(df_live.iloc[-1]['Close']), 3)
                bar_ts   = df_live.index[-1]
                if bar_ts.tzinfo is None:
                    bar_ts = bar_ts.tz_localize('UTC')
                rt_time  = bar_ts.tz_convert('Europe/Rome').strftime('%d/%m/%Y %H:%M')
        except Exception:
            pass

        psar_ok    = bool(last['PSAR_TREND'] == 1)
        gate_score = (int(bool(last['C5_EMA'])) +
                      int(bool(last['C8_TREND'])) +
                      int(bool(last['LIQUIDITY_OK'])) +
                      int(psar_ok))

        return {
            "error":        None,
            "date":         df.index[-1].strftime('%d/%m/%Y'),
            "price":        round(float(last['Close']), 3),
            "rt_price":     rt_price,
            "rt_time":      rt_time,
            "rt_today":     (rt_time is not None and
                             rt_time.startswith(datetime.now().strftime('%d/%m/%Y'))),
            "setup_active": bool(last['SETUP_ACTIVE']),
            "liquidity_ok": bool(last['LIQUIDITY_OK']),
            "C5_EMA":       bool(last['C5_EMA']),
            "C8_TREND":     bool(last['C8_TREND']),
            "psar_ok":      psar_ok,
            "score":        int(last['SCORE']),
            "gate_score":   gate_score,
            "ytd_ret":      ytd_ret,
            "w52_high":     round(w52_high, 3) if w52_high else None,
        }
    except Exception as e:
        return {"error": str(e)}

# ─────────────────────────────────────────────
# HELPER UI
# ─────────────────────────────────────────────
def _bar_html(score: int, max_score: int, label: str) -> str:
    pct = score / max_score * 100
    if score == max_score:
        fill = "background:linear-gradient(90deg,#238636,#3fb950)"
    elif score >= max_score * 0.6:
        fill = "background:linear-gradient(90deg,#d29922,#e3b341)"
    else:
        fill = "background:linear-gradient(90deg,#da3633,#f85149)"
    return (f'<div style="margin-top:0.45rem;">'
            f'<div style="font-size:0.72rem;color:#4a4a4a;'
            f'font-family:IBM Plex Mono,monospace;margin-bottom:3px;">'
            f'{label} {score}/{max_score}</div>'
            f'<div style="background:#e0e0e0;border-radius:4px;height:6px;'
            f'width:100%;overflow:hidden;">'
            f'<div style="height:6px;border-radius:4px;width:{pct}%;{fill}"></div>'
            f'</div></div>')

def render_ticker_card(ticker: str, nome: str, data: dict, changed: bool = False):
    if data.get("error"):
        st.markdown(f'<div class="card-sell">'
                    f'<span class="ticker-name">{ticker}</span>'
                    f'<span class="badge-sell">ERRORE</span>'
                    f'<div style="color:#6e4040;font-size:0.8rem;margin-top:0.5rem;">'
                    f'{data["error"]}</div></div>', unsafe_allow_html=True)
        return

    sa  = data["setup_active"]
    liq = data["liquidity_ok"]

    # Determina classe base della card (senza tenere conto di changed)
    if not liq:
        base_cls = "card-illiquid"
        badge = '<span class="badge-warn">⚠ LIQUIDO</span>'
    else:
        if sa:
            base_cls = "card-buy"
            badge = '<span class="badge-buy">BUY</span>'
        else:
            base_cls = "card-sell"
            badge = '<span class="badge-sell">SELL</span>'

    # Aggiunge eventuale classe per cambio stato (solo bordo animato)
    if changed:
        base_cls += " card-changed"

    changed_badge = '<span class="badge-changed">⚡ CAMBIO</span>' if changed else ""

    px = data["rt_price"] if data.get("rt_price") else data["price"]

    if data.get("rt_today"):
        t_html = (f'<span style="color:#1a1a1a;font-size:0.7rem;font-family:monospace;">'
                  f'🔴 LIVE {data["rt_time"]}</span>')
    elif data.get("rt_time"):
        t_html = (f'<span style="color:#4a4a4a;font-size:0.7rem;font-family:monospace;">'
                  f'📅 {data["rt_time"]}</span>')
    else:
        t_html = (f'<span style="color:#4a4a4a;font-size:0.7rem;font-family:monospace;">'
                  f'📅 chiusura {data["date"]}</span>')

    ytd_html = ""
    if data.get("ytd_ret") is not None:
        c = "#238636" if data["ytd_ret"] >= 0 else "#da3633"
        ytd_html = f'<span style="color:{c};font-size:0.78rem;margin-left:10px;">YTD {data["ytd_ret"]:+.1f}%</span>'

    w52_html = ""
    if data.get("w52_high"):
        d52 = (px / data["w52_high"] - 1) * 100
        w52_html = f'<span style="color:#4a4a4a;font-size:0.75rem;margin-left:8px;">Max52w {d52:+.1f}%</span>'

    gate_bar  = _bar_html(data["gate_score"], 4, "GATE")
    score_bar = _bar_html(data["score"],      6, "SCORE")

    st.markdown(
        f'<div class="{base_cls}">'
        f'<div style="display:flex;align-items:center;flex-wrap:wrap;">'
        f'<span class="ticker-name">{ticker}</span>'
        f'<span style="color:#4a4a4a;font-size:0.85rem;margin-left:8px;">{nome}</span>'
        f'{badge}{changed_badge}</div>'
        f'<div style="margin-top:0.4rem;display:flex;align-items:baseline;flex-wrap:wrap;gap:4px;">'
        f'<span style="font-family:IBM Plex Mono,monospace;font-size:1.25rem;'
        f'color:#1a1a1a;font-weight:700;">{px:.3f} €</span>'
        f'{ytd_html}{w52_html}</div>'
        f'<div style="margin-top:2px;">{t_html}</div>'
        f'{gate_bar}{score_bar}'
        f'</div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "prev_signals"  not in st.session_state:
    st.session_state["prev_signals"]  = {}
if "last_params"   not in st.session_state:
    st.session_state["last_params"]   = {}

# ─────────────────────────────────────────────
# HEADER + STATO MERCATO
# ─────────────────────────────────────────────
mkt_open, mkt_label = is_market_open()
mkt_cls = "market-open" if mkt_open else "market-closed"
st.markdown(
    f'<div class="scanner-header">'
    f'<h1>📡 MOMENTUM SETUP SCANNER</h1>'
    f'<p>Basato su regime_classifier v3.6.1 &nbsp;·&nbsp; '
    f'EMA + TrendScore + MACD/RSI/Stoch/Volume + PSAR &nbsp;·&nbsp; '
    f'<span class="{mkt_cls}">{mkt_label}</span></p>'
    f'</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# SIDEBAR (tutti i controlli visibili all'utente)
# ─────────────────────────────────────────────
with st.sidebar:

    # ── Ticker ──────────────────────────────
    st.markdown("### 🎛️ Ticker")
    selected_tickers = st.multiselect(
        "Seleziona i titoli",
        options=list(ALL_TICKERS.keys()),
        default=list(ALL_TICKERS.keys()),
        format_func=lambda x: f"{x} — {ALL_TICKERS[x]}",
    )
    ordine = st.selectbox(
        "Ordinamento",
        ["Setup ON prima → Score", "Score decrescente", "Ticker A→Z"],
    )

    # ── Livello di Rischio ──────────────────
    st.divider()
    st.markdown("### ⚠️ Livello di Rischio")
    st.caption(
        "Definisce quante **condizioni su 6** devono essere soddisfatte "
        "per generare un segnale BUY. "
        "Più alto = segnali rari ma affidabili. "
        "Più basso = segnali frequenti ma meno filtrati."
    )
    risk_level = st.radio(
        "Profilo",
        options=["🛡️ Rischio Minimo", "⚖️ Rischio Normale", "⚡ Rischio Massimo"],
        index=1,
    )
    risk_map       = {"🛡️ Rischio Minimo": 6,
                      "⚖️ Rischio Normale": 5,
                      "⚡ Rischio Massimo": 4}
    min_conditions = risk_map[risk_level]
    risk_desc      = {
        "🛡️ Rischio Minimo":  "Tutte e 6 le condizioni devono essere OK. Segnali molto selettivi, falsi positivi minimi.",
        "⚖️ Rischio Normale": "5 condizioni su 6. Bilanciamento ottimale tra qualità e frequenza dei segnali.",
        "⚡ Rischio Massimo": "Bastano 4 condizioni su 6. Più segnali e opportunità, ma aumentano i falsi positivi.",
    }
    st.info(risk_desc[risk_level])

    # ── Parametri di Uscita ─────────────────
    st.divider()
    st.markdown("### 🎯 Parametri di Uscita")
    st.caption("Valori di riferimento per la gestione della posizione.")

    tp_pct = st.slider(
        "Take Profit",
        min_value=10, max_value=100, value=50, step=5, format="%d%%",
        help="Obiettivo di guadagno percentuale per chiudere la posizione in profitto.",
    )
    ts_start = st.slider(
        "Trailing Stop — attivazione",
        min_value=1, max_value=20, value=3, step=1, format="%d%%",
        help="Ribasso % dal massimo raggiunto che attiva il trailing stop.",
    )
    ts_post = st.slider(
        "Trailing Stop — ampiezza",
        min_value=5, max_value=30, value=12, step=1, format="%d%%",
        help="Ampiezza del trailing stop una volta attivato: quanto lasci 'respirare' il titolo prima di uscire.",
    )
    max_days = st.number_input(
        "Max giorni in posizione",
        min_value=30, max_value=1000, value=600, step=10,
        help="Giorni massimi in cui mantenere la posizione aperta, indipendentemente dal segnale.",
    )

    # ── Riepilogo ───────────────────────────
    st.divider()
    st.markdown("### 📋 Riepilogo Attivo")
    st.markdown(
        f'<div class="params-box">'
        f'<strong>— ENTRY —</strong><br>'
        f'EMA({CFG_BASE["EMA_PERIOD"]}) dist &le;{CFG_BASE["EMA_MAX_DIST"]:.0f}%<br>'
        f'TrendScore &gt; {CFG_BASE["LIM_TRENDSCORE"]}<br>'
        f'Stoch [{CFG_BASE["STOCH_MIN"]},{CFG_BASE["STOCH_MAX"]}] K&gt;D<br>'
        f'RSI [{CFG_BASE["RSI_MIN"]},{CFG_BASE["RSI_MAX"]}] '
        f'&uarr;{CFG_BASE["RSI_SLOPE_BARS"]}gg<br>'
        f'GATE: EMA + Trend + Liquidit&agrave; + PSAR (4/4)<br>Min condizioni: <strong>{min_conditions}/6</strong><br>'
        f'Liquidit&agrave;: &ge;{CFG_BASE["MIN_TURNOVER_EUR"]/1e6:.0f}M&euro;/gg<br>'
        f'<br><strong>— EXIT —</strong><br>'
        f'Take Profit: +{tp_pct}%<br>'
        f'Trail attivazione: -{ts_start}%<br>'
        f'Trail ampiezza: -{ts_post}%<br>'
        f'Max durata: {max_days} gg<br>'
        f'<br><strong>— DATI —</strong><br>'
        f'Periodo scaricato: {REQUIRED_DAYS} gg'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Auto-refresh ────────────────────────
    st.divider()
    st.markdown("### 🔄 Aggiornamento")
    auto_refresh = st.checkbox(
        "Auto-aggiornamento",
        value=False,
        help="Aggiorna automaticamente all'intervallo scelto. Consigliato solo durante l'orario di mercato.",
    )
    refresh_mins = 30
    if auto_refresh:
        refresh_mins = st.select_slider(
            "Intervallo (minuti)",
            options=[5, 10, 15, 20, 30, 60],
            value=30,
        )
        if mkt_open:
            st.success(f"⏱ Prossimo aggiornamento tra {refresh_mins} min")
        else:
            st.warning("Mercato chiuso — l'auto-refresh è attivo ma i dati saranno statici")

    if st.button("🔄 Aggiorna ora"):
        st.cache_data.clear()
        st.session_state["prev_signals"] = {}
        st.rerun()

    # Auto-clear cache se cambia MIN_CONDITIONS
    current_params = {"min_conditions": min_conditions}
    if st.session_state["last_params"] != current_params:
        st.cache_data.clear()
        st.session_state["last_params"] = current_params

# ─────────────────────────────────────────────
# BOTTONE PRINCIPALE
# ─────────────────────────────────────────────
col_btn, _ = st.columns([1, 4])
with col_btn:
    avvia = st.button("▶  ANALIZZA SEGNALI", use_container_width=True)

if not avvia and not auto_refresh:
    st.markdown(
        '<div style="text-align:center;padding:3rem;color:#4d5566;">'
        '<div style="font-size:2.5rem;margin-bottom:0.5rem;">📡</div>'
        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.9rem;">'
        'Configura i parametri nel pannello laterale<br>'
        'e premi <strong style="color:#58a6ff;">ANALIZZA SEGNALI</strong>'
        '</div></div>',
        unsafe_allow_html=True
    )
    st.stop()

if not selected_tickers:
    st.warning("Seleziona almeno un ticker.")
    st.stop()

# ─────────────────────────────────────────────
# ANALISI
# ─────────────────────────────────────────────
results_map  = {}
progress_bar = st.progress(0, text="Scarico dati e calcolo indicatori...")
for i, ticker in enumerate(selected_tickers):
    progress_bar.progress(i / len(selected_tickers), text=f"Analisi {ticker}...")
    results_map[ticker] = download_and_analyze(ticker, min_conditions)
progress_bar.progress(1.0, text="✅ Completato!")
progress_bar.empty()

# Rilevamento cambi di stato
prev            = st.session_state["prev_signals"]
changed_tickers = set()
for ticker, data in results_map.items():
    if not data.get("error"):
        new_state = data["setup_active"]
        if ticker in prev and prev[ticker] != new_state:
            changed_tickers.add(ticker)
        prev[ticker] = new_state
st.session_state["prev_signals"] = prev

# ─────────────────────────────────────────────
# ORDINAMENTO
# ─────────────────────────────────────────────
def sort_key(item):
    t, d = item
    if d.get("error"):
        return (9, 0, t)
    chg = 0 if t in changed_tickers else 1
    if ordine == "Setup ON prima → Score":
        return (chg, 0 if d["setup_active"] else 1, -d["score"], t)
    elif ordine == "Score decrescente":
        return (chg, -d["score"], t)
    else:
        return (0, 0, t)

sorted_results = sorted(results_map.items(), key=sort_key)

# ─────────────────────────────────────────────
# RIEPILOGO IN CIMA
# ─────────────────────────────────────────────
n_on      = sum(1 for _, d in sorted_results if not d.get("error") and d.get("setup_active"))
n_off     = sum(1 for _, d in sorted_results if not d.get("error") and not d.get("setup_active"))
n_err     = sum(1 for _, d in sorted_results if d.get("error"))
n_changed = len(changed_tickers)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("✅ BUY",    n_on)
c2.metric("❌ SELL",   n_off)
c3.metric("⚡ Cambi stato", n_changed)
c4.metric("⚠️ Errori",     n_err)
c5.metric("🕒 Aggiornato",  datetime.now().strftime("%H:%M:%S"))

if changed_tickers:
    st.info(f"⚡ Cambio segnale rilevato su: **{', '.join(sorted(changed_tickers))}**")

st.markdown('<div class="section-title">SEGNALI PER TICKER</div>',
            unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARDS — due colonne
# ─────────────────────────────────────────────
left_items  = sorted_results[0::2]
right_items = sorted_results[1::2]

col_l, col_r = st.columns(2)
with col_l:
    for ticker, data in left_items:
        render_ticker_card(ticker, ALL_TICKERS.get(ticker, ticker),
                           data, changed=(ticker in changed_tickers))
with col_r:
    for ticker, data in right_items:
        render_ticker_card(ticker, ALL_TICKERS.get(ticker, ticker),
                           data, changed=(ticker in changed_tickers))

# ─────────────────────────────────────────────
# FOOTER (opzionale, visibile solo se non nascosto)
# ─────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#4d5566;font-size:0.72rem;font-family:monospace;'>"
    "Momentum Setup Scanner v3.6.1 · Solo a scopo informativo · "
    "Non costituisce consulenza finanziaria"
    "</div>",
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# AUTO-REFRESH (in fondo per non bloccare il rendering)
# ─────────────────────────────────────────────
if auto_refresh:
    time.sleep(refresh_mins * 60)
    st.cache_data.clear()
    st.rerun()
