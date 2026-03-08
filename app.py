import streamlit as st
import pandas as pd
import io
import bcrypt
from datetime import datetime, timedelta
import random
from supabase import create_client, Client

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard UMKM v2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f0f4f8; }

    .hero {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 60%, #3b82f6 100%);
        border-radius: 20px; padding: 28px 32px; color: white;
        margin-bottom: 28px; box-shadow: 0 8px 32px rgba(37,99,235,0.28);
    }
    .hero h1 { font-size: 22px; font-weight: 800; margin-bottom: 6px; }
    .hero p  { font-size: 13px; opacity: 0.85; }

    .metric-card {
        background: white; border-radius: 16px; padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06); border-left: 4px solid; margin-bottom: 8px;
    }
    .metric-card.green  { border-color: #10b981; }
    .metric-card.blue   { border-color: #3b82f6; }
    .metric-card.orange { border-color: #f59e0b; }
    .metric-card.purple { border-color: #8b5cf6; }
    .metric-label { font-size: 11px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
    .metric-value { font-size: 22px; font-weight: 800; color: #111827; }
    .metric-sub   { font-size: 11px; color: #9ca3af; margin-top: 4px; }

    .ai-box {
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        border: 1px solid #93c5fd; border-radius: 16px;
        padding: 20px; margin-bottom: 16px;
    }
    .ai-title { font-size: 15px; font-weight: 700; color: #1e40af; margin-bottom: 8px; }
    .ai-pred  { font-size: 28px; font-weight: 800; color: #1e3a5f; }
    .ai-sub   { font-size: 12px; color: #3b82f6; margin-top: 4px; }

    .login-card {
        background: white; border-radius: 20px; padding: 40px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08); max-width: 420px; margin: 0 auto;
    }
    .login-title { font-size: 24px; font-weight: 800; color: #111827; margin-bottom: 4px; text-align: center; }
    .login-sub   { font-size: 13px; color: #6b7280; text-align: center; margin-bottom: 28px; }

    .stTextInput > div > div > input {
        border-radius: 10px !important; border: 1.5px solid #e5e7eb !important;
        padding: 10px 14px !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stTextInput > div > div > input:focus { border-color: #2563eb !important; }

    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        padding: 10px 24px !important; font-weight: 700 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 14px !important; width: 100% !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669, #047857) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        padding: 10px 24px !important; font-weight: 700 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important; width: 100% !important;
    }
    div[data-testid="stSidebar"] { background: white; border-right: 1px solid #e5e7eb; }
    hr { border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(email: str, password: str, nama_toko: str) -> dict:
    existing = supabase.table("users").select("*").eq("email", email).execute()
    if existing.data:
        return {"success": False, "msg": "Email sudah terdaftar!"}
    hashed = hash_password(password)
    supabase.table("users").insert({
        "email": email, "password": hashed, "nama_toko": nama_toko
    }).execute()
    return {"success": True, "msg": "Registrasi berhasil!"}

def login_user(email: str, password: str) -> dict:
    result = supabase.table("users").select("*").eq("email", email).execute()
    if not result.data:
        return {"success": False, "msg": "Email tidak ditemukan!"}
    user = result.data[0]
    if not verify_password(password, user["password"]):
        return {"success": False, "msg": "Password salah!"}
    return {"success": True, "user": user}


# ─────────────────────────────────────────────
# SAMPLE DATA
# ─────────────────────────────────────────────
def generate_sample_csv(platform: str) -> bytes:
    random.seed(42 if platform == "Shopee" else 99)
    base = datetime.today() - timedelta(days=14)
    products = ["Kaos Polos", "Celana Jeans", "Jaket Hoodie", "Sepatu Sneakers", "Tas Ransel"]
    rows = []
    for i in range(14):
        for _ in range(random.randint(3, 8)):
            qty   = random.randint(1, 5)
            harga = random.choice([85000, 120000, 180000, 250000, 95000])
            rows.append({
                "tanggal": (base + timedelta(days=i)).strftime("%Y-%m-%d"),
                "produk": random.choice(products),
                "qty": qty, "harga": harga, "total": qty * harga
            })
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


# ─────────────────────────────────────────────
# AI PREDICTION (Linear Trend)
# ─────────────────────────────────────────────
def predict_next_7_days(harian_total: pd.DataFrame) -> pd.DataFrame:
    if len(harian_total) < 3:
        return pd.DataFrame()
    df = harian_total.copy()
    df["day_num"] = range(len(df))
    slope = (df["total"].iloc[-1] - df["total"].iloc[0]) / max(len(df) - 1, 1)
    last_total = df["total"].iloc[-1]
    last_date  = df["tanggal"].iloc[-1]
    preds = []
    for i in range(1, 8):
        pred_date  = last_date + timedelta(days=i)
        pred_total = max(0, last_total + slope * i * random.uniform(0.85, 1.15))
        preds.append({"tanggal": pred_date, "prediksi": round(pred_total, 0)})
    return pd.DataFrame(preds)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"


# ─────────────────────────────────────────────
# LOGIN / REGISTER PAGE
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; margin-bottom:8px'>
        <span style='font-size:48px'>📊</span>
    </div>
    <div class='login-title'>Dashboard UMKM v2</div>
    <div class='login-sub'>Platform analisis marketplace dengan AI</div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Daftar"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        email    = st.text_input("Email", placeholder="email@kamu.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Masuk →", key="btn_login"):
            if not email or not password:
                st.error("Email dan password wajib diisi!")
            else:
                with st.spinner("Memverifikasi..."):
                    result = login_user(email, password)
                if result["success"]:
                    st.session_state.logged_in = True
                    st.session_state.user = result["user"]
                    st.success(f"Selamat datang, {result['user']['nama_toko']}! 🎉")
                    st.rerun()
                else:
                    st.error(result["msg"])

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        nama_toko  = st.text_input("Nama Toko", placeholder="Toko Berkah Jaya", key="reg_toko")
        email_reg  = st.text_input("Email", placeholder="email@kamu.com", key="reg_email")
        pass_reg   = st.text_input("Password", type="password", placeholder="Min. 6 karakter", key="reg_pass")
        pass_reg2  = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password", key="reg_pass2")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Daftar Sekarang →", key="btn_register"):
            if not all([nama_toko, email_reg, pass_reg, pass_reg2]):
                st.error("Semua kolom wajib diisi!")
            elif pass_reg != pass_reg2:
                st.error("Password tidak cocok!")
            elif len(pass_reg) < 6:
                st.error("Password minimal 6 karakter!")
            else:
                with st.spinner("Mendaftarkan akun..."):
                    result = register_user(email_reg, pass_reg, nama_toko)
                if result["success"]:
                    st.success("Akun berhasil dibuat! Silakan login.")
                else:
                    st.error(result["msg"])

    st.stop()


# ─────────────────────────────────────────────
# SIDEBAR (setelah login)
# ─────────────────────────────────────────────
with st.sidebar:
    user = st.session_state.user
    st.markdown(f"### 👋 Halo, **{user['nama_toko']}**!")
    st.markdown(f"<small style='color:#6b7280'>{user['email']}</small>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📁 Format CSV:**")
    st.markdown("""
    - `tanggal` → YYYY-MM-DD
    - `produk` → nama produk
    - `qty` → jumlah
    - `total` → total pendapatan
    """)
    st.markdown("---")
    st.markdown("**📥 Download Contoh CSV**")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Shopee", generate_sample_csv("Shopee"), "contoh_shopee.csv", "text/csv")
    with col2:
        st.download_button("Tokopedia", generate_sample_csv("Tokopedia"), "contoh_tokopedia.csv", "text/csv")

    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()


# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <h1>📊 Dashboard UMKM v2</h1>
    <p>Selamat datang kembali, <b>{user['nama_toko']}</b> · Analisis marketplace dengan AI prediksi omzet</p>
</div>
""", unsafe_allow_html=True)

# UPLOAD
st.markdown("#### 📂 Upload Laporan CSV")
col_up1, col_up2 = st.columns(2)
with col_up1:
    shopee_file = st.file_uploader("📦 File Shopee", type=["csv"])
with col_up2:
    tokopedia_file = st.file_uploader("🛒 File Tokopedia", type=["csv"])

if shopee_file and tokopedia_file:
    try:
        shopee    = pd.read_csv(shopee_file)
        tokopedia = pd.read_csv(tokopedia_file)

        shopee["platform"]    = "Shopee"
        tokopedia["platform"] = "Tokopedia"
        data = pd.concat([shopee, tokopedia], ignore_index=True)
        data["tanggal"] = pd.to_datetime(data["tanggal"], errors="coerce")
        data["total"]   = pd.to_numeric(data["total"], errors="coerce").fillna(0)
        data = data.dropna(subset=["tanggal"])

        harian_total   = data.groupby("tanggal")["total"].sum().reset_index()
        platform_total = data.groupby("platform")["total"].sum().reset_index()
        total_omzet    = data["total"].sum()
        omzet_shopee   = data[data["platform"]=="Shopee"]["total"].sum()
        omzet_tokped   = data[data["platform"]=="Tokopedia"]["total"].sum()
        rata_harian    = harian_total["total"].mean()

        # METRICS
        st.markdown("#### 📈 Ringkasan Performa")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card green"><div class="metric-label">Total Omzet</div><div class="metric-value">Rp {total_omzet:,.0f}</div><div class="metric-sub">Semua platform</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card blue"><div class="metric-label">Omzet Shopee</div><div class="metric-value">Rp {omzet_shopee:,.0f}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card orange"><div class="metric-label">Omzet Tokopedia</div><div class="metric-value">Rp {omzet_tokped:,.0f}</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card purple"><div class="metric-label">Rata-rata Harian</div><div class="metric-value">Rp {rata_harian:,.0f}</div><div class="metric-sub">{len(data)} transaksi</div></div>', unsafe_allow_html=True)

        # CHARTS
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### 📉 Grafik Omzet Harian")
            st.line_chart(harian_total.set_index("tanggal"), use_container_width=True, height=250)
        with col2:
            st.markdown("#### 🥧 Per Platform")
            st.bar_chart(platform_total.set_index("platform"), use_container_width=True, height=250)

        # AI PREDICTION
        st.markdown("---")
        st.markdown("#### 🤖 AI Analytics — Prediksi Omzet 7 Hari ke Depan")
        predictions = predict_next_7_days(harian_total)

        if not predictions.empty:
            pred_total  = predictions["prediksi"].sum()
            pred_harian = predictions["prediksi"].mean()
            trend = "📈 Naik" if predictions["prediksi"].iloc[-1] > predictions["prediksi"].iloc[0] else "📉 Turun"

            ai1, ai2, ai3 = st.columns(3)
            with ai1:
                st.markdown(f"""<div class="ai-box">
                    <div class="ai-title">🎯 Prediksi Total 7 Hari</div>
                    <div class="ai-pred">Rp {pred_total:,.0f}</div>
                    <div class="ai-sub">Estimasi omzet minggu depan</div>
                </div>""", unsafe_allow_html=True)
            with ai2:
                st.markdown(f"""<div class="ai-box">
                    <div class="ai-title">📅 Rata-rata Harian</div>
                    <div class="ai-pred">Rp {pred_harian:,.0f}</div>
                    <div class="ai-sub">Per hari minggu depan</div>
                </div>""", unsafe_allow_html=True)
            with ai3:
                st.markdown(f"""<div class="ai-box">
                    <div class="ai-title">📊 Tren Omzet</div>
                    <div class="ai-pred">{trend}</div>
                    <div class="ai-sub">Berdasarkan data historis</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("**Grafik Prediksi:**")
            pred_chart = predictions.set_index("tanggal")
            st.bar_chart(pred_chart, use_container_width=True, height=200)

            st.info("⚠️ Prediksi menggunakan analisis tren linear. Hasil aktual bisa berbeda tergantung kondisi pasar.")

        # TOP PRODUK
        if "produk" in data.columns:
            st.markdown("---")
            st.markdown("#### 🏆 Top 5 Produk Terlaris")
            top = data.groupby("produk")["total"].sum().sort_values(ascending=False).head(5).reset_index()
            top.columns = ["Produk", "Total Omzet"]
            top["Total Omzet"] = top["Total Omzet"].apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(top, use_container_width=True, hide_index=True)

        # EXPORT
        st.markdown("---")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            data.to_excel(writer, sheet_name="Data Gabungan", index=False)
            harian_total.to_excel(writer, sheet_name="Omzet Harian", index=False)
            platform_total.to_excel(writer, sheet_name="Omzet Per Platform", index=False)
            if not predictions.empty:
                predictions.to_excel(writer, sheet_name="Prediksi AI", index=False)

        col_dl, col_info = st.columns([1, 2])
        with col_dl:
            st.download_button(
                "⬇️ Download Laporan Excel",
                data=buffer,
                file_name=f"laporan_umkm_v2_{datetime.today().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col_info:
            st.markdown(f"""<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px 16px;font-size:12px;color:#166534">
                ✅ {len(data)} transaksi · {len(harian_total)} hari data · Prediksi AI 7 hari included
            </div>""", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.markdown("""
    <div style="text-align:center;padding:56px 0;color:#9ca3af">
        <div style="font-size:52px;margin-bottom:12px">📂</div>
        <div style="font-size:18px;font-weight:700;color:#374151;margin-bottom:8px">Upload file CSV untuk mulai</div>
        <div style="font-size:13px">Download contoh file dari sidebar kiri</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center;font-size:12px;color:#9ca3af">Dashboard UMKM v2 · Powered by AI · Dibuat oleh <b>Fasfast Dev</b></div>', unsafe_allow_html=True)
