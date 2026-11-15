import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Dashboard EVM - Janabadra", layout="wide")
st.title("Dashboard Pengendalian Biaya dan Waktu Proyek")

# --- SIDEBAR: Upload + Slider ---
st.sidebar.header("1. Upload Data")
uploaded = st.sidebar.file_uploader("Upload file CSV atau Excel", type=["csv", "xlsx"])

st.sidebar.header("2. Pilih Periode Status")
periode_status = st.sidebar.slider("Periode Status Evaluasi", 1, 10, 3)

st.sidebar.divider()
st.sidebar.caption("Dibuat oleh")
st.sidebar.markdown("**Hari Nuryanto**")
st.sidebar.caption("Dashboard EVM v1.0")

# --- DATA DEFAULT - Kalau belum upload, pakai data contoh --
if uploaded is None:
    st.info("Belum upload file. Silahkan menggunakan data template")
    data = pd.DataFrame([
        {"periode": 1, "kode_wbs": "STR-01", "bac": 100000000, "progres_rencana": 0.5, "progres_aktual": 0.4, "biaya_aktual": 45000000},
        {"periode": 1, "kode_wbs": "ARS-01", "bac": 200000000, "progres_rencana": 0.3, "progres_aktual": 0.3, "biaya_aktual": 60000000},
        {"periode": 2, "kode_wbs": "STR-01", "bac": 100000000, "progres_rencana": 0.8, "progres_aktual": 0.7, "biaya_aktual": 75000000},
        {"periode": 2, "kode_wbs": "ARS-01", "bac": 200000000, "progres_rencana": 0.6, "progres_aktual": 0.5, "biaya_aktual": 110000000},
        {"periode": 3, "kode_wbs": "STR-01", "bac": 100000000, "progres_rencana": 1.0, "progres_aktual": 0.9, "biaya_aktual": 95000000},
        {"periode": 3, "kode_wbs": "ARS-01", "bac": 200000000, "progres_rencana": 0.8, "progres_aktual": 0.6, "biaya_aktual": 130000000},
    ])
else:
    if uploaded.name.endswith(".csv"):
        data = pd.read_csv(uploaded)
    else:
        data = pd.read_excel(uploaded)
    st.success(f"File {uploaded.name} berhasil diupload!")

# --- HITUNG EVM ---
data["PV"] = data["bac"] * data["progres_rencana"]
data["EV"] = data["bac"] * data["progres_aktual"]
data["AC"] = data["biaya_aktual"]

rekap = data.groupby("periode")[["PV", "EV", "AC"]].sum().reset_index()
rekap["PV"] = rekap["PV"].cumsum()
rekap["EV"] = rekap["EV"].cumsum()
rekap["AC"] = rekap["AC"].cumsum()

# Ambil data di periode status
row = rekap[rekap["periode"] == periode_status]
if len(row) == 0:
   
    st.warning(f"Data periode {periode_status} belum ada. Silahkan pilih periode yang tersedia.")
    st.stop()

pv = float(row["PV"].iloc[0])
ev = float(row["EV"].iloc[0])
ac = float(row["AC"].iloc[0])
bac_total = float(data["bac"].max() * 0 + data.groupby("kode_wbs")["bac"].max().sum())
spi = ev / pv if pv != 0 else 0
cpi = ev / ac if ac != 0 else 0
eac = bac_total / cpi if cpi != 0 else 0

# --- KARTU INDIKATOR - 4 Kolom ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("BAC - Total Anggaran", f"Rp {bac_total:,.0f}")
col2.metric("SPI - Jadwal", f"{spi:.3f}", f"{'Terlambat' if spi < 1 else 'Tepat / Cepat'}")
col3.metric("CPI - Biaya", f"{cpi:.3f}", f"{'Boros' if cpi < 1 else 'Hemat'}")
col4.metric("EAC - Perkiraan Akhir", f"Rp {eac:,.0f}")

# --- GRAFIK KURVA-S ---
st.subheader("Kurva-S")
fig = go.Figure()
fig.add_trace(go.Scatter(x=rekap["periode"], y=rekap["PV"], mode="lines+markers", name="PV - Rencana", line=dict(color="#1f77b4", width=3)))
fig.add_trace(go.Scatter(x=rekap["periode"], y=rekap["EV"], mode="lines+markers", name="EV - Nyata Kerja", line=dict(color="#2ca02c", width=3)))
fig.add_trace(go.Scatter(x=rekap["periode"], y=rekap["AC"], mode="lines+markers", name="AC - Uang Keluar", line=dict(color="#d62728", width=3, dash="dash")))
fig.add_vline(x=periode_status, line_width=2, line_dash="dot", line_color="gray", annotation_text=f"Status Periode {periode_status}")
fig.update_layout(title="Kurva-S Pengendalian Biaya dan Waktu Proyek", xaxis_title="Periode", yaxis_title="Nilai Kumulatif (Rp)", hovermode="x unified", template="plotly_white")

st.plotly_chart(fig, width="stretch")

# --- TABEL + DOWNLOAD ---
st.subheader("Tabel Rekap")
st.dataframe(rekap)

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    rekap.to_excel(writer, index=False, sheet_name="Rekap")
st.download_button("Download Hasil ke Excel (.xlsx)", data=buffer.getvalue(), file_name="rekap_evm.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.divider()
st.caption("© 2026 Hari Nuryanto - Dashboard Pengendalian Biaya dan Waktu Proyek dengan Metode Earned Value Management (EVM)")