"""
TPID Dashboard — Kab. Pekalongan
Aplikasi Streamlit untuk monitoring harga komoditas dan inflasi daerah
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import calendar

# Page config — HARUS pertama sebelum import lain
st.set_page_config(
    page_title="TPID Dashboard — Kab. Pekalongan",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils import CSS, MONTHS_ID, HET_HAP, fmt_rp, fmt_pct, PLOTLY_LAYOUT, \
                  COLOR_PALETTE, make_line_chart, get_ref_value, status_harga, \
                  IDUL_FITRI, NATAL, TAHUN_BARU
import database as db

st.markdown(CSS, unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "df_harga" not in st.session_state:
    st.session_state.df_harga = None
if "df_inflasi" not in st.session_state:
    st.session_state.df_inflasi = None
if "df_komoditas" not in st.session_state:
    st.session_state.df_komoditas = None
if "df_pasar" not in st.session_state:
    st.session_state.df_pasar = None
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None

@st.cache_data(ttl=300)
def load_all_data():
    harga    = db.get_harga_harian()
    inflasi  = db.get_inflasi()
    komoditas = db.get_komoditas()
    pasar    = db.get_pasar()
    return harga, inflasi, komoditas, pasar

def refresh_data():
    load_all_data.clear()
    harga, inflasi, komoditas, pasar = load_all_data()
    st.session_state.df_harga     = harga
    st.session_state.df_inflasi   = inflasi
    st.session_state.df_komoditas = komoditas
    st.session_state.df_pasar     = pasar
    st.session_state.last_refresh = datetime.now().strftime("%H:%M:%S")

# Load awal
if st.session_state.df_harga is None:
    harga, inflasi, komoditas, pasar = load_all_data()
    st.session_state.df_harga     = harga
    st.session_state.df_inflasi   = inflasi
    st.session_state.df_komoditas = komoditas
    st.session_state.df_pasar     = pasar
    st.session_state.last_refresh = datetime.now().strftime("%H:%M:%S")

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 16px">
        <div class="sidebar-logo">📈 TPID Dashboard</div>
        <div class="sidebar-sub">Kab. Pekalongan · Jawa Tengah</div>
        <div style="margin-top:8px">
            <span style="background:#2ea043;color:#fff;font-size:9px;padding:3px 10px;
            border-radius:20px;font-weight:700;letter-spacing:.5px">▸ LIVE DATA</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**🧭 Navigasi**")
    page = st.radio(
        "",
        options=["🏠 Beranda", "🌙 Analisis HBK", "📊 Detail Harga",
                 "🗄️ Manajemen Data", "📋 Laporan"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("🔄 Refresh", use_container_width=True):
            refresh_data()
            st.success("Data diperbarui!")
    with col_r2:
        st.markdown(
            f"<div style='font-size:10px;color:#6e7681;padding-top:8px'>⏱ {st.session_state.last_refresh}</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:11px;color:#6e7681'>v2.0 · TPID Kab. Pekalongan<br>"
        f"📅 {datetime.now().strftime('%d %b %Y')}</div>",
        unsafe_allow_html=True
    )

# Shortcut variabel
df_h  = st.session_state.df_harga
df_i  = st.session_state.df_inflasi
df_k  = st.session_state.df_komoditas
df_p  = st.session_state.df_pasar

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BERANDA
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Beranda":
    st.markdown("""
    <div class="page-header" style="margin-bottom:24px">
        <div style="font-size:12px;color:#6e7681;margin-bottom:4px">Dashboard</div>
        <h1 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:800;margin:0">
            📈 Beranda Ekonomi Daerah
        </h1>
        <p style="color:#8b949e;font-size:14px;margin-top:6px">
            Ringkasan inflasi, kurs, dan pergerakan harga komoditas strategis terkini.
            Inflasi Kab. Pekalongan mengikuti Indikator Kota Tegal.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── INFLASI CARDS ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 Indikator Inflasi Terkini</div>', unsafe_allow_html=True)

    if df_i is not None and not df_i.empty:
        now_y = datetime.now().year
        now_m = datetime.now().month

        def get_latest_inflasi(wilayah_filter, level=None):
            if level:
                sub = df_i[df_i["level_wilayah"] == level]
            else:
                sub = df_i[df_i["nama_wilayah"].str.contains(wilayah_filter, case=False, na=False)]
            if sub.empty:
                return None
            return sub.sort_values(["tahun", "bulan"], ascending=False).iloc[0]

        kota  = get_latest_inflasi("Tegal", "kota")
        jateng = get_latest_inflasi("Jawa Tengah", "provinsi")
        nas   = get_latest_inflasi("Nasional", "nasional")

        infl_data = [
            ("🏙️ Kota Tegal", kota,  "#388bfd"),
            ("🗺️ Jawa Tengah", jateng, "#14b8a6"),
            ("🇮🇩 Nasional",   nas,   "#d29922"),
        ]
        cols = st.columns(3)
        for ci, (label, row, color) in enumerate(infl_data):
            with cols[ci]:
                if row is not None:
                    yoy = row.get("inflasi_yoy", 0) or 0
                    mtm = row.get("inflasi_mtm", 0) or 0
                    ytd = row.get("inflasi_ytd", 0) or 0
                    bln = MONTHS_ID[int(row["bulan"]) - 1]
                    thn = int(row["tahun"])
                    delta_color = "#f85149" if yoy >= 0 else "#3fb950"
                    st.markdown(f"""
                    <div class="info-card" style="border-left: 3px solid {color}">
                        <div style="font-size:11px;color:#6e7681;text-transform:uppercase;
                            letter-spacing:.8px;font-weight:600;margin-bottom:8px">{label}</div>
                        <div style="font-family:'Playfair Display',serif;font-size:42px;
                            font-weight:800;color:{color};line-height:1">{fmt_pct(yoy)}</div>
                        <div style="font-size:12px;color:#8b949e;margin-top:4px">YoY · {bln} {thn}</div>
                        <div style="display:flex;gap:16px;margin-top:14px;padding-top:14px;
                            border-top:1px solid #30363d">
                            <div style="text-align:center;flex:1">
                                <div style="font-size:16px;font-weight:700;color:{delta_color}">{fmt_pct(mtm)}</div>
                                <div style="font-size:10px;color:#6e7681;text-transform:uppercase">MtM</div>
                            </div>
                            <div style="text-align:center;flex:1">
                                <div style="font-size:16px;font-weight:700">{fmt_pct(ytd)}</div>
                                <div style="font-size:10px;color:#6e7681;text-transform:uppercase">YtD</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="info-card" style="border-left: 3px solid {color}">
                        <div style="font-size:11px;color:#6e7681;text-transform:uppercase;
                            letter-spacing:.8px;font-weight:600;margin-bottom:8px">{label}</div>
                        <div style="color:#6e7681;font-size:14px">— Data belum tersedia —</div>
                    </div>""", unsafe_allow_html=True)
    else:
        st.info("ℹ️ Belum ada data inflasi. Tambahkan di halaman Manajemen Data.")

    # ── HARGA KOMODITAS HARI INI ────────────────────────────────────────────────
    st.markdown('<div class="section-title" style="margin-top:28px">🛒 Harga Komoditas Terkini</div>',
                unsafe_allow_html=True)

    if df_h is not None and not df_h.empty:
        # Ambil harga terbaru per komoditas
        latest_date = df_h["tanggal"].max()
        df_today = df_h[df_h["tanggal"] == latest_date].copy()

        # Rata-rata per komoditas
        df_avg_today = df_today.groupby(["nama_komoditas", "satuan"])["harga"].mean().reset_index()

        # Harga kemarin untuk perbandingan
        prev_date = df_h[df_h["tanggal"] < latest_date]["tanggal"].max() if len(df_h["tanggal"].unique()) > 1 else None
        df_prev = df_h[df_h["tanggal"] == prev_date].groupby("nama_komoditas")["harga"].mean() if prev_date else None

        st.caption(f"📅 Data per: {latest_date.strftime('%d %B %Y')} | Rata-rata semua pasar")

        cols = st.columns(4)
        for idx, row in df_avg_today.iterrows():
            nama = row["nama_komoditas"]
            harga_now = row["harga"]
            satuan = row["satuan"]
            ref_val, ref_type = get_ref_value(nama)
            status = status_harga(harga_now, ref_val)

            # Delta vs kemarin
            delta_txt = ""
            delta_color = "#8b949e"
            if df_prev is not None and nama in df_prev.index:
                delta = harga_now - df_prev[nama]
                pct = (delta / df_prev[nama] * 100) if df_prev[nama] > 0 else 0
                sign = "▲" if delta > 0 else "▼" if delta < 0 else "▬"
                delta_color = "#f85149" if delta > 0 else "#3fb950" if delta < 0 else "#8b949e"
                delta_txt = f"{sign} {fmt_pct(pct)}"

            # HET bar
            het_pct = min(int(harga_now / ref_val * 100), 120) if ref_val else None
            het_color = "#da3633" if het_pct and het_pct >= 100 else "#d29922" if het_pct and het_pct >= 90 else "#2ea043"
            het_bar_html = ""
            if het_pct is not None:
                het_bar_html = f"""
                <div style="margin-top:8px">
                    <div style="display:flex;justify-content:space-between;font-size:10px;color:#6e7681;margin-bottom:4px">
                        <span>{ref_type}: {fmt_rp(ref_val)}</span><span>{min(het_pct,120)}%</span>
                    </div>
                    <div style="height:4px;background:#30363d;border-radius:4px;overflow:hidden">
                        <div style="width:{min(het_pct,100)}%;height:100%;background:{het_color};border-radius:4px"></div>
                    </div>
                </div>"""

            with cols[idx % 4]:
                st.markdown(f"""
                <div class="info-card" style="margin-bottom:8px">
                    <div style="font-size:12px;color:#8b949e;font-weight:500">{nama}</div>
                    <div style="font-size:22px;font-weight:800;margin:4px 0">{fmt_rp(harga_now)}</div>
                    <div style="font-size:10px;color:#6e7681">per {satuan}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px">
                        <span style="font-size:11px;font-weight:600;color:{delta_color}">{delta_txt}</span>
                        <span style="font-size:10px">{status}</span>
                    </div>
                    {het_bar_html}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Belum ada data harga. Tambahkan di halaman Manajemen Data.")

    # ── TREND HARGA CHART ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title" style="margin-top:28px">📉 Tren Harga Komoditas</div>',
                unsafe_allow_html=True)

    if df_h is not None and not df_h.empty and df_k is not None and not df_k.empty:
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        with col_f1:
            all_kom = sorted(df_h["nama_komoditas"].dropna().unique().tolist())
            sel_kom = st.multiselect("Komoditas", all_kom,
                                     default=all_kom[:3] if len(all_kom) >= 3 else all_kom,
                                     key="beranda_kom")
        with col_f2:
            periode = st.selectbox("Periode", ["30 Hari", "60 Hari", "90 Hari", "6 Bulan", "1 Tahun"],
                                   key="beranda_period")
        with col_f3:
            show_het = st.checkbox("Tampilkan HET/HAP", value=True, key="beranda_het")

        days_map = {"30 Hari": 30, "60 Hari": 60, "90 Hari": 90,
                    "6 Bulan": 180, "1 Tahun": 365}
        n_days = days_map[periode]
        cutoff = datetime.now() - timedelta(days=n_days)

        if sel_kom:
            df_chart = df_h[
                (df_h["nama_komoditas"].isin(sel_kom)) &
                (df_h["tanggal"] >= cutoff)
            ].copy()
            df_avg = df_chart.groupby(["tanggal", "nama_komoditas"])["harga"].mean().reset_index()
            df_pivot = df_avg.pivot(index="tanggal", columns="nama_komoditas", values="harga")

            fig = go.Figure()
            for i, col in enumerate(df_pivot.columns):
                fig.add_trace(go.Scatter(
                    x=df_pivot.index, y=df_pivot[col], name=col,
                    mode="lines", line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=2),
                ))
                if show_het:
                    rv, rt = get_ref_value(col)
                    if rv:
                        fig.add_hline(y=rv, line_dash="dot",
                                      line_color=COLOR_PALETTE[i % len(COLOR_PALETTE)],
                                      opacity=0.4,
                                      annotation_text=f"{col} {rt}",
                                      annotation_font_size=9)
            fig.update_layout(**PLOTLY_LAYOUT, height=320)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pilih minimal satu komoditas")

    # ── TABEL INFLASI ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title" style="margin-top:28px">📋 Riwayat Inflasi Semua Wilayah</div>',
                unsafe_allow_html=True)

    if df_i is not None and not df_i.empty:
        df_show = df_i.copy()
        df_show["Bulan"] = df_show["bulan"].apply(lambda x: MONTHS_ID[int(x)-1])
        df_show["MtM (%)"] = df_show["inflasi_mtm"].apply(fmt_pct)
        df_show["YtD (%)"] = df_show["inflasi_ytd"].apply(fmt_pct)
        df_show["YoY (%)"] = df_show["inflasi_yoy"].apply(fmt_pct)
        df_show = df_show.rename(columns={
            "tahun": "Tahun", "nama_wilayah": "Wilayah", "level_wilayah": "Level"
        })
        st.dataframe(
            df_show[["Tahun", "Bulan", "Wilayah", "Level", "MtM (%)", "YtD (%)", "YoY (%)"]],
            use_container_width=True, hide_index=True, height=280,
        )

    # ── HET/HAP REFERENSI ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title" style="margin-top:28px">📋 Referensi HET & HAP</div>',
                unsafe_allow_html=True)
    with st.expander("📊 Lihat Tabel Detail HET/HAP"):
        rows_het = []
        for nama, info in HET_HAP.items():
            rows_het.append({
                "Komoditas": nama, "Satuan": info["satuan"],
                "HET (Rp)": fmt_rp(info["het"]) if info["het"] else "—",
                "HAP (Rp)": fmt_rp(info["hap"]) if info["hap"] else "—",
                "Dasar Hukum": info["dasar"],
            })
        st.dataframe(pd.DataFrame(rows_het), use_container_width=True, hide_index=True)
        st.caption("⚠️ Komoditas tanpa regulasi HET/HAP resmi tidak ditampilkan indikator ini.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALISIS HBK
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌙 Analisis HBK":
    st.markdown("""
    <div style="margin-bottom:24px">
        <div style="font-size:12px;color:#6e7681;margin-bottom:4px">Analisis</div>
        <h1 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:800;margin:0">
            🌙 Analisis Hari Besar Keagamaan (HBK)
        </h1>
        <p style="color:#8b949e;font-size:14px;margin-top:6px">
            Pola pergerakan harga komoditas di sekitar Idulfitri, Natal, dan Tahun Baru
        </p>
    </div>
    """, unsafe_allow_html=True)

    if df_h is None or df_h.empty:
        st.warning("⚠️ Belum ada data harga. Silakan tambahkan di halaman Manajemen Data.")
    else:
        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1])
        with col_f1:
            all_kom = sorted(df_h["nama_komoditas"].dropna().unique().tolist())
            hbk_kom = st.selectbox("Komoditas", all_kom, key="hbk_kom")
        with col_f2:
            hbk_window = st.selectbox("Window", [14, 21, 30, 45, 60], index=2, key="hbk_win")
        with col_f3:
            hbk_type = st.selectbox("Hari Besar", ["Idulfitri", "Natal", "Tahun Baru"], key="hbk_type")
        with col_f4:
            hbk_tahun = st.selectbox(
                "Tahun Detail",
                sorted((IDUL_FITRI if hbk_type == "Idulfitri" else NATAL if hbk_type == "Natal" else TAHUN_BARU).keys(), reverse=True),
                key="hbk_year"
            )

        HBK_MAP = {"Idulfitri": IDUL_FITRI, "Natal": NATAL, "Tahun Baru": TAHUN_BARU}
        hbk_dates = HBK_MAP[hbk_type]

        tab1, tab2 = st.tabs(["📊 Infografis Historis", "🔍 Detail Tahun Terpilih"])

        with tab1:
            st.markdown(f"**Perbandingan Kenaikan Harga Pra-Pasca {hbk_type} — Multi-Tahun**")
            df_kom = df_h[df_h["nama_komoditas"] == hbk_kom].copy()
            df_kom["tanggal"] = pd.to_datetime(df_kom["tanggal"])
            df_kom_avg = df_kom.groupby("tanggal")["harga"].mean().reset_index()
            df_kom_avg = df_kom_avg.set_index("tanggal")["harga"]

            bars_pre, bars_post, years_ok = [], [], []
            for yr, h_date_str in sorted(hbk_dates.items()):
                h_date = pd.to_datetime(h_date_str)
                pre = df_kom_avg[
                    (df_kom_avg.index >= h_date - timedelta(days=hbk_window)) &
                    (df_kom_avg.index < h_date)
                ]
                post = df_kom_avg[
                    (df_kom_avg.index > h_date) &
                    (df_kom_avg.index <= h_date + timedelta(days=hbk_window))
                ]
                if len(pre) >= 3 and len(post) >= 3:
                    bars_pre.append(pre.mean())
                    bars_post.append(post.mean())
                    years_ok.append(str(yr))

            if years_ok:
                fig_hist = go.Figure()
                fig_hist.add_trace(go.Bar(name=f"H-{hbk_window} → H-1", x=years_ok, y=bars_pre,
                                          marker_color="#388bfd"))
                fig_hist.add_trace(go.Bar(name=f"H+1 → H+{hbk_window}", x=years_ok, y=bars_post,
                                          marker_color="#f85149"))
                fig_hist.update_layout(**PLOTLY_LAYOUT, height=280, barmode="group",
                                       title=f"{hbk_kom} — Rata-rata Harga Pra vs Pasca {hbk_type}")
                st.plotly_chart(fig_hist, use_container_width=True)

                # Summary cards
                hist_cols = st.columns(len(years_ok))
                for ci, yr in enumerate(years_ok):
                    pre_v = bars_pre[ci]
                    post_v = bars_post[ci]
                    chg = (post_v - pre_v) / pre_v * 100 if pre_v > 0 else 0
                    delta_color = "#f85149" if chg > 0 else "#3fb950"
                    with hist_cols[ci]:
                        st.markdown(f"""
                        <div class="info-card" style="text-align:center">
                            <div style="font-size:11px;color:#6e7681">{yr}</div>
                            <div style="font-size:18px;font-weight:800;color:{delta_color};margin:4px 0">
                                {fmt_pct(chg)}</div>
                            <div style="font-size:10px;color:#8b949e">Pra→Pasca</div>
                        </div>""", unsafe_allow_html=True)
            else:
                st.info("📭 Data tidak cukup untuk analisis historis komoditas ini.")

        with tab2:
            h_date_str = hbk_dates.get(hbk_tahun)
            if h_date_str:
                h_date = pd.to_datetime(h_date_str)
                df_kom = df_h[df_h["nama_komoditas"] == hbk_kom].copy()
                df_kom["tanggal"] = pd.to_datetime(df_kom["tanggal"])
                df_kom_avg = df_kom.groupby("tanggal")["harga"].mean()

                mask = (df_kom_avg.index >= h_date - timedelta(days=hbk_window)) & \
                       (df_kom_avg.index <= h_date + timedelta(days=hbk_window))
                df_window = df_kom_avg[mask]

                if not df_window.empty:
                    # Info box
                    avg_pre  = df_kom_avg[(df_kom_avg.index < h_date)].tail(hbk_window).mean()
                    avg_post = df_kom_avg[(df_kom_avg.index > h_date)].head(hbk_window).mean()
                    chg = (avg_post - avg_pre) / avg_pre * 100 if avg_pre > 0 else 0

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Rata-rata Pra", fmt_rp(avg_pre))
                    c2.metric("Rata-rata Pasca", fmt_rp(avg_post),
                              delta=fmt_pct(chg))
                    c3.metric("Tertinggi", fmt_rp(df_window.max()))
                    c4.metric("Terendah",  fmt_rp(df_window.min()))

                    fig_detail = go.Figure()
                    # Area sebelum
                    pre_mask = df_window.index < h_date
                    fig_detail.add_trace(go.Scatter(
                        x=df_window[pre_mask].index, y=df_window[pre_mask].values,
                        name="Pra-HBK", mode="lines+markers",
                        line=dict(color="#388bfd", width=2), fill="tozeroy",
                        fillcolor="rgba(56,139,253,0.08)"
                    ))
                    post_mask = df_window.index >= h_date
                    fig_detail.add_trace(go.Scatter(
                        x=df_window[post_mask].index, y=df_window[post_mask].values,
                        name="Pasca-HBK", mode="lines+markers",
                        line=dict(color="#f85149", width=2), fill="tozeroy",
                        fillcolor="rgba(248,81,73,0.08)"
                    ))
                    fig_detail.add_vline(x=str(h_date), line_dash="dash",
                                         line_color="#d29922", opacity=0.8,
                                         annotation_text=f"H0 — {hbk_type} {hbk_tahun}",
                                         annotation_font_color="#e3b341")
                    fig_detail.update_layout(**PLOTLY_LAYOUT, height=300,
                                             title=f"{hbk_kom} — ±{hbk_window} hari sekitar {hbk_type} {hbk_tahun}")
                    st.plotly_chart(fig_detail, use_container_width=True)

                    # Tabel detail
                    rows_d = []
                    h1_price = df_kom_avg.get(h_date, None)
                    for tgl, harga in df_window.items():
                        delta_d = int(( tgl - h_date).days)
                        keterangan = "H0 (Hari H)" if delta_d == 0 else \
                                     f"H-{abs(delta_d)}" if delta_d < 0 else f"H+{delta_d}"
                        delta_vs = ((harga - h1_price) / h1_price * 100) if h1_price and h1_price > 0 else None
                        rows_d.append({
                            "Tanggal": tgl.strftime("%d %b %Y"),
                            "H- / H+": keterangan,
                            "Harga (Rp)": fmt_rp(harga),
                            "Δ vs H0": fmt_pct(delta_vs) if delta_vs is not None else "—",
                        })
                    st.dataframe(pd.DataFrame(rows_d), use_container_width=True, hide_index=True)
                else:
                    st.info("📭 Tidak ada data harga untuk komoditas dan tahun yang dipilih.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DETAIL HARGA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Detail Harga":
    st.markdown("""
    <div style="margin-bottom:24px">
        <div style="font-size:12px;color:#6e7681;margin-bottom:4px">Analisis</div>
        <h1 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:800;margin:0">
            📊 Analisis Detail Perubahan Harga
        </h1>
        <p style="color:#8b949e;font-size:14px;margin-top:6px">
            Tabel harga harian per komoditas dan Indeks Perkembangan Harga (IPH) mingguan
        </p>
    </div>
    """, unsafe_allow_html=True)

    if df_h is None or df_h.empty:
        st.warning("⚠️ Belum ada data harga.")
    else:
        # Filter bar
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([2, 1, 1, 1, 1])
        all_kom_det = sorted(df_h["nama_komoditas"].dropna().unique().tolist())
        all_years = sorted(df_h["tanggal"].dt.year.unique(), reverse=True)
        with col_f1:
            sel_kom_det = st.multiselect("Komoditas", all_kom_det, default=all_kom_det[:5], key="det_kom")
        with col_f2:
            sel_year_det = st.selectbox("Tahun", all_years, key="det_year")
        with col_f3:
            sel_month_det = st.selectbox("Bulan", range(1, 13),
                                         format_func=lambda x: MONTHS_ID[x-1], key="det_month",
                                         index=datetime.now().month - 1)
        with col_f4:
            show_het_det = st.checkbox("Tampilkan HET/HAP", value=True, key="det_het")
        with col_f5:
            st.write("")
            if st.button("🔍 Tampilkan", key="det_btn"):
                st.rerun()

        # Filter data
        df_det = df_h[
            (df_h["tanggal"].dt.year == sel_year_det) &
            (df_h["tanggal"].dt.month == sel_month_det)
        ].copy()

        if sel_kom_det:
            df_det = df_det[df_det["nama_komoditas"].isin(sel_kom_det)]

        if df_det.empty:
            st.info("📭 Tidak ada data untuk filter yang dipilih.")
        else:
            # Summary cards
            df_avg_det = df_det.groupby("nama_komoditas")["harga"].agg(["mean", "min", "max", "std"]).reset_index()
            st.markdown('<div class="section-title">📊 Ringkasan Statistik</div>', unsafe_allow_html=True)
            ccols = st.columns(4)
            ccols[0].metric("Total Komoditas", len(df_avg_det))
            ccols[1].metric("Harga Rata-rata", fmt_rp(df_avg_det["mean"].mean()))
            over_het = sum(1 for _, r in df_avg_det.iterrows()
                           if get_ref_value(r["nama_komoditas"])[0] and
                              r["mean"] >= get_ref_value(r["nama_komoditas"])[0])
            ccols[2].metric("Melebihi HET/HAP", f"{over_het} komoditas")
            ccols[3].metric("Total Entri Data", len(df_det))

            # PIVOT TABLE harga harian
            st.markdown('<div class="section-title" style="margin-top:24px">📅 Data Harga Harian (Pivot)</div>',
                        unsafe_allow_html=True)

            df_avg_daily = df_det.groupby(["tanggal", "nama_komoditas"])["harga"].mean().reset_index()
            df_pivot = df_avg_daily.pivot(index="nama_komoditas", columns="tanggal", values="harga")
            df_pivot.columns = [c.strftime("%d") + f"\n{['Sen','Sel','Rab','Kam','Jum','Sab','Min'][c.weekday()]}"
                                for c in df_pivot.columns]

            st.caption(
                "🔴 Melebihi HET/HAP &nbsp;|&nbsp; 🟡 Mendekati HET/HAP (≥90%) &nbsp;|&nbsp; ⬜ Data kosong"
            )

            def style_pivot(val, nama_kom=""):
                if pd.isna(val) or val == 0:
                    return "color: #6e7681; font-style: italic"
                return ""

            st.dataframe(
                df_pivot.round(0).astype("Int64", errors="ignore"),
                use_container_width=True, height=min(60 + len(df_pivot) * 35, 480),
            )

            # IPH MINGGUAN
            st.markdown('<div class="section-title" style="margin-top:24px">📊 IPH Mingguan</div>',
                        unsafe_allow_html=True)

            df_avg_daily2 = df_det.groupby(["tanggal", "nama_komoditas"])["harga"].mean().reset_index()
            df_avg_daily2["week"] = df_avg_daily2["tanggal"].dt.isocalendar().week.astype(int)
            df_week = df_avg_daily2.groupby(["week", "nama_komoditas"])["harga"].mean().reset_index()

            weeks = sorted(df_week["week"].unique())
            iph_rows = []
            for kom in df_avg_det["nama_komoditas"]:
                row_data = {"Komoditas": kom}
                prev_avg = None
                for wk in weeks:
                    sub = df_week[(df_week["week"] == wk) & (df_week["nama_komoditas"] == kom)]
                    avg = sub["harga"].mean() if not sub.empty else None
                    iph = ((avg - prev_avg) / prev_avg * 100) if (avg and prev_avg and prev_avg > 0) else None
                    row_data[f"Mg{wk} Rata"] = fmt_rp(avg) if avg else "—"
                    row_data[f"Mg{wk} IPH"]  = fmt_pct(iph) if iph else "—"
                    prev_avg = avg
                iph_rows.append(row_data)

            if iph_rows:
                st.dataframe(pd.DataFrame(iph_rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MANAJEMEN DATA (CRUD)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗄️ Manajemen Data":
    st.markdown("""
    <div style="margin-bottom:24px">
        <div style="font-size:12px;color:#6e7681;margin-bottom:4px">Kelola Data</div>
        <h1 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:800;margin:0">
            🗄️ Manajemen Data
        </h1>
        <p style="color:#8b949e;font-size:14px;margin-top:6px">
            Input, edit, dan hapus data harga harian, inflasi, komoditas, dan pasar
        </p>
    </div>
    """, unsafe_allow_html=True)

    crud_tab = st.tabs(["💰 Harga Harian", "📈 Inflasi", "🛒 Komoditas", "🏪 Pasar"])

    # ── TAB: HARGA HARIAN ────────────────────────────────────────────────────
    with crud_tab[0]:
        col_form, col_tbl = st.columns([1, 2])
        with col_form:
            st.markdown("**➕ Tambah Harga Harian**")
            with st.form("form_harga"):
                f_tgl = st.date_input("Tanggal", value=date.today())
                kom_opts = {r["nama_komoditas"]: r["id_komoditas"] for _, r in df_k.iterrows()} if df_k is not None and not df_k.empty else {}
                f_kom = st.selectbox("Komoditas", list(kom_opts.keys()) if kom_opts else ["—"])
                pasar_opts = {r["nama_pasar"]: r["id_pasar"] for _, r in df_p.iterrows()} if df_p is not None and not df_p.empty else {}
                f_pasar = st.selectbox("Pasar", list(pasar_opts.keys()) if pasar_opts else ["—"])
                f_harga = st.number_input("Harga (Rp)", min_value=0, step=100, value=0)
                submitted = st.form_submit_button("💾 Simpan", use_container_width=True)
                if submitted:
                    if kom_opts and pasar_opts and f_harga > 0:
                        try:
                            db.add_harga_harian(
                                str(f_tgl), int(kom_opts[f_kom]),
                                int(pasar_opts[f_pasar]), int(f_harga)
                            )
                            refresh_data()
                            st.success("✅ Harga berhasil disimpan!")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ Lengkapi semua field.")

        with col_tbl:
            st.markdown("**📋 Data Harga Terbaru**")
            if df_h is not None and not df_h.empty:
                df_show_h = df_h.head(100).copy()
                df_show_h["Tanggal"] = df_show_h["tanggal"].dt.strftime("%d %b %Y")
                df_show_h["Harga"] = df_show_h["harga"].apply(fmt_rp)
                st.dataframe(
                    df_show_h[["Tanggal", "nama_komoditas", "nama_pasar", "Harga"]].rename(
                        columns={"nama_komoditas": "Komoditas", "nama_pasar": "Pasar"}
                    ),
                    use_container_width=True, hide_index=True, height=350,
                )
                st.caption(f"Menampilkan 100 data terbaru dari {len(df_h)} total")
            else:
                st.info("Belum ada data.")

    # ── TAB: INFLASI ─────────────────────────────────────────────────────────
    with crud_tab[1]:
        col_fi, col_ti = st.columns([1, 2])
        with col_fi:
            st.markdown("**➕ Tambah Data Inflasi**")
            with st.form("form_inflasi"):
                fi_tahun = st.number_input("Tahun", min_value=2000, max_value=2099,
                                           value=datetime.now().year, step=1)
                fi_bulan = st.selectbox("Bulan", range(1, 13),
                                        format_func=lambda x: MONTHS_ID[x-1])
                fi_level = st.selectbox("Level Wilayah", ["nasional", "provinsi", "kota", "kabupaten"])
                fi_nama  = st.text_input("Nama Wilayah", placeholder="contoh: Kota Tegal")
                fi_mtm   = st.number_input("Inflasi MtM (%)", step=0.01, format="%.2f")
                fi_ytd   = st.number_input("Inflasi YtD (%)", step=0.01, format="%.2f")
                fi_yoy   = st.number_input("Inflasi YoY (%)", step=0.01, format="%.2f")
                sub_i = st.form_submit_button("💾 Simpan", use_container_width=True)
                if sub_i:
                    if fi_nama.strip():
                        try:
                            db.add_inflasi(int(fi_tahun), int(fi_bulan), fi_level, fi_nama,
                                           fi_mtm, fi_ytd, fi_yoy)
                            refresh_data()
                            st.success("✅ Data inflasi disimpan!")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ Nama wilayah harus diisi.")

        with col_ti:
            st.markdown("**📋 Data Inflasi**")
            if df_i is not None and not df_i.empty:
                df_i_show = df_i.copy()
                df_i_show["Bulan"] = df_i_show["bulan"].apply(lambda x: MONTHS_ID[int(x)-1])
                st.dataframe(
                    df_i_show[["id_inflasi", "tahun", "Bulan", "nama_wilayah", "level_wilayah",
                                "inflasi_mtm", "inflasi_ytd", "inflasi_yoy"]].rename(
                        columns={"id_inflasi": "ID", "tahun": "Tahun",
                                 "nama_wilayah": "Wilayah", "level_wilayah": "Level",
                                 "inflasi_mtm": "MtM", "inflasi_ytd": "YtD", "inflasi_yoy": "YoY"}
                    ),
                    use_container_width=True, hide_index=True, height=350,
                )
                # Delete
                del_id = st.number_input("ID untuk dihapus", min_value=0, step=1, value=0)
                if st.button("🗑️ Hapus Record", key="del_inflasi"):
                    if del_id > 0:
                        try:
                            db.delete_inflasi(int(del_id))
                            refresh_data()
                            st.success(f"✅ Record ID {del_id} dihapus!")
                        except Exception as e:
                            st.error(f"❌ {e}")
            else:
                st.info("Belum ada data inflasi.")

    # ── TAB: KOMODITAS ───────────────────────────────────────────────────────
    with crud_tab[2]:
        col_fk, col_tk = st.columns([1, 2])
        with col_fk:
            st.markdown("**➕ Tambah Komoditas**")
            with st.form("form_kom"):
                fk_nama = st.text_input("Nama Komoditas")
                fk_sat  = st.selectbox("Satuan", ["kg", "liter", "butir", "ikat", "buah", "gram", "ml"])
                sub_k = st.form_submit_button("💾 Simpan", use_container_width=True)
                if sub_k:
                    if fk_nama.strip():
                        try:
                            db.add_komoditas(fk_nama.strip(), fk_sat)
                            refresh_data()
                            st.success("✅ Komoditas ditambahkan!")
                        except Exception as e:
                            st.error(f"❌ {e}")
        with col_tk:
            st.markdown("**📋 Daftar Komoditas**")
            if df_k is not None and not df_k.empty:
                st.dataframe(df_k, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada komoditas.")

    # ── TAB: PASAR ───────────────────────────────────────────────────────────
    with crud_tab[3]:
        col_fp, col_tp = st.columns([1, 2])
        with col_fp:
            st.markdown("**➕ Tambah Pasar**")
            with st.form("form_pasar"):
                fp_nama = st.text_input("Nama Pasar")
                fp_kab  = st.text_input("Kabupaten", value="Kab. Pekalongan")
                fp_kec  = st.text_input("Kecamatan")
                sub_p = st.form_submit_button("💾 Simpan", use_container_width=True)
                if sub_p:
                    if fp_nama.strip():
                        try:
                            db.add_pasar(fp_nama.strip(), fp_kab, fp_kec)
                            refresh_data()
                            st.success("✅ Pasar ditambahkan!")
                        except Exception as e:
                            st.error(f"❌ {e}")
        with col_tp:
            st.markdown("**📋 Daftar Pasar**")
            if df_p is not None and not df_p.empty:
                st.dataframe(df_p, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada data pasar.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LAPORAN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Laporan":
    st.markdown("""
    <div style="margin-bottom:24px">
        <div style="font-size:12px;color:#6e7681;margin-bottom:4px">Output</div>
        <h1 style="font-family:'Playfair Display',serif;font-size:28px;font-weight:800;margin:0">
            📋 Laporan Bulanan TPID
        </h1>
        <p style="color:#8b949e;font-size:14px;margin-top:6px">
            Ekspor laporan dalam format CSV · Excel · Teks Ringkasan
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_lf1, col_lf2, col_lf3 = st.columns(3)
    with col_lf1:
        lap_tahun = st.selectbox("Tahun Laporan",
                                 sorted(df_h["tanggal"].dt.year.unique(), reverse=True) if df_h is not None and not df_h.empty else [datetime.now().year])
    with col_lf2:
        lap_bulan = st.selectbox("Bulan Laporan", range(1, 13),
                                 format_func=lambda x: MONTHS_ID[x-1],
                                 index=datetime.now().month - 1)
    with col_lf3:
        lap_pasar_all = st.checkbox("Semua Pasar", value=True)

    st.markdown("---")

    if df_h is not None and not df_h.empty:
        df_lap = df_h[
            (df_h["tanggal"].dt.year == lap_tahun) &
            (df_h["tanggal"].dt.month == lap_bulan)
        ].copy()

        if df_lap.empty:
            st.info(f"📭 Tidak ada data untuk {MONTHS_ID[lap_bulan-1]} {lap_tahun}")
        else:
            # Preview laporan
            st.markdown(f"""
            <div class="info-card" style="border-left:3px solid #d29922;margin-bottom:20px">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:800;
                            color:#e3b341">📊 TPID Kab. Pekalongan</div>
                        <div style="font-size:12px;color:#8b949e;margin-top:4px">
                            Laporan Monitoring Harga Komoditas</div>
                    </div>
                    <div style="text-align:right;font-size:11px;color:#6e7681">
                        <strong style="color:#e6edf3;font-size:13px">{MONTHS_ID[lap_bulan-1]} {lap_tahun}</strong><br>
                        Dicetak: {datetime.now().strftime('%d %b %Y')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Ringkasan harga
            df_sum = df_lap.groupby("nama_komoditas")["harga"].agg(
                avg="mean", min="min", max="max"
            ).reset_index()

            # Ambil bulan sebelumnya
            if lap_bulan == 1:
                prev_bulan, prev_tahun = 12, lap_tahun - 1
            else:
                prev_bulan, prev_tahun = lap_bulan - 1, lap_tahun

            df_prev_lap = df_h[
                (df_h["tanggal"].dt.year == prev_tahun) &
                (df_h["tanggal"].dt.month == prev_bulan)
            ]
            df_prev_sum = df_prev_lap.groupby("nama_komoditas")["harga"].mean() if not df_prev_lap.empty else pd.Series()

            rows_lap = []
            violators = []
            for _, row in df_sum.iterrows():
                nama = row["nama_komoditas"]
                avg_cur = row["avg"]
                avg_prev = df_prev_sum.get(nama, None)
                delta = ((avg_cur - avg_prev) / avg_prev * 100) if avg_prev and avg_prev > 0 else None
                ref_val, ref_type = get_ref_value(nama)
                st_txt = status_harga(avg_cur, ref_val)
                if "Melebihi" in st_txt:
                    violators.append(nama)
                rows_lap.append({
                    "Komoditas": nama,
                    "Rata Bln Ini": fmt_rp(avg_cur),
                    "Rata Bln Lalu": fmt_rp(avg_prev) if avg_prev else "—",
                    "Δ (%)": fmt_pct(delta) if delta is not None else "—",
                    f"HET/HAP": fmt_rp(ref_val) if ref_val else "—",
                    "Status": st_txt,
                })

            st.markdown("**📦 Perkembangan Harga Komoditas**")
            st.dataframe(pd.DataFrame(rows_lap), use_container_width=True, hide_index=True)

            # Inflasi bulan ini
            if df_i is not None and not df_i.empty:
                df_i_lap = df_i[(df_i["tahun"] == lap_tahun) & (df_i["bulan"] == lap_bulan)]
                if not df_i_lap.empty:
                    st.markdown("**📈 Data Inflasi**")
                    df_i_show = df_i_lap.copy()
                    df_i_show["Bulan"] = MONTHS_ID[lap_bulan - 1]
                    st.dataframe(
                        df_i_show[["tahun", "Bulan", "nama_wilayah", "level_wilayah",
                                   "inflasi_mtm", "inflasi_ytd", "inflasi_yoy"]].rename(
                            columns={"tahun": "Tahun", "nama_wilayah": "Wilayah",
                                     "level_wilayah": "Level", "inflasi_mtm": "MtM (%)",
                                     "inflasi_ytd": "YtD (%)", "inflasi_yoy": "YoY (%)"}),
                        use_container_width=True, hide_index=True
                    )

            # Rekomendasi
            st.markdown("**💡 Ringkasan & Rekomendasi**")
            if violators:
                st.error(f"🔴 **Melebihi HET/HAP:** {', '.join(violators)} — Operasi pasar dan koordinasi distributor diperlukan.")
            else:
                st.success("🟢 Semua komoditas dalam batas normal. Pemantauan rutin dilanjutkan.")

            top_risers = sorted(
                [r for r in rows_lap if r["Δ (%)"] != "—" and r["Δ (%)"].startswith("+")],
                key=lambda x: float(x["Δ (%)"].replace("+", "").replace("%", "")), reverse=True
            )[:3]
            if top_risers:
                st.warning(f"📊 **Kenaikan Tertinggi:** {', '.join([r['Komoditas'] + ' (' + r['Δ (%)'] + ')' for r in top_risers])}")

            # Export
            st.markdown("---")
            st.markdown("**💾 Ekspor Data**")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                csv_data = df_lap.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download CSV — Harga Harian",
                    data=csv_data,
                    file_name=f"TPID_Harga_{MONTHS_ID[lap_bulan-1]}_{lap_tahun}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col_ex2:
                lap_df = pd.DataFrame(rows_lap)
                lap_csv = lap_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download CSV — Ringkasan Komoditas",
                    data=lap_csv,
                    file_name=f"TPID_Ringkasan_{MONTHS_ID[lap_bulan-1]}_{lap_tahun}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
    else:
        st.info("ℹ️ Belum ada data harga untuk diekspor.")
