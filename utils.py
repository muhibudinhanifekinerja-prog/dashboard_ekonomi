"""
Utilitas, konstanta, dan referensi HET/HAP untuk TPID Dashboard
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ── BULAN ──────────────────────────────────────────────────────────────────────
MONTHS_ID = ["Januari","Februari","Maret","April","Mei","Juni",
             "Juli","Agustus","September","Oktober","November","Desember"]

# ── HET / HAP REFERENCE ────────────────────────────────────────────────────────
HET_HAP = {
    "Beras Medium":      {"het": 13500, "hap": None,  "dasar": "Perbadan 299/2025",  "satuan": "kg"},
    "Beras Premium":     {"het": 14900, "hap": None,  "dasar": "Perbadan 299/2025",  "satuan": "kg"},
    "Telur Ayam Ras":    {"het": None,  "hap": 27000, "dasar": "Perbadan 6/2024",    "satuan": "kg"},
    "Daging Ayam Ras":   {"het": None,  "hap": 40000, "dasar": "Perbadan 6/2024",    "satuan": "kg"},
    "Bawang Merah":      {"het": None,  "hap": 41500, "dasar": "Perbadan 12/2024",   "satuan": "kg"},
    "Bawang Putih":      {"het": None,  "hap": 41500, "dasar": "Perbadan 12/2024",   "satuan": "kg"},
    "Cabai Rawit Merah": {"het": None,  "hap": 57000, "dasar": "Perbadan 12/2024",   "satuan": "kg"},
    "Cabai Merah Besar": {"het": None,  "hap": 55000, "dasar": "Perbadan 12/2024",   "satuan": "kg"},
    "Daging Sapi":       {"het": None,  "hap": 150000,"dasar": "Perbadan 12/2024",   "satuan": "kg"},
    "Gula Konsumsi":     {"het": 17500, "hap": None,  "dasar": "Perbadan 12/2024",   "satuan": "kg"},
    "Minyak Goreng":     {"het": 15700, "hap": None,  "dasar": "Permendag Kemendag", "satuan": "liter"},
}

def get_het_hap(nama_komoditas: str) -> dict:
    """Cari HET/HAP berdasarkan nama komoditas (case-insensitive partial match)."""
    nama = nama_komoditas.lower()
    for k, v in HET_HAP.items():
        if any(w in nama for w in k.lower().split()):
            return {"nama": k, **v}
    return {"het": None, "hap": None, "dasar": "-", "satuan": "-"}

def get_ref_value(nama_komoditas: str) -> tuple:
    """Return (ref_value, ref_type) — pilih HET jika ada, lalu HAP."""
    info = get_het_hap(nama_komoditas)
    if info["het"]:
        return info["het"], "HET"
    if info["hap"]:
        return info["hap"], "HAP"
    return None, None

def status_harga(harga: float, ref_val: float) -> str:
    if ref_val is None or harga == 0:
        return "—"
    ratio = harga / ref_val
    if ratio >= 1.0:
        return "🔴 Melebihi"
    if ratio >= 0.9:
        return "🟡 Mendekati"
    return "🟢 Normal"

def fmt_rp(val) -> str:
    try:
        return f"Rp {int(val):,}".replace(",", ".")
    except Exception:
        return "—"

def fmt_pct(val, decimals=2) -> str:
    try:
        sign = "+" if float(val) >= 0 else ""
        return f"{sign}{float(val):.{decimals}f}%"
    except Exception:
        return "—"

# ── PLOTLY THEME ───────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,34,0.5)",
    font=dict(color="#e6edf3", family="Plus Jakarta Sans, sans-serif", size=12),
    xaxis=dict(gridcolor="#30363d", linecolor="#30363d", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#30363d", linecolor="#30363d", tickfont=dict(size=11)),
    legend=dict(bgcolor="rgba(22,27,34,0.8)", bordercolor="#30363d", borderwidth=1, font=dict(size=11)),
    margin=dict(l=20, r=20, t=30, b=20),
    hovermode="x unified",
)

COLOR_PALETTE = [
    "#2ea043", "#388bfd", "#d29922", "#da3633", "#8957e5",
    "#0e9488", "#f97316", "#ec4899", "#06b6d4", "#84cc16",
]

def make_line_chart(df_pivot: pd.DataFrame, title: str, y_label: str = "Harga (Rp)") -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(df_pivot.columns):
        fig.add_trace(go.Scatter(
            x=df_pivot.index, y=df_pivot[col], name=col,
            mode="lines+markers",
            line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=2),
            marker=dict(size=4),
        ))
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font=dict(size=14), x=0))
    fig.update_yaxes(title_text=y_label)
    return fig

def make_bar_chart(x, y, colors=None, title="", orientation="v") -> go.Figure:
    fig = go.Figure(go.Bar(
        x=x if orientation == "v" else y,
        y=y if orientation == "v" else x,
        marker_color=colors or COLOR_PALETTE[0],
        orientation=orientation,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font=dict(size=14), x=0))
    return fig

# ── HARI BESAR KEAGAMAAN ───────────────────────────────────────────────────────
IDUL_FITRI = {
    2020: "2020-05-24", 2021: "2021-05-13", 2022: "2022-05-02",
    2023: "2023-04-22", 2024: "2024-04-10", 2025: "2025-03-31",
}
NATAL = {yr: f"{yr}-12-25" for yr in range(2019, 2026)}
TAHUN_BARU = {yr: f"{yr}-01-01" for yr in range(2020, 2026)}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:wght@700;800&display=swap');

:root {
  --bg: #0d1117; --bg2: #161b22; --bg3: #21262d; --bg4: #30363d;
  --border: #30363d; --border2: #484f58;
  --text: #e6edf3; --text2: #8b949e; --text3: #6e7681;
  --primary: #2ea043; --primary2: #3fb950;
  --accent: #d29922; --accent2: #e3b341;
  --blue: #1f6feb; --blue2: #388bfd;
  --red: #da3633; --red2: #f85149;
  --purple: #8957e5; --teal: #0e9488; --teal2: #14b8a6;
}
html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}
/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}
/* Metrics */
[data-testid="metric-container"] {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: var(--text2) !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: .8px; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 800 !important; font-family: 'Playfair Display', serif !important; }
[data-testid="stMetricDelta"] { font-size: 12px !important; }
/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 8px; }
/* Tabs */
[data-baseweb="tab-list"] { background: var(--bg2) !important; border-bottom: 1px solid var(--border) !important; border-radius: 8px 8px 0 0; padding: 4px; gap: 2px; }
[data-baseweb="tab"] { background: transparent !important; color: var(--text2) !important; border-radius: 6px; font-size: 13px !important; }
[aria-selected="true"] { background: var(--bg3) !important; color: var(--primary2) !important; }
/* Buttons */
.stButton > button {
  background: var(--primary) !important; color: #fff !important;
  border: none !important; border-radius: 8px !important;
  font-weight: 600 !important; font-family: inherit !important;
}
.stButton > button:hover { background: var(--primary2) !important; }
/* Selectbox */
[data-baseweb="select"] > div { background: var(--bg3) !important; border-color: var(--border2) !important; color: var(--text) !important; border-radius: 6px !important; }
/* Input */
input[type="number"], input[type="text"], textarea {
  background: var(--bg3) !important; color: var(--text) !important;
  border-color: var(--border2) !important; border-radius: 6px !important;
}
/* Section title */
.section-title {
  font-size: 13px; font-weight: 700; color: var(--text2);
  text-transform: uppercase; letter-spacing: .8px;
  margin: 20px 0 12px; display: flex; align-items: center; gap: 8px;
  border-bottom: 1px solid var(--border); padding-bottom: 8px;
}
/* Info card */
.info-card {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 12px; padding: 16px 20px; margin-bottom: 12px;
}
/* Badge */
.badge-up   { background: rgba(248,81,73,.15); color: #f85149; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; display: inline-block; }
.badge-down { background: rgba(46,160,67,.15); color: #3fb950; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; display: inline-block; }
.badge-neutral { background: rgba(139,148,158,.1); color: #8b949e; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; display: inline-block; }
/* Sidebar logo */
.sidebar-logo { font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 800; color: var(--accent2); }
.sidebar-sub  { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: .5px; }
/* Alert / Toast */
.stAlert { border-radius: 8px !important; }
/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 1200px; }
/* Expander */
[data-testid="stExpander"] { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
</style>
"""
