import streamlit as st
import requests
import time

# 1. JARING PENGAMAN IMPORT
try:
    import pubchempy as pcp
    from stmol import showmol
    import py3Dmol
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    IMPORTS_SUCCESSFUL = False
    IMPORT_ERROR_MSG = str(e)

# Konfigurasi halaman utama
st.set_page_config(
    page_title="ChemExplorer Ultimate - Proyek Kelompok", 
    layout="wide",
    page_icon="🧬"
)

# 2. INJEKSI CUSTOM CSS UNTUK TEMA PROFESIONAL & COLORFUL
st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    .main-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .quiz-card {
        background: white; padding: 30px; border-radius: 20px;
        border-top: 8px solid #6c5ce7; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        color: white; border: none; border-radius: 10px;
        padding: 12px 30px; font-weight: bold; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 3. HEADER & IDENTITAS KELOMPOK
st.markdown("""
<div style="background: linear-gradient(135deg, #0984e3, #6c5ce7, #fd79a8); padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 25px;">
    <h1 style="color: white; margin: 0; font-size: 45px;">🧪 ChemExplorer Ultimate v3.0</h1>
    <p style="font-size: 18px; opacity: 0.9;">Solusi Cerdas Belajar Kimia Organik: Visualisasi, Reaksi & Kuis Interaktif</p>
</div>
""", unsafe_allow_html=True)

# Tampilkan Anggota (Versi Ringkas agar hemat ruang)
with st.expander("👥 Lihat Anggota Kelompok"):
    cols = st.columns(4)
    names = ["Anggota 1", "Anggota 2", "Anggota 3", "Anggota 4"]
    for i, col in enumerate(cols):
        col.markdown(f"<div style='text-align:center; padding:10px; background:white; border-radius:10px;'><b>{names[i]}</b><br><small>NIM. 210xxxx</small></div>", unsafe_allow_html=True)

# 4. NAVIGASI TABS
tab1, tab2, tab3 = st.tabs(["🔍 Penjelajah 3D", "⚡ Lab Reaksi", "📝 Game Kuis"])

# ==========================================
# TAB 1: PENJELAJAH SENYAWA 3D
# ==========================================
with tab1:
    st.markdown("### 🔍 Visualisasi Molekul Interaktif")
    nama_senyawa = st.text_input("Ketik Nama Senyawa (Inggris):", "Aspirin")
    
    if st.button("Cari & Render 3D"):
        with st.spinner("Mengambil data..."):
            try:
                hasil = pcp.get_compounds(nama_senyawa, 'name')
                if hasil:
                    c = hasil[0]
                    k1, k2 = st.columns([1, 2])
                    with k1:
                        st.markdown(f"""<div class='main-card'>
                        <h4>Data Senyawa</h4>
                        <b>IUPAC:</b> {c.iupac_name}<br>
                        <b>Rumus:</b> <span style='color:red;'>{c.molecular_formula}</span><br>
                        <b>Massa:</b> {c.molecular_weight} g/mol
                        </div>""", unsafe_allow_html=True)
                    with k2:
                        url_3d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{c.cid}/record/SDF/?record_type=3d"
                        res = requests.get(url_3d)
                        view = py3Dmol.view(width=600, height=400)
                        view.addModel(res.text, 'sdf')
                        view.setStyle({'stick': {'radius':0.2}, 'sphere': {'radius':0.45}})
                        view.zoomTo()
                        showmol(view, height=400, width=600)
                else: st.error("Senyawa tidak ditemukan.")
            except: st.error("Database sedang sibuk.")

# ==========================================
# TAB 2: LAB REAKSI (STATIC & DYNAMIC)
# ==========================================
with tab2:
    st.markdown("### ⚡ Laboratorium Reaksi Organik")
    
    # --- FITUR BARU: DYNAMIC REACTOR ---
    st.markdown("#### 🛠️ Reaktor Mandiri (Custom Reaction)")
    st.write("Gabungkan gugus di bawah untuk memprediksi produknya:")
    
    col_a, col_b = st.columns(2)
    alkil = col_a.selectbox("Pilih Gugus Alkil:", ["Metana (CH3-)", "Etana (C2H5-)", "Benzena (C6H5-)"])
    fungsi = col_b.selectbox("Pilih Gugus Fungsi:", ["Alkohol (-OH)", "Klorida (-Cl)", "Asam Karboksilat (-COOH)"])
    
    if st.button("Jalankan Reaksi Custom"):
        # Logika sederhana pembuat produk
        map_alkil = {"Metana (CH3-)": "Metil", "Etana (C2H5-)": "Etil", "Benzena (C6H5-)": "Fenil"}
        map_prod = {
            "Alkohol (-OH)": " Alkohol (Produk: ",
            "Klorida (-Cl)": " Klorida (Produk: ",
            "Asam Karboksilat (-COOH)": " (Produk: Asam "
        }
        
        # Penamaan khusus
        if fungsi == "Alkohol (-OH)": 
            final = "Metanol" if alkil.startswith("Metana") else "Etanol" if alkil.startswith("Etana") else "Fenol"
        elif fungsi == "Klorida (-Cl)":
            final = "Metil Klorida" if alkil.startswith("Metana") else "Etil Klorida" if alkil.startswith("Etana") else "Klorobenzena"
        else:
            final = "Asam Metanoat" if alkil.startswith("Metana") else "Asam Etanoat" if alkil.startswith("Etana") else "Asam Benzoat"
            
        st.success(f"🧪 Hasil Reaksi: {alkil} + {fungsi} ⮕ **{final}**")
        st.latex(f"R + X \\rightarrow R-X")

    st.markdown("---")
    st.markdown("#### 📚 Pustaka Reaksi Organik Lengkap")
    list_reaksi = {
        "Substitusi: Benzena + CH3Cl": "C_6H_6 + CH_3Cl \\xrightarrow{AlCl_3} C_6H_5CH_3 + HCl",
        "Adisi: Etena + H2": "CH_2=CH_2 + H_2 \\xrightarrow{Ni} CH_3-CH_3",
        "Eliminasi: Etanol + H2SO4": "CH_3CH_2OH \\xrightarrow{H_2SO_4, 180^oC} CH_2=CH_2 + H_2O",
        "Oksidasi: Metanol": "CH_3OH + [O] \\rightarrow HCHO + H_2O",
        "Saponifikasi (Sabun)": "R-COOR' + NaOH \\rightarrow R-COONa + R'OH",
        "Pembakaran Metana": "CH_4 + 2O_2 \\rightarrow CO_2 + 2H_2O"
    }
    pilihan = st.selectbox("Pilih Reaksi dari Database:", list(list_reaksi.keys()))
    st.latex(list_reaksi[pilihan])

# ==========================================
# TAB 3: GAME KUIS TATA NAMA (UI BARU)
# ==========================================
with tab3:
    st.markdown("<div style='text-align:center;'><h2>🏆 Tantangan Tata Nama IUPAC</h2><p>Uji pengetahuanmu dan jadilah Master Kimia!</p></div>", unsafe_allow_html=True)
    
    # Progress Bar
    if 'current_q' not in st.session_state: st.session_state.current_q = 0
    if 'score' not in st.session_state: st.session_state.score = 0
    
    soal = [
        {"p": "CH3-CH2-CH3 adalah...", "a": ["Metana", "Etana", "Propana", "Butana"], "b": "Propana"},
        {"p": "Gugus fungsi -CHO adalah ciri khas dari...", "a": ["Alkohol", "Aldehid", "Keton", "Ester"], "b": "Aldehid"},
        {"p": "Nama IUPAC dari C2H5OH adalah...", "a": ["Metanol", "Etanol", "Propanol", "Fenol"], "b": "Etanol"},
        {"p": "Senyawa Benzena dengan gugus -CH3 disebut...", "a": ["Anilin", "Fenol", "Toluena", "Stirena"], "b": "Toluena"},
        {"p": "Rumus umum Alkena adalah...", "a": ["CnH2n+2", "CnH2n", "CnH2n-2", "CnHn"], "b": "CnH2n"},
        {"p": "Asam cuka memiliki nama IUPAC...", "a": ["Asam Metanoat", "Asam Etanoat", "Asam Semut", "Etanol"], "b": "Asam Etanoat"},
        {"p": "CH3-CO-CH3 adalah...", "a": ["Propanal", "Propanon", "Etanon", "Metanon"], "b": "Propanon"},
        {"p": "Gugus fungsi -O- menunjukkan senyawa...", "a": ["Ester", "Eter", "Keton", "Alkohol"], "b": "Eter"},
        {"p": "Nama dari CH3-CH2-CH2-COOH adalah...", "a": ["Asam Propanoat", "Asam Butanoat", "Asam Pentanoat", "Butanal"], "b": "Asam Butanoat"},
        {"p": "C2H2 termasuk golongan...", "a": ["Alkana", "Alkena", "Alkuna", "Sikloalkana"], "b": "Alkuna"}
    ]

    # Cek apakah sudah selesai
    if st.session_state.current_q < len(soal):
        cur = st.session_state.current_q
        st.progress((cur) / len(soal))
        
        st.markdown(f"""<div class='quiz-card'>
            <small>Pertanyaan {cur+1} dari {len(soal)}</small>
            <h3>{soal[cur]['p']}</h3>
        </div>""", unsafe_allow_html=True)
        
        jawaban = st.radio("Pilih jawaban yang benar:", soal[cur]['a'], key=f"q_{cur}")
        
        if st.button("Konfirmasi Jawaban ⮕"):
            if jawaban == soal[cur]['b']:
                st.session_state.score += 10
                st.balloons()
                st.success("✨ Luar Biasa! Jawabanmu Benar.")
            else:
                st.error(f"❌ Kurang Tepat. Jawaban yang benar adalah: {soal[cur]['b']}")
            
            time.sleep(1.5)
            st.session_state.current_q += 1
            st.rerun()
    else:
        st.markdown(f"""<div style='text-align:center; padding:50px; background:white; border-radius:20px;'>
            <h1>🏁 Kuis Selesai!</h1>
            <h2 style='color:#6c5ce7;'>Skor Akhir Anda: {st.session_state.score} / 100</h2>
        </div>""", unsafe_allow_html=True)
        if st.button("Ulangi Kuis"):
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.rerun()
