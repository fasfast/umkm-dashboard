import streamlit as st
import pandas as pd
import io

st.title("Dashboard Laporan UMKM Multi Marketplace")

shopee_file = st.file_uploader("Upload File Shopee", type=["csv"])
tokopedia_file = st.file_uploader("Upload File Tokopedia", type=["csv"])

if shopee_file and tokopedia_file:

    shopee = pd.read_csv(shopee_file)
    tokopedia = pd.read_csv(tokopedia_file)

    shopee["platform"] = "Shopee"
    tokopedia["platform"] = "Tokopedia"

    data = pd.concat([shopee, tokopedia])

    data["tanggal"] = pd.to_datetime(data["tanggal"])

    harian_total = data.groupby("tanggal")["total"].sum().reset_index()
    platform_total = data.groupby("platform")["total"].sum().reset_index()

    st.subheader("Grafik Omzet Harian (Semua Platform)")
    st.line_chart(harian_total.set_index("tanggal"))

    st.subheader("Perbandingan Omzet Per Platform")
    st.bar_chart(platform_total.set_index("platform"))

    st.metric("Total Omzet Semua Platform", f"Rp {data['total'].sum():,.0f}")

    # ===== EXPORT EXCEL =====
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        data.to_excel(writer, sheet_name="Data Gabungan", index=False)
        harian_total.to_excel(writer, sheet_name="Omzet Harian", index=False)
        platform_total.to_excel(writer, sheet_name="Omzet Per Platform", index=False)

    st.download_button(
        label="Download Laporan Excel",
        data=buffer,
        file_name="laporan_umkm.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )