import streamlit as st
import pandas as pd
import base64, re

st.set_page_config(
    page_title="Apresiasi Pegawai Terbaik - FIPP UNNES",
    layout="wide",
    initial_sidebar_state="collapsed",
)

css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
*, html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; }

.stApp { background: linear-gradient(150deg, #e8f4fd 0%, #f3eeff 50%, #e6f9f1 100%); min-height: 100vh; }

.header-wrap {
    background: linear-gradient(135deg, #4a90e2 0%, #7b68ee 55%, #56c596 100%);
    border-radius: 22px; padding: 2.2rem 2rem 1.8rem; text-align: center;
    margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(74,144,226,0.28);
}
.header-wrap h1 { color: white !important; font-size: 2.5rem; font-weight: 800; margin: 0; text-shadow: 0 2px 10px rgba(0,0,0,0.18); }
.header-wrap .sub1 { color: rgba(255,255,255,0.92); font-size: 1rem; margin: 0.2rem 0 0; }
.header-wrap .sub2 { color: rgba(255,255,255,0.72); font-size: 0.82rem; margin: 0.25rem 0 0; }

.card-wrap { border-radius: 22px; padding: 1.8rem 1.4rem 1.6rem; text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.09); height: 100%;
    transition: transform 0.3s, box-shadow 0.3s; }
.card-wrap:hover { transform: translateY(-7px); box-shadow: 0 16px 48px rgba(0,0,0,0.14); }
.c1 { background: linear-gradient(170deg,#fffef0,#fff8d0); border: 2.5px solid #f6c90e; }
.c2 { background: linear-gradient(170deg,#f2f7ff,#dce9fb); border: 2.5px solid #90b8e8; }
.c3 { background: linear-gradient(170deg,#fff6ef,#f7e4d0); border: 2.5px solid #d4a270; }

.card-rank-title { font-size: 0.68rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: #8a9ab5; margin-bottom: 0.6rem; }
.card-name { font-size: 1.15rem; font-weight: 700; color: #2d3748; margin: 0.3rem 0; line-height: 1.3; }
.card-unit { font-size: 0.74rem; color: #8a9ab5; line-height: 1.5; margin-bottom: 0.9rem; }
.score-pill { display: inline-block; background: linear-gradient(135deg, #4a90e2, #7b68ee);
    color: white; padding: 0.32rem 1.2rem; border-radius: 50px; font-size: 0.88rem; font-weight: 700;
    box-shadow: 0 3px 12px rgba(74,144,226,0.35); }
.label-pill { display: inline-block; background: #e6f9f1; color: #38a169;
    padding: 0.22rem 1rem; border-radius: 50px; font-size: 0.76rem; font-weight: 600; margin-top: 0.5rem; }
.stat-row { margin-top: 0.7rem; }
.chip { display: inline-block; background: rgba(74,144,226,0.1); color: #4a6fa5;
    border-radius: 30px; padding: 0.15rem 0.65rem; font-size: 0.72rem; font-weight: 500; margin: 0.15rem 0.1rem; }
.photo-circle { width: 115px; height: 115px; border-radius: 50%; object-fit: cover;
    margin: 0 auto 0.8rem; display: block; border: 4px solid white; box-shadow: 0 5px 18px rgba(0,0,0,0.14); }
.photo-placeholder { width: 115px; height: 115px; border-radius: 50%;
    background: linear-gradient(135deg, #b8d4f5, #d5c8f8);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 0.8rem; font-size: 3.2rem; border: 4px solid white; box-shadow: 0 5px 18px rgba(0,0,0,0.12); }
.video-wrap { background: white; border-radius: 20px; padding: 1.4rem 1.6rem;
    box-shadow: 0 4px 22px rgba(0,0,0,0.07); margin-top: 1.8rem; }
.video-label { font-size: 0.95rem; font-weight: 600; color: #4a90e2; text-align: center; margin-bottom: 1rem; }
.stats-strip { background: white; border-radius: 18px; padding: 1.4rem 1.8rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07); margin-top: 1.6rem; }
.snum { font-size: 2rem; font-weight: 800; color: #4a90e2; }
.slabel { font-size: 0.75rem; color: #8a9ab5; font-weight: 500; }
.footer { text-align:center; color:#b0bec5; font-size:0.75rem; margin-top:2rem; padding-bottom:1.5rem; }

section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, #2c3a50 0%, #3d4f68 100%); padding-top: 1.5rem;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span { color: #dce8f7 !important; }
section[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.12) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 10px !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────
for k, v in {"admin_ok": False, "top3": None, "all_df": None,
             "photos": {}, "yt_id": "IUN664s7N-c", "periode": "Februari 2026"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ────────────────────────────────────────────────────────
def extract_yt_id(url):
    for pat in [r"v=([\w-]+)", r"youtu\.be/([\w-]+)", r"embed/([\w-]+)"]:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return url.strip()

def process_excel(file):
    df = pd.read_excel(file, header=0)
    df.columns = [str(c).strip() for c in df.columns]
    for c in ["Total Jam","Skor Produktivitas","Hari Tercatat","Skor Konsistensi (%)","Rata-rata Jam/Hari","Total Log"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[df["Nama Pegawai"].notna()].copy()
    sort_cols = [c for c in ["Skor Produktivitas","Total Jam"] if c in df.columns]
    return df.sort_values(sort_cols, ascending=[False]*len(sort_cols)).head(3).reset_index(drop=True), df

def render_photo(rank_num, emoji):
    if rank_num in st.session_state.photos and st.session_state.photos[rank_num]:
        b64 = base64.b64encode(st.session_state.photos[rank_num]).decode()
        return f'<img src="data:image/jpeg;base64,{b64}" class="photo-circle"/>'
    return f'<div class="photo-placeholder">{emoji}</div>'

# ── ADMIN SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔐 Panel Admin")
    st.markdown("---")
    if not st.session_state.admin_ok:
        pwd = st.text_input("Password Admin", type="password", placeholder="Ketik password...")
        if st.button("Masuk", use_container_width=True):
            if pwd == "fipp@2026":
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Password salah!")
    else:
        st.markdown("**Selamat datang, Admin!**")
        st.markdown("---")

        st.markdown("**1. Upload File Excel**")
        xls = st.file_uploader("File .xlsx", type=["xlsx"], label_visibility="collapsed")
        if xls:
            try:
                top3, all_df = process_excel(xls)
                st.session_state.top3   = top3
                st.session_state.all_df = all_df
                st.success("Data terupdate!")
            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("**2. Upload Foto Pegawai**")
        for i, badge in enumerate(["Peringkat 1 (Medali Emas)", "Peringkat 2 (Perak)", "Peringkat 3 (Perunggu)"], 1):
            ph = st.file_uploader(badge, type=["jpg","jpeg","png"], key=f"p{i}")
            if ph:
                st.session_state.photos[i] = ph.read()
                st.success(f"Foto {i} tersimpan!")

        st.markdown("---")
        st.markdown("**3. URL Video YouTube**")
        yt_input = st.text_input("URL YouTube", value=f"https://youtu.be/{st.session_state.yt_id}", label_visibility="collapsed")

        st.markdown("**4. Periode**")
        periode_input = st.text_input("Periode", value=st.session_state.periode, label_visibility="collapsed")

        st.markdown("---")
        if st.button("Simpan Pengaturan", use_container_width=True, type="primary"):
            if yt_input:
                st.session_state.yt_id = extract_yt_id(yt_input)
            if periode_input:
                st.session_state.periode = periode_input
            st.success("Tersimpan!")
            st.balloons()

        if st.button("Logout", use_container_width=True):
            st.session_state.admin_ok = False
            st.rerun()

# ── LOAD DEFAULT DATA ──────────────────────────────────────────────
if st.session_state.top3 is None:
    try:
        top3, all_df = process_excel("logbook_summary_2026_Februari-1.xlsx")
        st.session_state.top3   = top3
        st.session_state.all_df = all_df
    except:
        pass

# ── HEADER ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-wrap">
  <h1>Apresiasi Pegawai Terbaik</h1>
  <p class="sub1">Fakultas Ilmu Pendidikan dan Psikologi &nbsp;|&nbsp; Universitas Negeri Semarang</p>
  <p class="sub2">Periode: {st.session_state.periode} &nbsp;&middot;&nbsp; Berdasarkan Skor Produktivitas Logbook</p>
</div>
""", unsafe_allow_html=True)

# ── TOP 3 CARDS ───────────────────────────────────────────────────
data = st.session_state.top3
cfg = [
    ("🥇","PEGAWAI TERBAIK I","c1"),
    ("🥈","PEGAWAI TERBAIK II","c2"),
    ("🥉","PEGAWAI TERBAIK III","c3"),
]

if data is not None and len(data) >= 1:
    cols = st.columns(3, gap="large")
    for i, col in enumerate(cols):
        if i >= len(data):
            break
        emoji, title, css_cls = cfg[i]
        row = data.iloc[i]
        name   = str(row.get("Nama Pegawai","-"))
        unit   = str(row.get("Unit","-"))
        jam    = row.get("Total Jam",0) or 0
        skor   = row.get("Skor Produktivitas",0) or 0
        label  = str(row.get("Label Produktivitas","-"))
        hari   = row.get("Hari Tercatat","-")
        konsis = row.get("Skor Konsistensi (%)","- ")
        avgjam = row.get("Rata-rata Jam/Hari","- ")
        photo_html = render_photo(i+1, emoji)
        with col:
            st.markdown(f"""
            <div class="card-wrap {css_cls}">
              {photo_html}
              <div class="card-rank-title">{title}</div>
              <div class="card-name">{name}</div>
              <div class="card-unit">{unit}</div>
              <div class="score-pill">Skor {skor:.0f} / 100</div>
              <div class="stat-row">
                <span class="chip">⏱ {jam:.1f} Jam</span>
                <span class="chip">📅 {hari} Hari</span>
                <span class="chip">🎯 {konsis}% Konsisten</span>
                <span class="chip">⚡ {avgjam} Jam/Hari</span>
              </div>
              <div><span class="label-pill">{label}</span></div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Upload file Excel melalui Panel Admin (klik panah di kiri atas).")

# ── VIDEO ─────────────────────────────────────────────────────────
yt = st.session_state.yt_id
embed_url = f"https://www.youtube.com/embed/{yt}?autoplay=1&mute=1&loop=1&playlist={yt}&controls=1&rel=0"
st.markdown('<div class="video-wrap"><div class="video-label">Selamat & Semangat untuk Seluruh Civitas FIPP UNNES</div>', unsafe_allow_html=True)
st.components.v1.iframe(embed_url, height=380, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)

# ── STATISTIK ─────────────────────────────────────────────────────
if st.session_state.all_df is not None:
    df_all = st.session_state.all_df
    total    = len(df_all)
    sangat_p = len(df_all[df_all["Label Produktivitas"] == "Sangat Produktif"]) if "Label Produktivitas" in df_all else 0
    produk   = len(df_all[df_all["Label Produktivitas"] == "Produktif"]) if "Label Produktivitas" in df_all else 0
    avg_skor = df_all["Skor Produktivitas"].mean() if "Skor Produktivitas" in df_all else 0
    st.markdown(f"""
    <div class="stats-strip">
      <div style="text-align:center;font-size:0.9rem;font-weight:600;color:#4a90e2;margin-bottom:1.2rem;">
        Statistik Produktivitas Logbook &mdash; {st.session_state.periode}
      </div>
      <div style="display:flex;justify-content:space-around;flex-wrap:wrap;gap:1rem;">
        <div style="text-align:center"><div class="snum">{total}</div><div class="slabel">Total Pegawai</div></div>
        <div style="text-align:center"><div class="snum" style="color:#38a169">{sangat_p}</div><div class="slabel">Sangat Produktif</div></div>
        <div style="text-align:center"><div class="snum" style="color:#7b68ee">{produk}</div><div class="slabel">Produktif</div></div>
        <div style="text-align:center"><div class="snum" style="color:#f6ad55">{avg_skor:.1f}</div><div class="slabel">Rata-rata Skor</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  FIPP UNNES &nbsp;&middot;&nbsp; Sistem Informasi Apresiasi Pegawai Terbaik &nbsp;&middot;&nbsp; 2026
</div>
""", unsafe_allow_html=True)
