import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard UMKM | Laporan Marketplace",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main { background-color: #f8f9fb; }

    .stApp { background-color: #f8f9fb; }

    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
        border-left: 4px solid;
        margin-bottom: 8px;
    }
    .metric-card.green { border-color: #10b981; }
    .metric-card.blue  { border-color: #3b82f6; }
    .metric-card.orange{ border-color: #f59e0b; }
    .metric-card.purple{ border-color: #8b5cf6; }

    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 12px;
        color: #9ca3af;
        margin-top: 4px;
    }

    .hero-banner {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 60%, #3b82f6 100%);
        border-radius: 20px;
        padding: 32px 36px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(37,99,235,0.25);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 800;
        margin: 0 0 6px 0;
    }
    .hero-sub {
        font-size: 14px;
        opacity: 0.8;
        margin: 0;
    }

    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #111827;
        margin: 24px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    .badge-green  { background: #d1fae5; color: #065f46; }
    .badge-blue   { background: #dbeafe; color: #1e40af; }
    .badge-orange { background: #fef3c7; color: #92400e; }

    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 12px;
        padding: 16px 20px;
        font-size: 13px;
        color: #1e40af;
        margin-bottom: 16px;
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 14px !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(37,99,235,0.4) !important;
    }

    div[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e5e7eb;
    }

    .contact-box {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 1px solid #86efac;
        border-radius: 12px;
        padding: 16px;
        margin-top: 16px;
        font-size: 13px;
        color: #166534;
    }

    hr { border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER: GENERATE SAMPLE DATA
# ─────────────────────────────────────────────
def generate_sample_csv(platform: str, days: int = 14) -> bytes:
    random.seed(42 if platform == "Shopee" else 99)
    base = datetime.today() - timedelta(days=days)
    rows = []
    products = ["Kaos Polos", "Celana Jeans", "Jaket Hoodie", "Sepatu Sneakers", "Tas Ransel"]
    for i in range(days):
        for _ in range(random.randint(3, 8)):
            tanggal = (base + timedelta(days=i)).strftime("%Y-%m-%d")
            produk  = random.choice(products)
            qty     = random.randint(1, 5)
            harga   = random.choice([85000, 120000, 180000, 250000, 95000])
            total   = qty * harga
            rows.append({"tanggal": tanggal, "produk": produk, "qty": qty, "harga": harga, "total": total})
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Dashboard UMKM")
    st.markdown("---")

    st.markdown("**📁 Format CSV yang didukung:**")
    st.markdown("""
    Pastikan file CSV kamu punya kolom:
    - `tanggal` → format YYYY-MM-DD
    - `produk` → nama produk
    - `qty` → jumlah terjual
    - `harga` → harga satuan
    - `total` → total pendapatan
    """)

    st.markdown("---")
    st.markdown("**📥 Download Contoh File CSV**")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Shopee.csv",
            data=generate_sample_csv("Shopee"),
            file_name="contoh_shopee.csv",
            mime="text/csv"
        )
    with col2:
        st.download_button(
            "Tokopedia.csv",
            data=generate_sample_csv("Tokopedia"),
            file_name="contoh_tokopedia.csv",
            mime="text/csv"
        )

    st.markdown("""
    <div class="contact-box">
        <b>💬 Butuh bantuan?</b><br>
        Hubungi kami via WhatsApp atau email untuk setup & customisasi.<br><br>
        <b>WA:</b> +62 xxx-xxxx-xxxx<br>
        <b>Email:</b> fasfast@email.com
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <p class="hero-title">📊 Dashboard Laporan UMKM</p>
    <p class="hero-sub">Gabungkan & analisis laporan Shopee dan Tokopedia secara otomatis · Export ke Excel dalam 1 klik</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📂 Upload Laporan CSV</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    💡 Belum punya file CSV? Download <b>contoh file</b> dari sidebar kiri, lalu upload di sini untuk melihat demo dashboard.
</div>
""", unsafe_allow_html=True)

col_up1, col_up2 = st.columns(2)
with col_up1:
    shopee_file = st.file_uploader("📦 Upload File Shopee", type=["csv"], help="Export laporan penjualan dari Shopee Seller Center")
with col_up2:
    tokopedia_file = st.file_uploader("🛒 Upload File Tokopedia", type=["csv"], help="Export laporan penjualan dari Tokopedia Seller")


# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────
if shopee_file and tokopedia_file:
    try:
        shopee    = pd.read_csv(shopee_file)
        tokopedia = pd.read_csv(tokopedia_file)

        # Validasi kolom wajib
        required = {"tanggal", "total"}
        for name, df in [("Shopee", shopee), ("Tokopedia", tokopedia)]:
            missing = required - set(df.columns)
            if missing:
                st.error(f"❌ File {name} kurang kolom: {', '.join(missing)}")
                st.stop()

        shopee["platform"]    = "Shopee"
        tokopedia["platform"] = "Tokopedia"
        data = pd.concat([shopee, tokopedia], ignore_index=True)

        data["tanggal"] = pd.to_datetime(data["tanggal"], errors="coerce")
        data = data.dropna(subset=["tanggal"])
        data["total"]   = pd.to_numeric(data["total"], errors="coerce").fillna(0)

        harian_total   = data.groupby("tanggal")["total"].sum().reset_index()
        platform_total = data.groupby("platform")["total"].sum().reset_index()

        total_omzet   = data["total"].sum()
        omzet_shopee  = data[data["platform"] == "Shopee"]["total"].sum()
        omzet_tokped  = data[data["platform"] == "Tokopedia"]["total"].sum()
        total_transaksi = len(data)
        rata_harian   = harian_total["total"].mean()

        # ── METRICS ──────────────────────────────
        st.markdown('<div class="section-title">📈 Ringkasan Performa</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.markdown(f"""
            <div class="metric-card green">
                <div class="metric-label">Total Omzet</div>
                <div class="metric-value">Rp {total_omzet:,.0f}</div>
                <div class="metric-sub">Semua platform</div>
            </div>""", unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="metric-card blue">
                <div class="metric-label">Omzet Shopee</div>
                <div class="metric-value">Rp {omzet_shopee:,.0f}</div>
                <div class="metric-sub"><span class="badge badge-orange">Shopee</span></div>
            </div>""", unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
            <div class="metric-card orange">
                <div class="metric-label">Omzet Tokopedia</div>
                <div class="metric-value">Rp {omzet_tokped:,.0f}</div>
                <div class="metric-sub"><span class="badge badge-green">Tokopedia</span></div>
            </div>""", unsafe_allow_html=True)

        with m4:
            st.markdown(f"""
            <div class="metric-card purple">
                <div class="metric-label">Rata-rata Harian</div>
                <div class="metric-value">Rp {rata_harian:,.0f}</div>
                <div class="metric-sub">{total_transaksi} total transaksi</div>
            </div>""", unsafe_allow_html=True)

        # ── CHARTS ───────────────────────────────
        st.markdown('<div class="section-title">📉 Grafik Omzet Harian</div>', unsafe_allow_html=True)
        st.line_chart(harian_total.set_index("tanggal"), use_container_width=True, height=280)

        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            st.markdown('<div class="section-title">🥧 Perbandingan Platform</div>', unsafe_allow_html=True)
            st.bar_chart(platform_total.set_index("platform"), use_container_width=True, height=220)

        with col_c2:
            st.markdown('<div class="section-title">📋 Data Terbaru (10 Transaksi)</div>', unsafe_allow_html=True)
            display_cols = [c for c in ["tanggal", "produk", "platform", "qty", "total"] if c in data.columns]
            st.dataframe(
                data[display_cols].sort_values("tanggal", ascending=False).head(10),
                use_container_width=True,
                hide_index=True,
                height=220
            )

        # ── TOP PRODUK (jika ada kolom produk) ───
        if "produk" in data.columns:
            st.markdown('<div class="section-title">🏆 Top 5 Produk Terlaris</div>', unsafe_allow_html=True)
            top_produk = data.groupby("produk")["total"].sum().sort_values(ascending=False).head(5).reset_index()
            top_produk.columns = ["Produk", "Total Omzet"]
            top_produk["Total Omzet"] = top_produk["Total Omzet"].apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(top_produk, use_container_width=True, hide_index=True)

        # ── EXPORT ───────────────────────────────
        st.markdown("---")
        st.markdown('<div class="section-title">💾 Export Laporan</div>', unsafe_allow_html=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            data.to_excel(writer, sheet_name="Data Gabungan", index=False)
            harian_total.to_excel(writer, sheet_name="Omzet Harian", index=False)
            platform_total.to_excel(writer, sheet_name="Omzet Per Platform", index=False)
            if "produk" in data.columns:
                data.groupby("produk")["total"].sum().reset_index().to_excel(
                    writer, sheet_name="Top Produk", index=False)

        col_dl, col_info = st.columns([1, 2])
        with col_dl:
            tanggal_export = datetime.today().strftime("%Y%m%d")
            st.download_button(
                label="⬇️ Download Laporan Excel",
                data=buffer,
                file_name=f"laporan_umkm_{tanggal_export}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col_info:
            st.markdown(f"""
            <div class="info-box" style="margin:0">
                ✅ Laporan siap download · {total_transaksi} transaksi · {len(harian_total)} hari data<br>
                File Excel berisi: Data Gabungan, Omzet Harian, Omzet Per Platform, Top Produk
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Terjadi error saat memproses file: {e}")
        st.info("Pastikan format file CSV sudah benar. Download contoh file dari sidebar untuk referensi.")

else:
    # PLACEHOLDER saat belum upload
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding: 48px 0; color: #9ca3af;">
        <div style="font-size: 48px; margin-bottom: 12px;">📂</div>
        <div style="font-size: 18px; font-weight: 700; color: #374151; margin-bottom: 8px;">Upload file CSV untuk mulai</div>
        <div style="font-size: 14px;">Atau download contoh file dari <b>sidebar kiri</b> untuk melihat demo</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:12px; color:#9ca3af; padding: 8px 0;">
    Dashboard UMKM · Dibuat oleh <b>Fasfast</b> · Untuk info & custom fitur hubungi via sidebar
</div>
""", unsafe_allow_html=True)
