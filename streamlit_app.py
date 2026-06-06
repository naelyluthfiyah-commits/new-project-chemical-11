import streamlit as st
import requests

# 1. JARING PENGAMAN IMPORT: Menjaga web tetap berjalan meskipun library kimia sedang dimuat
try:
    import pubchempy as pcp
    from stmol import showmol
    import py3Dmol
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    IMPORTS_SUCCESSFUL = False
    IMPORT_ERROR_MSG = str(e)

# Inisialisasi Session State agar input dan hasil kuis/reaksi tidak hilang saat halaman memuat ulang
if "kuis_dikirim" not in st.session_state:
    st.session_state.kuis_dikirim = False
if "skor_total" not in st.session_state:
    st.session_state.skor_total = 0
if "pembahasan" not in st.session_state:
    st.session_state.pembahasan = []
if "reaksi_dijalankan" not in st.session_state:
    st.session_state.reaksi_dijalankan = False
if "reaksi_hasil" not in st.session_state:
    st.session_state.reaksi_hasil = {}

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="ChemExplorer Pro - Kelompok Kimia", 
    layout="wide",
    page_icon="🧪"
)

# 2. INJEKSI CUSTOM CSS UNTUK TEMA YANG SANGAT COLORFUL & CERIA (Sesuai Desain Awal)
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    /* Style untuk tombol Cari & Reaksi */
    div.stButton > button {
        background: linear-gradient(135deg, #ff7675, #6c5ce7) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 5px 15px rgba(108, 92, 231, 0.4) !important;
    }
    /* Gaya untuk Tab Navigasi */
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: bold;
        color: #2d3436;
    }
    .stTabs [aria-selected="true"] {
        color: #6c5ce7 !important;
        border-bottom-color: #6c5ce7 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. COVER WEB & BANNER SELAMAT DATANG (GRADASI COLORFUL)
st.markdown("""
<div style="background: linear-gradient(135deg, #6c5ce7, #a29bfe, #fd79a8, #ffeaa7); padding: 45px; border-radius: 20px; color: white; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.15); margin-bottom: 30px;">
    <h1 style="color: white; margin: 0; font-size: 42px; font-weight: 800; font-family: 'Segoe UI', Arial, sans-serif; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
        🧪 ChemExplorer Pro 3D
    </h1>
    <p style="font-size: 18px; opacity: 0.95; margin-top: 10px; margin-bottom: 0; font-weight: 500; letter-spacing: 0.5px;">
        Platform Interaktif Visualisasi Molekul 3D & Laboratorium Reaksi Kimia Organik
    </p>
</div>
""", unsafe_allow_html=True)

# 4. BAGIAN ANGGOTA KELOMPOK (DENGAN TEMA WARNA-WARNI, HANYA NAMA & NIM)
st.markdown("<h3 style='text-align: center; color: #2d3436; font-weight: 700; margin-top: 15px; margin-bottom: 20px;'>👥 Tim Peneliti / Anggota Kelompok</h3>", unsafe_allow_html=True)

member_cols = st.columns(4)

colors = [
    {"bg": "#ffeaa7", "border": "#fdcb6e", "text": "#d35400", "emoji": "🧑‍💻"}, # Kuning Pastel
    {"bg": "#dff9fb", "border": "#c7ecee", "text": "#0984e3", "emoji": "👩‍🔬"}, # Biru Mint Pastel
    {"bg": "#ffdfdf", "border": "#ff7675", "text": "#c0392b", "emoji": "👩‍💻"}, # Pink/Merah Pastel
    {"bg": "#ebfffa", "border": "#55efc4", "text": "#00b894", "emoji": "🕵️‍♀️"}  # Hijau Pastel
]

# Data Anggota Kelompok (Tanpa Peran/Role)
members_data = [
    {"nama": "Andika Dwi Prashojo", "nim": "NIM. 2560571", "color": colors[0]},
    {"nama": "Jawaher Sabrina Alodya A. S.", "nim": "NIM. 2560648", "color": colors[1]},
    {"nama": "Naely Luthfiyah Arif", "nim": "NIM. 2560698", "color": colors[2]},
    {"nama": "Salwa Azka Sabana", "nim": "NIM. 2560767", "color": colors[3]},
]

for idx, col in enumerate(member_cols):
    data = members_data[idx]
    with col:
        st.markdown(f"""
        <div style="background-color: {data['color']['bg']}; padding: 20px; border-radius: 15px; border-top: 5px solid {data['color']['border']}; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); min-height: 140px;">
            <div style="font-size: 30px; margin-bottom: 5px;">{data['color']['emoji']}</div>
            <h4 style="margin: 5px 0 2px 0; color: #2d3436; font-size: 15px; font-weight: bold;">{data['nama']}</h4>
            <p style="margin: 0; color: {data['color']['text']}; font-size: 13px; font-weight: bold;">{data['nim']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='border: 1px solid #dfe6e9; margin: 35px 0;'>", unsafe_allow_html=True)

# 5. FUNGSI DINAMIS UNTUK MENGAMBIL TITIK DIDIH DAN REAKTIVITAS DARI PUBCHEM API
def get_boiling_point_and_safety(cid):
    bp_val = "Tidak ditemukan di database eksperimental"
    reactivity_val = "Stabil dalam kondisi normal. Hindari kontak langsung tanpa APD."
    
    try:
        # Panggil API XML/JSON PubChem untuk data eksperimental detail
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            sections = data.get("Record", {}).get("Section", [])
            
            for sec in sections:
                # Cari Bagian Sifat Kimia & Fisika (Chemical and Physical Properties)
                if sec.get("TOCHeading") == "Chemical and Physical Properties":
                    sub_sections = sec.get("Section", [])
                    for sub in sub_sections:
                        if sub.get("TOCHeading") == "Experimental Properties":
                            prop_sections = sub.get("Section", [])
                            for prop in prop_sections:
                                # Dapatkan Titik Didih
                                if prop.get("TOCHeading") == "Boiling Point":
                                    info_list = prop.get("Information", [])
                                    if info_list:
                                        bp_val = info_list[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", bp_val)
                                        
                # Cari Bagian Keselamatan & Reaktivitas (Safety and Hazard)
                if sec.get("TOCHeading") == "Safety and Hazard Properties":
                    sub_sections = sec.get("Section", [])
                    for sub in sub_sections:
                        if sub.get("TOCHeading") == "Hazards Identification":
                            prop_sections = sub.get("Section", [])
                            for prop in prop_sections:
                                if prop.get("TOCHeading") == "GHS Classification":
                                    info_list = prop.get("Information", [])
                                    if info_list:
                                        markup_list = info_list[0].get("Value", {}).get("StringWithMarkup", [{}])
                                        if markup_list:
                                            reactivity_val = markup_list[0].get("String", reactivity_val)
    except Exception:
        pass
        
    return bp_val, reactivity_val

# 6. MENYUSUN NAVIGASI TABS
tab1, tab2, tab3 = st.tabs(["🔍 Penjelajah 3D", "⚡ Lab Reaksi Organik", "📝 Kuis Tata Nama"])

# ==========================================
# TAB 1: PENJELAJAH SENYAWA 3D
# ==========================================
with tab1:
    if not IMPORTS_SUCCESSFUL:
        st.error(f"❌ Gagal memuat pustaka kimia. Masalah: {IMPORT_ERROR_MSG}")
    else:
        st.markdown("<h3 style='color: #6c5ce7;'>🔍 Eksplorasi & Visualisasi Senyawa</h3>", unsafe_allow_html=True)
        nama_senyawa = st.text_input("Ketik Nama Senyawa Kimia (Inggris):", "Ethanol", key="search_input")

        if st.button("Analisis & Visualisasikan", key="btn_search"):
            with st.spinner("Menghubungkan ke database PubChem..."):
                try:
                    hasil_pencarian = pcp.get_compounds(nama_senyawa, 'name')
                    if hasil_pencarian:
                        senyawa = hasil_pencarian[0]
                        
                        # Ambil Titik Didih dan Reaktivitas Riil dari API
                        titik_didih, bahaya_reaktivitas = get_boiling_point_and_safety(senyawa.cid)
                        
                        kol1, kol2 = st.columns(2)
                        
                        with kol1:
                            st.markdown(f"""
                            <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 5px solid #6c5ce7;">
                                <h4 style="color: #6c5ce7; margin-top: 0;">📝 Informasi Senyawa</h4>
                                <p style="color: #2ecc71; font-weight: bold; font-size: 15px;">✓ Berhasil Sinkronisasi (CID: {senyawa.cid})</p>
                                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                                    <tr style="border-bottom: 1px solid #f1f2f6;"><td style="padding: 8px 0; font-weight: bold;">Nama IUPAC</td><td style="color: #636e72;">{getattr(senyawa, 'iupac_name', 'Tidak tersedia')}</td></tr>
                                    <tr style="border-bottom: 1px solid #f1f2f6;"><td style="padding: 8px 0; font-weight: bold;">Rumus Molekul</td><td style="color: #e84393; font-weight: bold;">{getattr(senyawa, 'molecular_formula', 'Tidak tersedia')}</td></tr>
                                    <tr style="border-bottom: 1px solid #f1f2f6;"><td style="padding: 8px 0; font-weight: bold;">Berat Molekul</td><td style="color: #636e72;">{getattr(senyawa, 'molecular_weight', 'Tidak tersedia')} g/mol</td></tr>
                                    <tr style="border-bottom: 1px solid #f1f2f6;"><td style="padding: 8px 0; font-weight: bold; color: #ff7675;">🌡️ Titik Didih (Real)</td><td style="color: #ff7675; font-weight: bold;">{titik_didih}</td></tr>
                                </table>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.write("")
                            st.markdown(f"""
                            <div style="background-color: #fff2f2; padding: 20px; border-radius: 12px; border-left: 5px solid #ff7675;">
                                <h5 style="color: #d63031; margin-top:0;">⚠️ Klasifikasi Bahaya & Reaktivitas:</h5>
                                <p style="font-size: 13px; color: #2d3436; margin: 0;">{bahaya_reaktivitas}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with kol2:
                            st.markdown("""
                            <div style="background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 5px solid #fd79a8;">
                                <h4 style="color: #fd79a8; margin-top: 0;">🧬 Visualisasi Model 3D (Gaya Molymod)</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            url_3d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{senyawa.cid}/record/SDF/?record_type=3d"
                            respon = requests.get(url_3d, timeout=10)
                            
                            if respon.status_code == 200 and len(respon.text) > 100:
                                view = py3Dmol.view(width=450, height=350)
                                view.addModel(respon.text, 'sdf')
                                view.setStyle({'stick': {'radius': 0.2}, 'sphere': {'radius': 0.45}})
                                view.setBackgroundColor('#ffffff')
                                view.zoomTo()
                                showmol(view, height=350, width=450)
                                st.caption("👆 Tarik molekul dengan mouse untuk memutar. Scroll untuk memperbesar/memperkecil.")
                            else:
                                st.warning("⚠️ Struktur 3D tidak tersedia di database.")
                    else:
                        st.error("❌ Senyawa tidak ditemukan. Gunakan ejaan bahasa Inggris (Contoh: 'Water' untuk Air).")
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# TAB 2: LAB REAKSI ORGANIK
# ==========================================
with tab2:
    st.markdown("<h3 style='color: #e17055;'>⚡ Laboratorium Mekanisme Reaksi Organik</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #fff9f4; padding: 25px; border-radius: 15px; border-left: 5px solid #ff7675; box-shadow: 0 4px 15px rgba(0,0,0,0.02); margin-bottom: 25px;">
        <h4 style="color: #d63031; margin-top:0;">🛠️ Reaktor Kustom Dinamis</h4>
        <p>Tentukan senyawa alkil (rantai induk) Anda, lalu reaksikan dengan berbagai reagen/gugus fungsi pilihan Anda di bawah ini!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        rantai_alkil = st.selectbox(
            "Pilih Rantai Induk (Alkil/Aril):",
            [
                "Metil (CH3-)", 
                "Etil (C2H5-)", 
                "Propil (C3H7-)", 
                "Isopropil ((CH3)2CH-)", 
                "Fenil/Benzena (C6H5-)"
            ]
        )
        
    with col_input2:
        gugus_reagen = st.selectbox(
            "Pilih Gugus Fungsi Pereaksi:",
            [
                "Alkohol (-OH)", 
                "Aldehid (-CHO)", 
                "Keton (-CO-CH3)", 
                "Asam Karboksilat (-COOH)", 
                "Eter (-O-CH3)", 
                "Ester (-COOCH3)", 
                "Halogen / Klorida (-Cl)",
                "Halogen / Bromida (-Br)"
            ]
        )
        
    if st.button("Jalankan Reaksi Kustom 🧪"):
        st.session_state.reaksi_dijalankan = True
        
        # Logika Prediksi Reaksi Kimia Organik
        nama_induk = rantai_alkil.split(" (")[0]
        formula_induk = rantai_alkil.split("(")[1].replace(")", "")
        nama_pereaksi = gugus_reagen.split(" (")[0]
        formula_pereaksi = gugus_reagen.split("(")[1].replace(")", "")
        
        nama_produk = ""
        rumus_produk = ""
        tipe_reaksi_kustom = ""
        penjelasan_kustom = ""
        
        # Logika Kombinasi Produk
        if gugus_reagen == "Alkohol (-OH)":
            tipe_reaksi_kustom = "Substitusi Nukleofilik (Pembentukan Alkohol)"
            if "Metil" in nama_induk:
                nama_produk = "Metanol"
                rumus_produk = "CH_3OH"
                penjelasan_kustom = "Metil halida diserang oleh nukleofil hidroksida (OH⁻) melalui reaksi satu tahap (SN2) menghasilkan Metanol."
            elif "Etil" in nama_induk:
                nama_produk = "Etanol"
                rumus_produk = "C_2H_5OH"
                penjelasan_kustom = "Etil halida bereaksi dengan basa kuat encer (sekat NaOH encer) menghasilkan Etanol."
            elif "Propil" in nama_induk:
                nama_produk = "1-Propanol"
                rumus_produk = "C_3H_7OH"
                penjelasan_kustom = "Substitusi nukleofilik pada karbon primer menghasilkan propanol primer."
            elif "Isopropil" in nama_induk:
                nama_produk = "2-Propanol (Isopropanol)"
                rumus_produk = "(CH_3)_2CHOH"
                penjelasan_kustom = "Substitusi nukleofilik pada karbon sekunder menghasilkan alkohol sekunder."
            elif "Fenil" in nama_induk:
                nama_produk = "Fenol"
                rumus_produk = "C_6H_5OH"
                penjelasan_kustom = "Dibuat dari hidrolisis klorobenzena pada kondisi suhu tinggi dan tekanan ekstrim (Proses Dow)."

        elif gugus_reagen == "Aldehid (-CHO)":
            tipe_reaksi_kustom = "Oksidasi / Karbonilasi"
            if "Metil" in nama_induk:
                nama_produk = "Etanal (Asetaldehid)"
                rumus_produk = "CH_3CHO"
                penjelasan_kustom = "Penambahan gugus aldehid membentuk rantai aldehid beranggotakan dua atom karbon."
            elif "Etil" in nama_induk:
                nama_produk = "Propanal"
                rumus_produk = "C_2H_5CHO"
                penjelasan_kustom = "Gugus karbonil berada di ujung rantai dengan panjang tiga atom karbon."
            elif "Propil" in nama_induk:
                nama_produk = "Butanal"
                rumus_produk = "C_3H_7CHO"
                penjelasan_kustom = "Oksidasi butanol primer menggunakan pereaksi selektif menghasilkan Butanal."
            elif "Isopropil" in nama_induk:
                nama_produk = "2-Metilpropanal"
                rumus_produk = "(CH_3)_2CHCHO"
                penjelasan_kustom = "Membentuk aldehid bercabang dengan rantai induk propanal."
            elif "Fenil" in nama_induk:
                nama_produk = "Benzaldehid"
                rumus_produk = "C_6H_5CHO"
                penjelasan_kustom = "Oksidasi parsial Toluena menghasilkan senyawa aromatis beraroma khas amandel."

        elif gugus_reagen == "Keton (-CO-CH3)":
            tipe_reaksi_kustom = "Asilasi Friedel-Crafts / Adisi"
            if "Metil" in nama_induk:
                nama_produk = "Propanon (Aseton)"
                rumus_produk = "CH_3COCH_3"
                penjelasan_kustom = "Senyawa keton paling sederhana dan sering digunakan sebagai pelarut universal."
            elif "Etil" in nama_induk:
                nama_produk = "Butanon"
                rumus_produk = "C_2H_5COCH_3"
                penjelasan_kustom = "Senyawa keton rantai lurus berkarbon empat."
            elif "Propil" in nama_induk:
                nama_produk = "2-Pentanon"
                rumus_produk = "C_3H_7COCH_3"
                penjelasan_kustom = "Terbentuk senyawa keton asimetris dengan gugus fungsi karbonil di posisi karbon nomor dua."
            elif "Isopropil" in nama_induk:
                nama_produk = "3-Metil-2-butanon"
                rumus_produk = "(CH_3)_2CHCOCH_3"
                penjelasan_kustom = "Keton bercabang yang mempertahankan struktur awal isopropil."
            elif "Fenil" in nama_induk:
                nama_produk = "Asetofenon"
                rumus_produk = "C_6H_5COCH_3"
                penjelasan_kustom = "Dibuat lewat reaksi asilasi Friedel-Crafts benzena dengan bantuan asam Lewis AlCl3."

        elif gugus_reagen == "Asam Karboksilat (-COOH)":
            tipe_reaksi_kustom = "Karbonilasi / Hidrolisis"
            if "Metil" in nama_induk:
                nama_produk = "Asam Etanoat (Asam Asetat)"
                rumus_produk = "CH_3COOH"
                penjelasan_kustom = "Oksidasi etanol secara biologis atau kimiawi menghasilkan senyawa cuka makan."
            elif "Etil" in nama_induk:
                nama_produk = "Asam Propanoat"
                rumus_produk = "C_2H_5COOH"
                penjelasan_kustom = "Asam karboksilat berkarbon tiga."
            elif "Propil" in nama_induk:
                nama_produk = "Asam Butanoat"
                rumus_produk = "C_3H_7COOH"
                penjelasan_kustom = "Asam karboksilat berkarbon empat yang beraroma menyengat mentega tengik."
            elif "Isopropil" in nama_induk:
                nama_produk = "Asam 2-Metilpropanoat"
                rumus_produk = "(CH_3)_2CHCOOH"
                penjelasan_kustom = "Asam karboksilat bercabang."
            elif "Fenil" in nama_induk:
                nama_produk = "Asam Benzoat"
                rumus_produk = "C_6H_5COOH"
                penjelasan_kustom = "Zat pengawet makanan yang didapat melalui oksidasi keras Toluena."

        elif gugus_reagen == "Eter (-O-CH3)":
            tipe_reaksi_kustom = "Sintesis Eter Williamson"
            if "Metil" in nama_induk:
                nama_produk = "Metoksimetana (Dimetil Eter)"
                rumus_produk = "CH_3OCH_3"
                penjelasan_kustom = "Metoksida menyerang metil halida menghasilkan eter simetris terkecil."
            elif "Etil" in nama_induk:
                nama_produk = "Metoksietana (Etil Metil Eter)"
                rumus_produk = "C_2H_5OCH_3"
                penjelasan_kustom = "Eter asimetris hasil reaksi natrium metoksida dan etil iodida."
            elif "Propil" in nama_induk:
                nama_produk = "1-Metoksipropana"
                rumus_produk = "C_3H_7OCH_3"
                penjelasan_kustom = "Sintesis eter asimetris melalui substitusi nukleofilik."
            elif "Isopropil" in nama_induk:
                nama_produk = "2-Metoksipropana"
                rumus_produk = "(CH_3)_2CHOCH_3"
                penjelasan_kustom = "Sintesis eter bercabang sekunder."
            elif "Fenil" in nama_induk:
                nama_produk = "Anisol (Metoksibenzena)"
                rumus_produk = "C_6H_5OCH_3"
                penjelasan_kustom = "Natrium fenoksida bereaksi dengan metil halida menghasilkan eter aromatik."
            elif gugus_reagen == "Ester (-COOCH3)":
                tipe_reaksi_kustom = "Esterifikasi / Substitusi Asil"
            if "Metil" in nama_induk:
                nama_produk = "Metil Asetat"
                rumus_produk = "CH_3COOCH_3"
                penjelasan_kustom = "Esterifikasi asam asetat dengan metanol."
            elif "Etil" in nama_induk:
                nama_produk = "Metil Propanoat"
                rumus_produk = "C_2H_5COOCH_3"
                penjelasan_kustom = "Ester dengan aroma buah apel manis."
            elif "Propil" in nama_induk:
                nama_produk = "Metil Butanoat"
                rumus_produk = "C_3H_7COOCH_3"
                penjelasan_kustom = "Ester dengan aroma nanas yang segar."
            elif "Isopropil" in nama_induk:
                nama_produk = "Metil Isobutirat"
                rumus_produk = "(CH_3)_2CHCOOCH_3"
                penjelasan_kustom = "Ester bercabang dengan aroma manis buah-buahan."
            elif "Fenil" in nama_induk:
                nama_produk = "Metil Benzoat"
                rumus_produk = "C_6H_5COOCH_3"
                penjelasan_kustom = "Terbentuk melalui reaksi kondensasi asam benzoat dan metanol."

        elif "Halogen" in gugus_reagen:
            hal_sym = "Cl" if "Klorida" in gugus_reagen else "Br"
            hal_name = "Klorida" if "Klorida" in gugus_reagen else "Bromida"
            hal_prefix = "Kloro" if "Klorida" in gugus_reagen else "Bromo"
            tipe_reaksi_kustom = "Halogenasi Radikal Bebas / Substitusi Elektrofilik"
            
            if "Metil" in nama_induk:
                nama_produk = f"Metil {hal_name}"
                rumus_produk = f"CH_3{hal_sym}"
                penjelasan_kustom = "Substitusi radikal bebas alkana dengan gas halogen di bawah paparan sinar UV."
            elif "Etil" in nama_induk:
                nama_produk = f"Etil {hal_name}"
                rumus_produk = f"C_2H_5{hal_sym}"
                penjelasan_kustom = "Halogenasi terkontrol pada senyawa etana."
            elif "Propil" in nama_induk:
                nama_produk = f"1-{hal_prefix}propana"
                rumus_produk = f"C_3H_7{hal_sym}"
                penjelasan_kustom = "Halogenasi selektif propena pada suhu tinggi atau adisi peroksida."
            elif "Isopropil" in nama_induk:
                nama_produk = f"2-{hal_prefix}propana"
                rumus_produk = f"(CH_3)_2CH{hal_sym}"
                penjelasan_kustom = "Adisi asam halida sesuai Hukum Markovnikov pada propena."
            elif "Fenil" in nama_induk:
                nama_produk = f"{hal_prefix}benzena"
                rumus_produk = f"C_6H_5{hal_sym}"
                penjelasan_kustom = "Substitusi Elektrofilik Aromatik menggunakan katalis asam Lewis (FeCl3 atau FeBr3)."

        # Simpan hasil ke dalam session state agar tidak hilang saat di-render
        st.session_state.reaksi_hasil = {
            "induk": formula_induk,
            "reagen": formula_pereaksi,
            "tipe": tipe_reaksi_kustom,
            "produk": nama_produk,
            "rumus": rumus_produk,
            "penjelasan": penjelasan_kustom
        }

    # Merender Hasil Reaksi secara persist (tetap ada di layar)
    if st.session_state.reaksi_dijalankan:
        res = st.session_state.reaksi_hasil
        st.markdown(f"""
        <div style="background-color: #ebfffa; padding: 25px; border-radius: 12px; border: 1.5px solid #55efc4; margin-top: 20px;">
            <h4 style="color: #00b894; margin-top: 0;">🎉 JAWABAN REAKSI BERHASIL DIANALISIS!</h4>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                <tr><td style="width:30%; font-weight:bold;">Tipe Reaksi:</td><td>{res['tipe']}</td></tr>
                <tr><td style="font-weight:bold;">Nama IUPAC Produk:</td><td style="color:#d63031; font-weight:bold; font-size:16px;">{res['produk']}</td></tr>
            </table>
            <p><b>Mekanisme Reaksi:</b> {res['penjelasan']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(f"\\text{{{res['induk']}}} + \\text{{{res['reagen']}}} \\longrightarrow \\text{{{res['rumus']}}}")

    st.markdown("<hr style='border: 0.5px dashed #ccc;'>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # DATABASE REAKSI STATIS
    # ----------------------------------------------------
    st.markdown("#### 📚 Pustaka Reaksi Kimia Organik Lengkap")
    st.write("Gunakan pilihan menu di bawah untuk mempelajari berbagai jenis reaksi organik esensial:")

    opsi_reaksi = st.selectbox(
        "Pilih Contoh Reaksi Kimia dari Database:",
        [
            "1. Alkilasi Friedel-Crafts (Benzena + CH3Cl)", 
            "2. Esterifikasi Fischer (Asam Asetat + Etanol)", 
            "3. Hidrogenasi Alkena (Etena + H2)",
            "4. Eliminasi / Dehidrasi Alkohol (Etanol ke Etena)",
            "5. Oksidasi Alkohol Primer (Metanol ke Metanal)",
            "6. Reaksi Saponifikasi (Penyabunan Ester)",
            "7. Brominasi Alkena (Etena + Br2 / Uji Ikatan Rangkap)",
            "8. Hidrolisis Amida (Asetamida dalam Asam)"
        ]
    )

    if "1." in opsi_reaksi:
        st.markdown("""
        <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #e17055;">
            <h4 style="color: #d63031; margin-top:0;">🧪 Alkilasi Friedel-Crafts (Substitusi Elektrofilik)</h4>
            <p>Reaksi ini berfungsi memasukkan gugus alkil ke dalam inti Benzena yang kaya elektron menggunakan katalis asam Lewis.</p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{C}_6\text{H}_6 \text (Benzena) + \text{CH}_3\text{Cl} \xrightarrow{\text{AlCl}_3} \text{C}_6\text{H}_5\text{CH}_3 \text (Toluena) + \text{HCl}")

    elif "2." in opsi_reaksi:
        st.markdown("""
        <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #0984e3;">
            <h4 style="color: #0984e3; margin-top:0;">🧪 Esterifikasi Fischer (Kondensasi Asam)</h4>
            <p>Kombinasi asam karboksilat dan alkohol di bawah pengaruh asam sulfat pekat untuk menghasilkan ester aromatik buah-buahan.</p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{CH}_3\text{COOH} + \text{CH}_3\text{CH}_2\text{OH} \xrightarrow{\text{H}_2\text{SO}_4} \text{CH}_3\text{COOCH}_2\text{CH}_3 \text (Etil Asetat) + \text{H}_2\text{O}")

    elif "3." in opsi_reaksi:
        st.markdown("""
        <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #2ecc71;">
            <h4 style="color: #2ecc71; margin-top:0;">🧪 Hidrogenasi Katalitik (Reaksi Adisi)</h4>
            <p>Reaksi penjenuhan hidrokarbon alifatik dengan menambahkan gas hidrogen pada ikatan rangkap dua alkena.</p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{CH}_2\text{=CH}_2 + \text{H}_2 \xrightarrow{\text{Ni, Pt, atau Pd}} \text{CH}_3\text{-CH}_3 \text (Etana)")

    elif "4." in opsi_reaksi:
        st.markdown("""
        <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #fd79a8;">
            <h4 style="color: #e84393; margin-top:0;">🧪 Dehidrasi Alkohol (Reaksi Eliminasi)</h4>
            <p>Pelepasan molekul air dari alkohol rantai pendek untuk membentuk senyawa alkena menggunakan agen dehidrator asam pada suhu tinggi.</p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{CH}_3\text{CH}_2\text{OH} \xrightarrow{\text{H}_2\text{SO}_4, 180^\circ\text{C}} \text{CH}_2\text{=CH}_2 + \text{H}_2\text{O}")

    elif "5." in opsi_reaksi:
        st.markdown("""
        <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #ffeaa7;">
            <h4 style="color: #d35400; margin-top:0;">🧪 Oksidasi Terkontrol Alkohol Primer</h4>
            <p>Oksidasi alkohol primer menggunakan agen pengoksidasi sedang seperti PCC (Pyridinium Chlorochromate) menghasilkan aldehid.</p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{CH}_3\text{OH} + \text{[O]} \xrightarrow{\text{PCC}} \text{HCHO (Metanal)} + \text{H}_2\text{O}")

    elif "6." in opsi_reaksi:
        st.markdown("""
        <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #20bf6b;">
            <h4 style="color: #26de81; margin-top:0;">🧪 Reaksi Saponifikasi (Penyabunan)</h4>
            <p>Hidrolisis ester rantai panjang (lemak/minyak) menggunakan basa kuat alkali untuk membentuk molekul gliserol dan garam karboksilat (sabun).</p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{R-COOR'} + \text{NaOH} \longrightarrow \text{R-COONa (Sabun)} + \text{R'-OH}")

    elif "7." in opsi_reaksi:
        st.markdown("""
        <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #8854d0;">
            <h4 style="color: #3867d6; margin-top:0;">🧪 Adisi Halogen (Brominasi)</h4>
            <p>Reaksi identifikasi ikatan rangkap. Warna cokelat kemerahan dari larutan air brom ($Br_2$) akan memudar menjadi bening saat beradisi dengan alkena.</p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{CH}_2\text{=CH}_2 + \text{Br}_2 \longrightarrow \text{CH}_2\text{Br-CH}_2\text{Br (1,2-Dibromoetana)}")

    elif "8." in opsi_reaksi:
        st.markdown("""
        <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #4b5563;">
            <h4 style="color: #1f2937; margin-top:0;">🧪 Hidrolisis Amida</h4>
            <p>Pemutusan ikatan amida karbonil-nitrogen dengan mereaksikannya bersama air dalam suasana asam panas menghasilkan asam karboksilat dan garam amonium.</p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{CH}_3\text{CONH}_2 + \text{H}_2\text{O} + \text{HCl} \longrightarrow \text{CH}_3\text{COOH} + \text{NH}_4\text{Cl}")

# ==========================================
# TAB 3: GAME KUIS TATA NAMA (MENYENANGKAN & COLORFUL)
# ==========================================
with tab3:
    st.markdown("<h3 style='color: #00b894;'>🏆 Tantangan Cerdas: Kuis Tata Nama IUPAC</h3>", unsafe_allow_html=True)
    st.write("Kerjakan 10 soal di bawah ini. Hasil skor, persentase kelulusan, dan ulasan kunci jawaban akan langsung tertera!")

    # Menggunakan form agar interaksi tidak me-refresh halaman Streamlit di setiap klik
    with st.form("kuis_tata_nama_v3"):
        
        # Soal 1
        st.markdown("<div style='background-color:#ffeaa7; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 1:</b> Apa nama IUPAC alkana rantai lurus dengan struktur CH3-CH2-CH2-CH3?</div>", unsafe_allow_html=True)
        q1 = st.radio("", ["Propana", "Butana", "Pentana", "Heksana"], key="k1")
        
        # Soal 2
        st.markdown("<div style='background-color:#dff9fb; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 2:</b> Gugus fungsi aldehid dituliskan secara sistematis sebagai...</div>", unsafe_allow_html=True)
        q2 = st.radio("", ["-OH", "-CO-", "-CHO", "-COOH"], key="k2")
        
        # Soal 3
        st.markdown("<div style='background-color:#ffdfdf; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 3:</b> Senyawa hidrokarbon tidak jenuh CH3-CH=CH-CH3 diberi nama...</div>", unsafe_allow_html=True)
        q3 = st.radio("", ["1-Butena", "2-Butena", "Butuna", "Metilpropena"], key="k3")
        
        # Soal 4
        st.markdown("<div style='background-color:#ebfffa; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 4:</b> Nama IUPAC dari senyawa alkohol CH3-CH2-OH adalah...</div>", unsafe_allow_html=True)
        q4 = st.radio("", ["Metanol", "Etanol", "Propanol", "Gliserol"], key="k4")
        
        # Soal 5
        st.markdown("<div style='background-color:#ffeaa7; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 5:</b> Asam cuka (CH3-COOH) memiliki nama IUPAC sistematis berupa...</div>", unsafe_allow_html=True)
        q5 = st.radio("", ["Asam Metanoat", "Asam Etanoat", "Asam Propanoat", "Asam Asetat"], key="k5")
        
        # Soal 6
        st.markdown("<div style='background-color:#dff9fb; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 6:</b> Cincin Benzena yang berikatan langsung dengan gugus -OH disebut...</div>", unsafe_allow_html=True)
        q6 = st.radio("", ["Toluena", "Anilin", "Fenol", "Asam Benzoat"], key="k6")
        
        # Soal 7
        st.markdown("<div style='background-color:#ffdfdf; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 7:</b> Jika gugus metil (-CH3) melekat pada cincin benzena, nama senyawa tersebut adalah...</div>", unsafe_allow_html=True)
        q7 = st.radio("", ["Toluena", "Klorobenzena", "Stirena", "Nitrobenzena"], key="k7")
        
        # Soal 8
        st.markdown("<div style='background-color:#ebfffa; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 8:</b> Apa nama IUPAC untuk struktur eter simetris CH3-O-CH3?</div>", unsafe_allow_html=True)
        q8 = st.radio("", ["Dimetil Eter", "Metoksimetana", "Etoksimetana", "Metoksietana"], key="k8")
        
        # Soal 9
        st.markdown("<div style='background-color:#ffeaa7; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 9:</b> Senyawa keton terkecil CH3-CO-CH3 (aseton) memiliki nama resmi IUPAC...</div>", unsafe_allow_html=True)
        q9 = st.radio("", ["Propanal", "Propanon", "Butanon", "Etanon"], key="k9")
        
        # Soal 10
        st.markdown("<div style='background-color:#dff9fb; padding:15px; border-radius:10px; margin-bottom:10px;'><b>Pertanyaan 10:</b> Senyawa ester CH3-COO-CH3 tersusun atas metanol dan asam asetat. Apa nama IUPAC ester tersebut?</div>", unsafe_allow_html=True)
        q10 = st.radio("", ["Metil Metanoat", "Metil Etanoat", "Etil Metanoat", "Asetil Metilat"], key="k10")

        # Tombol Submit Form
        submit_kuis = st.form_submit_button("Kirim Jawaban & Koreksi Massal 📊")

    if submit_kuis:
        st.session_state.kuis_dikirim = True
        
        # Analisis Jawaban & Skor
        skor_total = 0
        pembahasan_list = []
        
        # Validasi tiap soal
        if q1 == "Butana": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 1 salah:** CH3-CH2-CH2-CH3 memiliki 4 karbon jenuh (alkana), dinamakan **Butana**.")
            
        if q2 == "-CHO": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 2 salah:** Gugus aldehid ditulis sistematis sebagai **-CHO**, sedangkan -OH adalah alkohol, -CO- adalah keton, dan -COOH adalah asam karboksilat.")
            
        if q3 == "2-Butena": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 3 salah:** CH3-CH=CH-CH3 memiliki ikatan rangkap dua alkene pada posisi karbon nomor 2, dinamakan **2-Butena**.")
            
        if q4 == "Etanol": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 4 salah:** Senyawa dengan 2 atom karbon (Et-) dan gugus fungsi alkohol (-ol) dinamakan **Etanol**.")
            
        if q5 == "Asam Etanoat": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 5 salah:** CH3-COOH memiliki 2 karbon, sehingga nama IUPAC-nya adalah **Asam Etanoat** (Asam asetat adalah nama trivial).")
            
        if q6 == "Fenol": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 6 salah:** Cincin benzena dengan hidroksil (-OH) dinamakan **Fenol**.")
            
        if q7 == "Toluena": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 7 salah:** Metilbenzena memiliki nama trivial IUPAC yang diakui resmi yaitu **Toluena**.")
            
        if q8 == "Metoksimetana": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 8 salah:** Struktur R-O-R' diberi nama alkoksialkana. CH3-O-CH3 berkarbon 1 di kiri-kanan, dinamai **Metoksimetana**.")
            
        if q9 == "Propanon": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 9 salah:** Keton terhitung dari rantai terpanjang alkana (-on). CH3-CO-CH3 memiliki 3 karbon, dinamakan **Propanon**.")
            
        if q10 == "Metil Etanoat": 
            skor_total += 10
        else: 
            pembahasan_list.append("• **Soal 10 salah:** Struktur ester R-COO-R' dinamakan alkil alkanoat. CH3-COO- (alkanoat 2 karbon = etanoat) dan -CH3 (alkil 1 karbon = metil), jadi namanya **Metil Etanoat**.")

        # Simpan nilai ke Session State agar persisten
        st.session_state.skor_total = skor_total
        st.session_state.pembahasan = pembahasan_list

    # Render hasil kuis secara persisten di layar
    if st.session_state.kuis_dikirim:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("📊 Hasil Evaluasi Skor Kuis:")
        
        skor = st.session_state.skor_total
        pembahasan_show = st.session_state.pembahasan
        
        if skor >= 70:
            st.balloons()
            st.success(f"🎉 **Luar Biasa! Kelompok Anda Lulus!** Skor Akhir: **{skor} / 100**")
        else:
            st.warning(f"📚 **Skor Akhir Kelompok: {skor} / 100**. Tetap semangat belajar kembali tata nama kimia organik!")

        # Menampilkan Pembahasan jika ada kesalahan
        if pembahasan_show:
            st.markdown("##### 🔍 Catatan & Pembahasan Jawaban yang Kurang Tepat:")
            for item in pembahasan_show:
                st.write(item)
        else:
            st.success("✨ Sempurna! Semua jawaban benar!")
