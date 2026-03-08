import streamlit as st
import pandas as pd
import io
import bcrypt
import re
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
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
SMTP_EMAIL   = st.secrets["SMTP_EMAIL"]
SMTP_PASS    = st.secrets["SMTP_PASS"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%); min-height: 100vh; }

/* AUTH PAGE */
.auth-wrapper {
    display: flex; align-items: center; justify-content: center;
    min-height: 80vh; padding: 40px 0;
}
.auth-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 48px 40px;
    max-width: 460px;
    margin: 0 auto;
    box-shadow: 0 32px 64px rgba(0,0,0,0.4);
}
.auth-logo {
    text-align: center;
    font-size: 52px;
    margin-bottom: 8px;
}
.auth-title {
    text-align: center;
    font-size: 28px;
    font-weight: 800;
    color: white;
    margin-bottom: 4px;
}
.auth-sub {
    text-align: center;
    font-size: 13px;
    color: rgba(255,255,255,0.5);
    margin-bottom: 32px;
}

/* PASSWORD STRENGTH */
.strength-bar {
    height: 4px;
    border-radius: 999px;
    margin: 6px 0 4px 0;
    transition: all 0.3s;
}
.strength-weak   { background: linear-gradient(90deg, #ef4444 33%, #374151 33%); }
.strength-medium { background: linear-gradient(90deg, #f59e0b 66%, #374151 66%); }
.strength-strong { background: #10b981; }
.strength-label  { font-size: 11px; font-weight: 700; margin-bottom: 8px; }
.strength-label.weak   { color: #ef4444; }
.strength-label.medium { color: #f59e0b; }
.strength-label.strong { color: #10b981; }

/* REQUIREMENT CHECKLIST */
.req-list { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; }
.req-item { font-size: 11px; display: flex; align-items: center; gap: 6px; }
.req-item.pass { color: #10b981; }
.req-item.fail { color: rgba(255,255,255,0.35); }

/* OTP INPUT */
.otp-box {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    margin: 16px 0;
}
.otp-title { font-size: 18px; font-weight: 700; color: white; margin-bottom: 6px; }
.otp-sub   { font-size: 12px; color: rgba(255,255,255,0.5); margin-bottom: 16px; }

/* VALIDATION MESSAGES */
.val-ok  { font-size: 11px; color: #10b981; margin-top: 2px; }
.val-err { font-size: 11px; color: #ef4444; margin-top: 2px; }

/* INPUTS */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.08) !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 12px 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    background: rgba(59,130,246,0.1) !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.3) !important; }
label { color: rgba(255,255,255,0.8) !important; font-size: 13px !important; font-weight: 600 !important; }

/* BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; padding: 12px 24px !important;
    font-weight: 700 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important; width: 100% !important;
    box-shadow: 0 4px 20px rgba(37,99,235,0.4) !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #047857) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    width: 100% !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important; padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important; color: rgba(255,255,255,0.5) !important;
    font-weight: 600 !important; font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    background: #2563eb !important; color: white !important;
}

/* DASHBOARD */
.dash-app { background: #f0f4f8 !important; }
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
    border: 1px solid #93c5fd; border-radius: 16px; padding: 20px; margin-bottom: 16px;
}
.ai-title { font-size: 15px; font-weight: 700; color: #1e40af; margin-bottom: 8px; }
.ai-pred  { font-size: 28px; font-weight: 800; color: #1e3a5f; }
.ai-sub   { font-size: 12px; color: #3b82f6; margin-top: 4px; }
div[data-testid="stSidebar"] { background: white !important; border-right: 1px solid #e5e7eb; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# VALIDATION HELPERS
# ─────────────────────────────────────────────
def validate_email(email: str) -> dict:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not email:
        return {"valid": False, "msg": "Email wajib diisi"}
    if not re.match(pattern, email):
        return {"valid": False, "msg": "Format email tidak valid (contoh: nama@gmail.com)"}
    return {"valid": True, "msg": "✓ Format email valid"}

def check_password_strength(password: str) -> dict:
    checks = {
        "min_length":    len(password) >= 8,
        "has_upper":     bool(re.search(r'[A-Z]', password)),
        "has_lower":     bool(re.search(r'[a-z]', password)),
        "has_digit":     bool(re.search(r'\d', password)),
        "has_special":   bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
    }
    score = sum(checks.values())
    if score <= 2:
        strength = "weak"
        label    = "⚠️ Lemah"
    elif score <= 3:
        strength = "medium"
        label    = "🔶 Sedang"
    else:
        strength = "strong"
        label    = "✅ Kuat"
    return {"checks": checks, "strength": strength, "label": label, "score": score}

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(to_email: str, otp: str, nama_toko: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔐 Kode OTP Dashboard UMKM - {otp}"
        msg["From"]    = SMTP_EMAIL
        msg["To"]      = to_email

        html = f"""
        <div style="font-family:'Plus Jakarta Sans',sans-serif;max-width:480px;margin:0 auto;background:#f0f4f8;padding:32px;border-radius:16px">
            <div style="background:linear-gradient(135deg,#1e3a5f,#2563eb);border-radius:16px;padding:28px;text-align:center;margin-bottom:24px">
                <div style="font-size:40px;margin-bottom:8px">📊</div>
                <h1 style="color:white;font-size:20px;margin:0">Dashboard UMKM v2</h1>
                <p style="color:rgba(255,255,255,0.7);font-size:13px;margin:4px 0 0">Verifikasi Email</p>
            </div>
            <div style="background:white;border-radius:16px;padding:28px">
                <p style="font-size:15px;color:#374151">Halo <b>{nama_toko}</b> 👋</p>
                <p style="font-size:13px;color:#6b7280">Gunakan kode OTP berikut untuk verifikasi email kamu:</p>
                <div style="background:#eff6ff;border:2px dashed #3b82f6;border-radius:12px;padding:20px;text-align:center;margin:20px 0">
                    <div style="font-size:40px;font-weight:800;letter-spacing:12px;color:#1e3a5f">{otp}</div>
                    <div style="font-size:12px;color:#6b7280;margin-top:8px">Berlaku 10 menit</div>
                </div>
                <p style="font-size:12px;color:#9ca3af">Jika kamu tidak melakukan registrasi, abaikan email ini.</p>
            </div>
            <p style="text-align:center;font-size:11px;color:#9ca3af;margin-top:16px">Dashboard UMKM v2 · Dibuat oleh Fasfast Dev</p>
        </div>
        """
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASS)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Gagal kirim email: {e}")
        return False


# ─────────────────────────────────────────────
# AUTH DB HELPERS
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(email, password, nama_toko):
    existing = supabase.table("users").select("*").eq("email", email).execute()
    if existing.data:
        return {"success": False, "msg": "Email sudah terdaftar!"}
    hashed = hash_password(password)
    supabase.table("users").insert({
        "email": email, "password": hashed,
        "nama_toko": nama_toko, "verified": True
    }).execute()
    return {"success": True}

def login_user(email, password):
    result = supabase.table("users").select("*").eq("email", email).execute()
    if not result.data:
        return {"success": False, "msg": "Email tidak ditemukan!"}
    user = result.data[0]
    if not verify_password(password, user["password"]):
        return {"success": False, "msg": "Password salah!"}
    return {"success": True, "user": user}


# ─────────────────────────────────────────────
# SAMPLE DATA & AI
# ─────────────────────────────────────────────
def generate_sample_csv(platform):
    random.seed(42 if platform == "Shopee" else 99)
    base = datetime.today() - timedelta(days=14)
    products = ["Kaos Polos", "Celana Jeans", "Jaket Hoodie", "Sepatu Sneakers", "Tas Ransel"]
    rows = []
    for i in range(14):
        for _ in range(random.randint(3, 8)):
            qty = random.randint(1, 5)
            harga = random.choice([85000, 120000, 180000, 250000, 95000])
            rows.append({
                "tanggal": (base + timedelta(days=i)).strftime("%Y-%m-%d"),
                "produk": random.choice(products), "qty": qty,
                "harga": harga, "total": qty * harga
            })
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")

def predict_next_7_days(harian_total):
    if len(harian_total) < 3:
        return pd.DataFrame()
    df = harian_total.copy()
    slope = (df["total"].iloc[-1] - df["total"].iloc[0]) / max(len(df) - 1, 1)
    last_total = df["total"].iloc[-1]
    last_date  = df["tanggal"].iloc[-1]
    preds = []
    for i in range(1, 8):
        pred_total = max(0, last_total + slope * i * random.uniform(0.85, 1.15))
        preds.append({"tanggal": last_date + timedelta(days=i), "prediksi": round(pred_total, 0)})
    return pd.DataFrame(preds)


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
for key, val in {
    "logged_in": False, "user": None,
    "reg_step": "form",   # form → otp → done
    "reg_data": {},
    "otp_code": "",
    "otp_expiry": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ─────────────────────────────────────────────
# AUTH PAGE
# ─────────────────────────────────────────────
if not st.session_state.logged_in:

    # Background stars effect
    st.markdown("""
    <div style="position:fixed;top:0;left:0;right:0;bottom:0;pointer-events:none;z-index:0;overflow:hidden">
        <div style="position:absolute;width:2px;height:2px;background:white;border-radius:50%;opacity:0.4;top:10%;left:20%"></div>
        <div style="position:absolute;width:1px;height:1px;background:white;border-radius:50%;opacity:0.3;top:30%;left:70%"></div>
        <div style="position:absolute;width:2px;height:2px;background:white;border-radius:50%;opacity:0.5;top:60%;left:40%"></div>
        <div style="position:absolute;width:1px;height:1px;background:white;border-radius:50%;opacity:0.3;top:80%;left:85%"></div>
        <div style="position:absolute;width:3px;height:3px;background:#3b82f6;border-radius:50%;opacity:0.4;top:20%;left:90%"></div>
        <div style="position:absolute;width:2px;height:2px;background:#60a5fa;border-radius:50%;opacity:0.3;top:70%;left:10%"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-logo">📊</div>
    <div class="auth-title">Dashboard UMKM v2</div>
    <div class="auth-sub">Platform analisis marketplace dengan AI · Dibuat oleh Fasfast Dev</div>
    """, unsafe_allow_html=True)

    # ── OTP VERIFICATION STEP ──────────────────
    if st.session_state.reg_step == "otp":
        col_c = st.columns([1, 2, 1])[1]
        with col_c:
            st.markdown(f"""
            <div class="otp-box">
                <div style="font-size:40px">📧</div>
                <div class="otp-title">Cek Email Kamu!</div>
                <div class="otp-sub">Kode OTP 6 digit telah dikirim ke<br><b style="color:white">{st.session_state.reg_data.get('email','')}</b></div>
            </div>
            """, unsafe_allow_html=True)

            otp_input = st.text_input("Masukkan Kode OTP", placeholder="_ _ _ _ _ _", max_chars=6)

            # Check expiry
            if st.session_state.otp_expiry and datetime.now() > st.session_state.otp_expiry:
                st.error("⏰ Kode OTP sudah kadaluarsa! Silakan daftar ulang.")
                if st.button("← Kembali ke Daftar"):
                    st.session_state.reg_step = "form"
                    st.rerun()
            else:
                remaining = ""
                if st.session_state.otp_expiry:
                    sisa = int((st.session_state.otp_expiry - datetime.now()).total_seconds())
                    remaining = f"⏱️ Kode berlaku {sisa} detik lagi"

                st.markdown(f"<div style='font-size:11px;color:rgba(255,255,255,0.4);text-align:center;margin-bottom:8px'>{remaining}</div>", unsafe_allow_html=True)

                if st.button("✅ Verifikasi OTP"):
                    if otp_input == st.session_state.otp_code:
                        d = st.session_state.reg_data
                        result = register_user(d["email"], d["password"], d["nama_toko"])
                        if result["success"]:
                            st.success("🎉 Email terverifikasi! Akun berhasil dibuat. Silakan login.")
                            st.session_state.reg_step = "form"
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(result["msg"])
                    else:
                        st.error("❌ Kode OTP salah! Coba lagi.")

                st.markdown("<div style='text-align:center;margin-top:8px'>", unsafe_allow_html=True)
                if st.button("🔄 Kirim Ulang OTP"):
                    new_otp = generate_otp()
                    st.session_state.otp_code   = new_otp
                    st.session_state.otp_expiry = datetime.now() + timedelta(minutes=10)
                    d = st.session_state.reg_data
                    if send_otp_email(d["email"], new_otp, d["nama_toko"]):
                        st.success("OTP baru telah dikirim!")
                st.markdown("</div>", unsafe_allow_html=True)

    # ── LOGIN / REGISTER FORM ──────────────────
    else:
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            tab1, tab2 = st.tabs(["🔐 Login", "📝 Daftar"])

            # ── LOGIN ──
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                login_email = st.text_input("Email", placeholder="nama@gmail.com", key="li_email")
                login_pass  = st.text_input("Password", type="password", placeholder="••••••••", key="li_pass")

                # Email validation feedback
                if login_email:
                    v = validate_email(login_email)
                    if v["valid"]:
                        st.markdown(f'<div class="val-ok">✓ Format email valid</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="val-err">✗ {v["msg"]}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("Masuk →", key="btn_login"):
                    email_check = validate_email(login_email)
                    if not email_check["valid"]:
                        st.error(email_check["msg"])
                    elif not login_pass:
                        st.error("Password wajib diisi!")
                    else:
                        with st.spinner("Memverifikasi..."):
                            result = login_user(login_email, login_pass)
                        if result["success"]:
                            st.session_state.logged_in = True
                            st.session_state.user = result["user"]
                            st.success(f"Selamat datang, {result['user']['nama_toko']}! 🎉")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['msg']}")

                st.markdown("""
                <div style="text-align:center;margin-top:16px;font-size:12px;color:rgba(255,255,255,0.3)">
                    Belum punya akun? Klik tab <b style="color:#60a5fa">Daftar</b> di atas
                </div>
                """, unsafe_allow_html=True)

            # ── REGISTER ──
            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                r_toko  = st.text_input("Nama Toko / Usaha", placeholder="Toko Berkah Jaya", key="r_toko")
                r_email = st.text_input("Email", placeholder="nama@gmail.com", key="r_email")

                # Email validation live
                if r_email:
                    v = validate_email(r_email)
                    if v["valid"]:
                        st.markdown(f'<div class="val-ok">✓ Format email valid</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="val-err">✗ {v["msg"]}</div>', unsafe_allow_html=True)

                r_pass  = st.text_input("Password", type="password", placeholder="Min. 8 karakter", key="r_pass")

                # Password strength meter
                if r_pass:
                    ps = check_password_strength(r_pass)
                    checks = ps["checks"]

                    # Strength bar
                    st.markdown(f'<div class="strength-bar strength-{ps["strength"]}"></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="strength-label {ps["strength"]}">{ps["label"]}</div>', unsafe_allow_html=True)

                    # Requirements checklist
                    req_items = [
                        ("min_length",  "Minimal 8 karakter"),
                        ("has_upper",   "Huruf besar (A-Z)"),
                        ("has_lower",   "Huruf kecil (a-z)"),
                        ("has_digit",   "Angka (0-9)"),
                        ("has_special", "Karakter spesial (!@#$%^&*)"),
                    ]
                    html_reqs = '<div class="req-list">'
                    for key, label in req_items:
                        status = "pass" if checks[key] else "fail"
                        icon   = "✅" if checks[key] else "○"
                        html_reqs += f'<div class="req-item {status}">{icon} {label}</div>'
                    html_reqs += '</div>'
                    st.markdown(html_reqs, unsafe_allow_html=True)

                r_pass2 = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password", key="r_pass2")

                # Password match feedback
                if r_pass2:
                    if r_pass == r_pass2:
                        st.markdown('<div class="val-ok">✓ Password cocok</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="val-err">✗ Password tidak cocok</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("Daftar & Verifikasi Email →", key="btn_reg"):
                    # Validasi semua field
                    errors = []
                    if not r_toko:
                        errors.append("Nama toko wajib diisi")
                    email_v = validate_email(r_email)
                    if not email_v["valid"]:
                        errors.append(email_v["msg"])
                    ps = check_password_strength(r_pass)
                    if ps["strength"] == "weak":
                        errors.append("Password terlalu lemah — penuhi semua persyaratan")
                    if r_pass != r_pass2:
                        errors.append("Konfirmasi password tidak cocok")

                    if errors:
                        for e in errors:
                            st.error(f"❌ {e}")
                    else:
                        # Cek email sudah terdaftar
                        existing = supabase.table("users").select("email").eq("email", r_email).execute()
                        if existing.data:
                            st.error("❌ Email sudah terdaftar! Silakan login.")
                        else:
                            otp = generate_otp()
                            with st.spinner("📧 Mengirim kode OTP ke email kamu..."):
                                sent = send_otp_email(r_email, otp, r_toko)
                            if sent:
                                st.session_state.reg_data   = {"email": r_email, "password": r_pass, "nama_toko": r_toko}
                                st.session_state.otp_code   = otp
                                st.session_state.otp_expiry = datetime.now() + timedelta(minutes=10)
                                st.session_state.reg_step   = "otp"
                                st.rerun()

    st.stop()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
user = st.session_state.user
with st.sidebar:
    st.markdown(f"### 👋 {user['nama_toko']}")
    st.markdown(f"<small style='color:#6b7280'>{user['email']}</small>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**📁 Format CSV:**")
    st.markdown("- `tanggal`, `produk`, `qty`, `total`")
    st.markdown("---")
    st.markdown("**📥 Download Contoh:**")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Shopee", generate_sample_csv("Shopee"), "contoh_shopee.csv", "text/csv")
    with c2:
        st.download_button("Tokopedia", generate_sample_csv("Tokopedia"), "contoh_tokopedia.csv", "text/csv")
    st.markdown("---")
    if st.button("🚪 Logout"):
        for k in ["logged_in","user","reg_step","reg_data","otp_code","otp_expiry"]:
            st.session_state[k] = False if k=="logged_in" else None if k=="user" else "form" if k=="reg_step" else {} if k=="reg_data" else ""
        st.rerun()


# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <h1>📊 Dashboard UMKM v2</h1>
    <p>Selamat datang, <b>{user['nama_toko']}</b> · Analisis marketplace dengan AI prediksi omzet</p>
</div>
""", unsafe_allow_html=True)

st.markdown("#### 📂 Upload Laporan CSV")
c1, c2 = st.columns(2)
with c1:
    shopee_file    = st.file_uploader("📦 File Shopee", type=["csv"])
with c2:
    tokopedia_file = st.file_uploader("🛒 File Tokopedia", type=["csv"])

if shopee_file and tokopedia_file:
    try:
        shopee    = pd.read_csv(shopee_file); shopee["platform"]    = "Shopee"
        tokopedia = pd.read_csv(tokopedia_file); tokopedia["platform"] = "Tokopedia"
        data = pd.concat([shopee, tokopedia], ignore_index=True)
        data["tanggal"] = pd.to_datetime(data["tanggal"], errors="coerce")
        data["total"]   = pd.to_numeric(data["total"], errors="coerce").fillna(0)
        data = data.dropna(subset=["tanggal"])

        harian_total   = data.groupby("tanggal")["total"].sum().reset_index()
        platform_total = data.groupby("platform")["total"].sum().reset_index()
        total_omzet    = data["total"].sum()

        st.markdown("#### 📈 Ringkasan Performa")
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.markdown(f'<div class="metric-card green"><div class="metric-label">Total Omzet</div><div class="metric-value">Rp {total_omzet:,.0f}</div><div class="metric-sub">Semua platform</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card blue"><div class="metric-label">Omzet Shopee</div><div class="metric-value">Rp {data[data.platform=="Shopee"]["total"].sum():,.0f}</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card orange"><div class="metric-label">Omzet Tokopedia</div><div class="metric-value">Rp {data[data.platform=="Tokopedia"]["total"].sum():,.0f}</div></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="metric-card purple"><div class="metric-label">Rata-rata Harian</div><div class="metric-value">Rp {harian_total["total"].mean():,.0f}</div><div class="metric-sub">{len(data)} transaksi</div></div>', unsafe_allow_html=True)

        c1,c2 = st.columns([2,1])
        with c1:
            st.markdown("#### 📉 Grafik Omzet Harian")
            st.line_chart(harian_total.set_index("tanggal"), use_container_width=True, height=250)
        with c2:
            st.markdown("#### 🥧 Per Platform")
            st.bar_chart(platform_total.set_index("platform"), use_container_width=True, height=250)

        st.markdown("---")
        st.markdown("#### 🤖 AI Analytics — Prediksi 7 Hari ke Depan")
        predictions = predict_next_7_days(harian_total)
        if not predictions.empty:
            a1,a2,a3 = st.columns(3)
            with a1: st.markdown(f'<div class="ai-box"><div class="ai-title">🎯 Prediksi Total 7 Hari</div><div class="ai-pred">Rp {predictions["prediksi"].sum():,.0f}</div><div class="ai-sub">Estimasi minggu depan</div></div>', unsafe_allow_html=True)
            with a2: st.markdown(f'<div class="ai-box"><div class="ai-title">📅 Rata-rata Harian</div><div class="ai-pred">Rp {predictions["prediksi"].mean():,.0f}</div><div class="ai-sub">Per hari minggu depan</div></div>', unsafe_allow_html=True)
            with a3:
                trend = "📈 Naik" if predictions["prediksi"].iloc[-1] > predictions["prediksi"].iloc[0] else "📉 Turun"
                st.markdown(f'<div class="ai-box"><div class="ai-title">📊 Tren Omzet</div><div class="ai-pred">{trend}</div><div class="ai-sub">Berdasarkan data historis</div></div>', unsafe_allow_html=True)
            st.bar_chart(predictions.set_index("tanggal"), use_container_width=True, height=200)
            st.info("⚠️ Prediksi menggunakan analisis tren linear. Hasil aktual bisa berbeda.")

        if "produk" in data.columns:
            st.markdown("---")
            st.markdown("#### 🏆 Top 5 Produk Terlaris")
            top = data.groupby("produk")["total"].sum().sort_values(ascending=False).head(5).reset_index()
            top.columns = ["Produk","Total Omzet"]
            top["Total Omzet"] = top["Total Omzet"].apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(top, use_container_width=True, hide_index=True)

        st.markdown("---")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            data.to_excel(writer, sheet_name="Data Gabungan", index=False)
            harian_total.to_excel(writer, sheet_name="Omzet Harian", index=False)
            if not predictions.empty:
                predictions.to_excel(writer, sheet_name="Prediksi AI", index=False)
        c1,c2 = st.columns([1,2])
        with c1:
            st.download_button("⬇️ Download Laporan Excel", data=buffer,
                file_name=f"laporan_umkm_v2_{datetime.today().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.markdown('<div style="text-align:center;padding:56px 0;color:#9ca3af"><div style="font-size:52px">📂</div><div style="font-size:18px;font-weight:700;color:#374151;margin:8px 0">Upload file CSV untuk mulai</div><div style="font-size:13px">Download contoh file dari sidebar</div></div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center;font-size:12px;color:#9ca3af">Dashboard UMKM v2 · Powered by AI · Dibuat oleh <b>Fasfast Dev</b></div>', unsafe_allow_html=True)
