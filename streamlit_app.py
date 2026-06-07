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

# Inisialisasi Session State agar data interaksi tetap terjaga selama perpindahan tab/aktivitas
if "halaman_masuk" not in st.session_state:
    st.session_state.halaman_masuk = False  # True jika pengguna sudah mengklik "Masuk ke Aplikasi"
if "reaksi_dijalankan" not in st.session_state:
    st.session_state.reaksi_dijalankan = False
if "reaksi_hasil" not in st.session_state:
    st.session_state.reaksi_hasil = {}

# Inisialisasi Session State untuk Kuis Step-by-Step
if "kuis_current_idx" not in st.session_state:
    st.session_state.kuis_current_idx = 0
if "kuis_score" not in st.session_state:
    st.session_state.kuis_score = 0
if "kuis_jawab_status" not in st.session_state:
    st.session_state.kuis_jawab_status = None # None, "Benar", atau "Salah"
if "kuis_terjawab" not in st.session_state:
    st.session_state.kuis_terjawab = False # True jika user sudah klik "Submit" pada soal aktif
if "kuis_selesai" not in st.session_state:
    st.session_state.kuis_selesai = False

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="Name the Molecul - Kelompok Kimia", 
    layout="wide",
    page_icon="🧪"
)

# 2. INJEKSI CUSTOM CSS UNTUK TEMA YANG SANGAT COLORFUL & CERIA
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    /* Style untuk tombol utama dengan warna gradasi */
    div.stButton > button {
        background: linear-gradient(135deg, #ff7675, #6c5ce7) !important;
        color: white !important;
        border: none !important;
        padding: 12px 28px !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: scale(1.04) !important;
        box-shadow: 0 6px 20px rgba(108, 92, 231, 0.4) !important;
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
    /* Kartu Edukasi */
    .edu-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. KAMUS PENERJEMAH KIMIA INDONESIA -> INGGRIS
KAMUS_KIMIA = {
    "air": "water",
    "metana": "methane",
    "etana": "ethane",
    "propana": "propane",
    "butana": "butane",
    "pentana": "pentane",
    "heksana": "hexane",
    "heptana": "heptane",
    "oktana": "octane",
    "nonana": "nonane",
    "dekana": "decane",
    "etena": "ethylene",
    "propena": "propylene",
    "butena": "butene",
    "etuna": "acetylene",
    "asetilen": "acetylene",
    "propuna": "propyne",
    "etanol": "ethanol",
    "metanol": "methanol",
    "propanol": "propanol",
    "butanol": "butanol",
    "isopropanol": "isopropanol",
    "gliserol": "glycerol",
    "glukosa": "glucose",
    "fruktosa": "fructose",
    "sukrosa": "sucrose",
    "benzena": "benzene",
    "toluena": "toluene",
    "fenol": "phenol",
    "anilin": "aniline",
    "naftalena": "naphthalene",
    "antrasena": "anthracene",
    "klorobenzena": "chlorobenzene",
    "bromobenzena": "bromobenzene",
    "nitrobenzena": "nitrobenzene",
    "asam asetat": "acetic acid",
    "asam format": "formic acid",
    "asam salisilat": "salicylic acid",
    "asam benzoat": "benzoic acid",
    "asam propanoat": "propanoic acid",
    "asam butanoat": "butanoic acid",
    "aseton": "acetone",
    "propanon": "propanone",
    "formaldehid": "formaldehyde",
    "asetaldehid": "acetaldehyde",
    "kloroform": "chloroform",
    "aspirin": "aspirin",
    "kafein": "caffeine",
    "urea": "urea",
    "etil asetat": "ethyl acetate",
    "metil asetat": "methyl acetate",
    "dimetil eter": "dimethyl ether",
    "dietil eter": "diethyl ether"
}

def terjemahkan_ke_inggris(nama_input):
    nama_bersih = nama_input.strip().lower()
    
    if nama_bersih in KAMUS_KIMIA:
        return KAMUS_KIMIA[nama_bersih]
    
    translated = nama_bersih
    if translated.endswith("ol"):
        pass 
    if translated.endswith("al"):
        pass 
    if translated.endswith("on"):
        pass 
    elif translated.endswith("at"):
        translated = translated[:-2] + "ate" 
    elif translated.startswith("asam "):
        bagian = translated.replace("asam ", "")
        if bagian.endswith("at"):
            translated = bagian[:-2] + "ic acid" 
        else:
            translated = bagian + " acid"
            
    translated = translated.replace("fena", "phena")
    translated = translated.replace("metil", "methyl")
    translated = translated.replace("etil", "ethyl")
    translated = translated.replace("propil", "propyl")
    translated = translated.replace("butil", "butyl")
    translated = translated.replace("isopropil", "isopropyl")
    translated = translated.replace("kloro", "chloro")
    translated = translated.replace("bromo", "bromo")
    translated = translated.replace("iodo", "iodo")
    translated = translated.replace("nitro", "nitro")
    translated = translated.replace("hidroksil", "hydroxyl")
    
    return translated

# 4. FUNGSI DINAMIS UNTUK MENGAMBIL DATA EKSPERIMENTAL PUBCHEM API
def get_boiling_point_and_safety(cid):
    bp_val = "Tidak ditemukan di database eksperimental"
    reactivity_val = "Stabil dalam kondisi normal. Hindari kontak langsung tanpa APD."
    
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            sections = data.get("Record", {}).get("Section", [])
            
            for sec in sections:
                if sec.get("TOCHeading") == "Chemical and Physical Properties":
                    sub_sections = sec.get("Section", [])
                    for sub in sub_sections:
                        if sub.get("TOCHeading") == "Experimental Properties":
                            prop_sections = sub.get("Section", [])
                            for prop in prop_sections:
                                if prop.get("TOCHeading") == "Boiling Point":
                                    info_list = prop.get("Information", [])
                                    if info_list:
                                        bp_val = info_list[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", bp_val)
                                        
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

# ==========================================
# SCREEN DEPAN / LANDING WELCOME PAGE
# ==========================================
if not st.session_state.halaman_masuk:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #6c5ce7, #a29bfe, #fd79a8, #ffeaa7); padding: 60px 40px; border-radius: 30px; color: white; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.15); margin-top: 50px; margin-bottom: 30px;">
        <span style="font-size: 80px;">🧪</span>
        <h1 style="color: white; font-size: 50px; font-weight: 900; font-family: 'Segoe UI', Arial, sans-serif; text-shadow: 2px 2px 8px rgba(0,0,0,0.2); margin-top: 10px;">
            Selamat Datang di Name the Molecul!
        </h1>
        <p style="font-size: 22px; max-width: 800px; margin: 20px auto; opacity: 0.95; line-height: 1.6; font-weight: 500;">
            Masuki dunia seru eksplorasi struktur kimia organik secara 3D! Anda dapat merancang molekul impian, mensimulasikan berbagai reaksi kimia yang menakjubkan, serta menguji pengetahuan tata nama senyawa Anda dengan cara menyenangkan.
        </p>
        <p style="font-size: 16px; font-style: italic; opacity: 0.8; margin-bottom: 30px;">
            Dibuat untuk memenuhi tugas project Praktik Logika Pemrograman Komputer.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #2d3436; margin-bottom: 15px;'>👥 Dipersembahkan oleh Kelompok 11:</h3>", unsafe_allow_html=True)
    
    member_cols = st.columns(4)
    colors = [
        {"bg": "#ffeaa7", "border": "#fdcb6e", "text": "#d35400", "emoji": "🧑‍💻"},
        {"bg": "#dff9fb", "border": "#c7ecee", "text": "#0984e3", "emoji": "👩‍🔬"},
        {"bg": "#ffdfdf", "border": "#ff7675", "text": "#c0392b", "emoji": "👩‍💻"},
        {"bg": "#ebfffa", "border": "#55efc4", "text": "#00b894", "emoji": "👩‍🔬"}
    ]
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
            <div style="background-color: {data['color']['bg']}; padding: 25px; border-radius: 15px; border-top: 5px solid {data['color']['border']}; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); min-height: 150px;">
                <div style="font-size: 35px; margin-bottom: 5px;">{data['color']['emoji']}</div>
                <h4 style="margin: 5px 0 2px 0; color: #2d3436; font-size: 16px; font-weight: bold;">{data['nama']}</h4>
                <p style="margin: 0; color: {data['color']['text']}; font-size: 13px; font-weight: bold;">{data['nim']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    col_btn_center = st.columns([2, 1, 2])
    with col_btn_center[1]:
        if st.button("Masuk ke Aplikasi 🚀", use_container_width=True):
            st.session_state.halaman_masuk = True
            st.rerun()

# ==========================================
# HALAMAN UTAMA APLIKASI
# ==========================================
else:
    if st.sidebar.button("⬅ Kembali ke Halaman Selamat Datang"):
        st.session_state.halaman_masuk = False
        st.rerun()
        
    st.sidebar.markdown("""
    ### 🧬 Menu Navigasi
    Gunakan tab menu di sebelah kanan layar untuk beralih fitur:
    * **🔍 Penjelajah 3D:** Cari senyawa ramah Bahasa Indonesia.
    * **⚡ Lab Reaksi Organik:** Pilih senyawa dan pereaksinya.
    * **📝 Kuis Tata Nama:** Evaluasi interaktif satu per satu soal.
    """)

    tab1, tab2, tab3 = st.tabs(["🔍 Penjelajah 3D", "⚡ Lab Reaksi Organik", "📝 Kuis Tata Nama"])

    # ==========================================
    # TAB 1: PENJELAJAH SENYAWA 3D
    # ==========================================
    with tab1:
        if not IMPORTS_SUCCESSFUL:
            st.error(f"❌ Gagal memuat pustaka kimia. Masalah: {IMPORT_ERROR_MSG}")
        else:
            st.markdown("<h3 style='color: #6c5ce7;'>🔍 Eksplorasi & Visualisasi Senyawa</h3>", unsafe_allow_html=True)
            st.write("Ketik nama senyawa organik secara **IUPAC** atau **Trivial** menggunakan **Bahasa Indonesia** atau **Bahasa Inggris** (Contoh: *etanol*, *asam asetat*, *aspirin*, *benzena*).")
            
            nama_senyawa_input = st.text_input("Ketik Nama Senyawa Kimia:", "etanol", key="search_input")

            if st.button("Analisis & Visualisasikan", key="btn_search"):
                nama_senyawa_en = terjemahkan_ke_inggris(nama_senyawa_input)
                
                with st.spinner(f"Menerjemahkan '{nama_senyawa_input}' ⮕ '{nama_senyawa_en}' dan menyinkronkan dengan PubChem..."):
                    try:
                        hasil_pencarian = pcp.get_compounds(nama_senyawa_en, 'name')
                        if hasil_pencarian:
                            senyawa = hasil_pencarian[0]
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
                            st.error(f"❌ Senyawa '{nama_senyawa_input}' (Pola: '{nama_senyawa_en}') tidak ditemukan. Pastikan ejaan benar atau coba sinonim lainnya.")
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
            
            nama_induk = rantai_alkil.split(" (")[0]
            formula_induk = rantai_alkil.split("(")[1].replace(")", "")
            nama_pereaksi = gugus_reagen.split(" (")[0]
            formula_pereaksi = gugus_reagen.split("(")[1].replace(")", "")
            
            nama_produk = ""
            rumus_produk = ""
            tipe_reaksi_kustom = ""
            penjelasan_kustom = ""
            
            if gugus_reagen == "Alkohol (-OH)":
                tipe_reaksi_kustom = "Substitusi Nukleofilik (Pembentukan Alkohol)"
                if "Metil" in nama_induk:
                    nama_produk = "Metanol"
                    rumus_produk = "CH3OH"
                    penjelasan_kustom = "Metil halida diserang oleh nukleofil hidroksida (OH⁻) melalui reaksi satu tahap (SN2) menghasilkan Metanol."
                elif "Etil" in nama_induk:
                    nama_produk = "Etanol"
                    rumus_produk = "C2H5OH"
                    penjelasan_kustom = "Etil halida bereaksi dengan basa kuat encer (seperti NaOH encer) menghasilkan Etanol."
                elif "Propil" in nama_induk:
                    nama_produk = "1-Propanol"
                    rumus_produk = "C3H7OH"
                    penjelasan_kustom = "Substitusi nukleofilik pada karbon primer menghasilkan propanol primer."
                elif "Isopropil" in nama_induk:
                    nama_produk = "2-Propanol (Isopropanol)"
                    rumus_produk = "(CH3)2CHOH"
                    penjelasan_kustom = "Substitusi nukleofilik pada karbon sekunder menghasilkan alkohol sekunder."
                elif "Fenil" in nama_induk:
                    nama_produk = "Fenol"
                    rumus_produk = "C6H5OH"
                    penjelasan_kustom = "Dibuat dari hidrolisis klorobenzena pada kondisi suhu tinggi dan tekanan ekstrim (Proses Dow)."

            elif gugus_reagen == "Aldehid (-CHO)":
                tipe_reaksi_kustom = "Oksidasi / Karbonilasi"
                if "Metil" in nama_induk:
                    nama_produk = "Etanal (Asetaldehid)"
                    rumus_produk = "CH3CHO"
                    penjelasan_kustom = "Penambahan gugus aldehid membentuk rantai aldehid beranggotakan dua atom karbon."
                elif "Etil" in nama_induk:
                    nama_produk = "Propanal"
                    rumus_produk = "C2H5CHO"
                    penjelasan_kustom = "Gugus karbonil berada di ujung rantai dengan panjang tiga atom karbon."
                elif "Propil" in nama_induk:
                    nama_produk = "Butanal"
                    rumus_produk = "C3H7CHO"
                    penjelasan_kustom = "Oksidasi butanol primer menggunakan pereaksi selektif menghasilkan Butanal."
                elif "Isopropil" in nama_induk:
                    nama_produk = "2-Metilpropanal"
                    rumus_produk = "(CH3)2CHCHO"
                    penjelasan_kustom = "Membentuk aldehid bercabang dengan rantai induk propanal."
                elif "Fenil" in nama_induk:
                    nama_produk = "Benzaldehid"
                    rumus_produk = "C6H5CHO"
                    penjelasan_kustom = "Oksidasi parsial Toluena menghasilkan senyawa aromatis beraroma khas amandel."

            elif gugus_reagen == "Keton (-CO-CH3)":
                tipe_reaksi_kustom = "Asilasi Friedel-Crafts / Adisi"
                if "Metil" in nama_induk:
                    nama_produk = "Propanon (Aseton)"
                    rumus_produk = "CH3COCH3"
                    penjelasan_kustom = "Senyawa keton paling sederhana dan sering digunakan sebagai pelarut universal."
                elif "Etil" in nama_induk:
                    nama_produk = "Butanon"
                    rumus_produk = "C2H5COCH3"
                    penjelasan_kustom = "Senyawa keton rantai lurus berkarbon empat."
                elif "Propil" in nama_induk:
                    nama_produk = "2-Pentanon"
                    rumus_produk = "C3H7COCH3"
                    penjelasan_kustom = "Terbentuk senyawa keton asimetris dengan gugus fungsi karbonil di posisi karbon nomor dua."
                elif "Isopropil" in nama_induk:
                    nama_produk = "3-Metil-2-butanon"
                    rumus_produk = "(CH3)2CHCOCH3"
                    penjelasan_kustom = "Keton bercabang yang mempertahankan struktur awal isopropil."
                elif "Fenil" in nama_induk:
                    nama_produk = "Asetofenon"
                    rumus_produk = "C6H5COCH3"
                    penjelasan_kustom = "Dibuat lewat reaksi asilasi Friedel-Crafts benzena dengan bantuan asam Lewis AlCl3."

            elif gugus_reagen == "Asam Karboksilat (-COOH)":
                tipe_reaksi_kustom = "Karbonilasi / Hidrolisis"
                if "Metil" in nama_induk:
                    nama_produk = "Asam Etanoat (Asam Asetat)"
                    rumus_produk = "CH3COOH"
                    penjelasan_kustom = "Oksidasi etanol secara biologis atau kimiawi menghasilkan senyawa cuka makan."
                elif "Etil" in nama_induk:
                    nama_produk = "Asam Propanoat"
                    rumus_produk = "C2H5COOH"
                    penjelasan_kustom = "Asam karboksilat berkarbon tiga."
                elif "Propil" in nama_induk:
                    nama_produk = "Asam Butanoat"
                    rumus_produk = "C3H7COOH"
                    penjelasan_kustom = "Asam karboksilat berkarbon empat yang beraroma menyengat mentega tengik."
                elif "Isopropil" in nama_induk:
                    nama_produk = "Asam 2-Metilpropanoat"
                    rumus_produk = "(CH3)2CHCOOH"
                    penjelasan_kustom = "Asam karboksilat bercabang."
                elif "Fenil" in nama_induk:
                    nama_produk = "Asam Benzoat"
                    rumus_produk = "C6H5COOH"
                    penjelasan_kustom = "Zat pengawet makanan yang didapat melalui oksidasi keras Toluena."

            elif gugus_reagen == "Eter (-O-CH3)":
                tipe_reaksi_kustom = "Sintesis Eter Williamson"
                if "Metil" in nama_induk:
                    nama_produk = "Metoksimetana (Dimetil Eter)"
                    rumus_produk = "CH3OCH3"
                    penjelasan_kustom = "Metoksida menyerang metil halida menghasilkan eter simetris terkecil."
                elif "Etil" in nama_induk:
                    nama_produk = "Metoksietana (Etil Metil Eter)"
                    rumus_produk = "C2H5OCH3"
                    penjelasan_kustom = "Eter asimetris hasil reaksi natrium metoksida dan etil iodida."
                elif "Propil" in nama_induk:
                    nama_produk = "1-Metoksipropana"
                    rumus_produk = "C3H7OCH3"
                    penjelasan_kustom = "Sintesis eter asimetris melalui substitusi nukleofilik."
                elif "Isopropil" in nama_induk:
                    nama_produk = "2-Metoksipropana"
                    rumus_produk = "(CH3)2CHOCH3"
                    penjelasan_kustom = "Sintesis eter bercabang sekunder."
                elif "Fenil" in nama_induk:
                    nama_produk = "Anisol (Metoksibenzena)"
                    rumus_produk = "C6H5OCH3"
                    penjelasan_kustom = "Natrium fenoksida bereaksi dengan metil halida menghasilkan eter aromatik."

            elif gugus_reagen == "Ester (-COOCH3)":
                tipe_reaksi_kustom = "Esterifikasi / Substitusi Asil"
                if "Metil" in nama_induk:
                    nama_produk = "Metil Asetat"
                    rumus_produk = "CH3COOCH3"
                    penjelasan_kustom = "Esterifikasi asam asetat dengan metanol."
                elif "Etil" in nama_induk:
                    nama_produk = "Metil Propanoat"
                    rumus_produk = "C2H5COOCH3"
                    penjelasan_kustom = "Ester dengan aroma buah apel manis."
                elif "Propil" in nama_induk:
                    nama_produk = "Metil Butanoat"
                    rumus_produk = "C3H7COOCH3"
                    penjelasan_kustom = "Ester dengan aroma nanas yang segar."
                elif "Isopropil" in nama_induk:
                    nama_produk = "Metil Isobutirat"
                    rumus_produk = "(CH3)2CHCOOCH3"
                    penjelasan_kustom = "Ester bercabang dengan aroma manis buah-buahan."
                elif "Fenil" in nama_induk:
                    nama_produk = "Metil Benzoat"
                    rumus_produk = "C6H5COOCH3"
                    penjelasan_kustom = "Terbentuk melalui reaksi kondensasi asam benzoat dan metanol."

            elif "Halogen" in gugus_reagen:
                hal_sym = "Cl" if "Klorida" in gugus_reagen else "Br"
                hal_name = "Klorida" if "Klorida" in gugus_reagen else "Bromida"
                hal_prefix = "Kloro" if "Klorida" in gugus_reagen else "Bromo"
                tipe_reaksi_kustom = "Halogenasi Radikal Bebas / Substitusi Elektrofilik"
                
                if "Metil" in nama_induk:
                    nama_produk = f"Metil {hal_name}"
                    rumus_produk = f"CH3{hal_sym}"
                    penjelasan_kustom = "Substitusi radikal bebas alkana dengan gas halogen di bawah paparan sinar UV."
                elif "Etil" in nama_induk:
                    nama_produk = f"Etil {hal_name}"
                    rumus_produk = f"C2H5{hal_sym}"
                    penjelasan_kustom = "Halogenasi terkontrol pada senyawa etana."
                elif "Propil" in nama_induk:
                    nama_produk = f"1-{hal_prefix}propana"
                    rumus_produk = f"C3H7{hal_sym}"
                    penjelasan_kustom = "Halogenasi selektif propena pada suhu tinggi atau adisi peroksida."
                elif "Isopropil" in nama_induk:
                    nama_produk = f"2-{hal_prefix}propana"
                    rumus_produk = f"(CH3)2CH{hal_sym}"
                    penjelasan_kustom = "Adisi asam halida sesuai Hukum Markovnikov pada propena."
                elif "Fenil" in nama_induk:
                    nama_produk = f"{hal_prefix}benzena"
                    rumus_produk = f"C6H5{hal_sym}"
                    penjelasan_kustom = "Substitusi Elektrofilik Aromatik menggunakan katalis asam Lewis (FeCl3 atau FeBr3)."
       
            st.session_state.reaksi_hasil = {
                "induk": formula_induk,
                "reagen": formula_pereaksi,
                "tipe": tipe_reaksi_kustom,
                "produk": nama_produk,
                "rumus": rumus_produk,
                "penjelasan": penjelasan_kustom
            }

        # Merender Hasil Reaksi agar tetap persisten di layar
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
            
            # KAMUS PARSER LATEX OTOMATIS SUPAYA REAKSI KIMIA RENDER CANTIK DAN PROPORSIONAL
            LATEX_MAP = {
                "CH3-": r"\text{CH}_3\text{-}", "C2H5-": r"\text{C}_2\text{H}_5\text{-}", "C3H7-": r"\text{C}_3\text{H}_7\text{-}", "(CH3)2CH-": r"\text{(CH}_3\text{)}_2\text{CH-}", "C6H5-": r"\text{C}_6\text{H}_5\text{-}",
                "-OH": r"\text{-OH}", "-CHO": r"\text{-CHO}", "-CO-CH3": r"\text{-CO-CH}_3", "-COOH": r"\text{-COOH}", "-O-CH3": r"\text{-O-CH}_3", "-COOCH3": r"\text{-COO-CH}_3", "-Cl": r"\text{-Cl}", "-Br": r"\text{-Br}",
                "CH3OH": r"\text{CH}_3\text{OH}", "C2H5OH": r"\text{C}_2\text{H}_5\text{OH}", "C3H7OH": r"\text{C}_3\text{H}_7\text{OH}", "(CH3)2CHOH": r"\text{(CH}_3\text{)}_2\text{CHOH}", "C6H5OH": r"\text{C}_6\text{H}_5\text{OH}",
                "CH3CHO": r"\text{CH}_3\text{CHO}", "C2H5CHO": r"\text{C}_2\text{H}_5\text{CHO}", "C3H7CHO": r"\text{C}_3\text{H}_7\text{CHO}", "(CH3)2CHCHO": r"\text{(CH}_3\text{)}_2\text{CHCHO}", "C6H5CHO": r"\text{C}_6\text{H}_5\text{CHO}",
                "CH3COCH3": r"\text{CH}_3\text{COCH}_3", "C2H5COCH3": r"\text{C}_2\text{H}_5\text{COCH}_3", "C3H7COCH3": r"\text{C}_3\text{H}_7\text{COCH}_3", "(CH3)2CHCOCH3": r"\text{(CH}_3\text{)}_2\text{CHCOCH}_3", "C6H5COCH3": r"\text{C}_6\text{H}_5\text{COCH}_3",
                "CH3COOH": r"\text{CH}_3\text{COOH}", "C2H5COOH": r"\text{C}_2\text{H}_5\text{COOH}", "C3H7COOH": r"\text{C}_3\text{H}_7\text{COOH}", "(CH3)2CHCOOH": r"\text{(CH}_3\text{)}_2\text{CHCOOH}", "C6H5COOH": r"\text{C}_6\text{H}_5\text{COOH}",
                "CH3OCH3": r"\text{CH}_3\text{OCH}_3", "C2H5OCH3": r"\text{C}_2\text{H}_5\text{OCH}_3", "C3H7OCH3": r"\text{C}_3\text{H}_7\text{OCH}_3", "(CH3)2CHOCH3": r"\text{(CH}_3\text{)}_2\text{CHOCH}_3", "C6H5OCH3": r"\text{C}_6\text{H}_5\text{OCH}_3",
                "CH3COOCH3": r"\text{CH}_3\text{COOCH}_3", "C2H5COOCH3": r"\text{C}_2\text{H}_5\text{COOCH}_3", "C3H7COOCH3": r"\text{C}_3\text{H}_7\text{COOCH}_3", "(CH3)2CHCOOCH3": r"\text{(CH}_3\text{)}_2\text{CHCOOCH}_3", "C6H5COOCH3": r"\text{C}_6\text{H}_5\text{COOCH}_3",
                "CH3Cl": r"\text{CH}_3\text{Cl}", "CH3Br": r"\text{CH}_3\text{Br}", "C2H5Cl": r"\text{C}_2\text{H}_5\text{Cl}", "C2H5Br": r"\text{C}_2\text{H}_5\text{Br}", "C3H7Cl": r"\text{C}_3\text{H}_7\text{Cl}", "C3H7Br": r"\text{C}_3\text{H}_7\text{Br}",
                "(CH3)2CHCl": r"\text{(CH}_3\text{)}_2\text{CHCl}", "(CH3)2CHBr": r"\text{(CH}_3\text{)}_2\text{CHBr}", "C6H5Cl": r"\text{C}_6\text{H}_5\text{Cl}", "C6H5Br": r"\text{C}_6\text{H}_5\text{Br}"
            }
            
            l_induk = LATEX_MAP.get(res['induk'], rf"\text{{{res['induk']}}}")
            l_reagen = LATEX_MAP.get(res['reagen'], rf"\text{{{res['reagen']}}}")
            l_rumus = LATEX_MAP.get(res['rumus'], rf"\text{{{res['rumus']}}}")
            
            st.write("")
            st.latex(f"{l_induk} + {l_reagen} \longrightarrow {l_rumus}")

        st.markdown("<hr style='border: 0.5px dashed #ccc;'>", unsafe_allow_html=True)
        st.markdown("#### 📚 Pustaka Reaksi Kimia Organik Lengkap")
        st.info("Gunakan form pilihan di atas untuk melihat visualisasi persamaan reaksi yang terbentuk secara otomatis.")

    # ==========================================
    # TAB 3: KUIS TATA NAMA INTERAKTIF (STEP-BY-STEP)
    # ==========================================
    with tab3:
        st.markdown("<h3 style='color: #6c5ce7;'>📝 Kuis Evaluasi Tata Nama Senyawa</h3>", unsafe_allow_html=True)
        
        # Bank Data Soal Kuis Kelompok 11
        KUIS_DATA = [
            {
                "soal": "Berdasarkan sistem IUPAC, apa nama senyawa hidrokarbon turunan alkana dengan rumus struktur metil yang berikatan dengan gugus fungsi alkohol (CH3-OH)?",
                "pilihan": ["Metanal", "Metanol", "Asam Metanoat", "Metoksimetana"],
                "kunci": "Metanol",
                "pembahasan": "Senyawa CH3-OH memiliki rantai alkil berupa metil (1 atom karbon) dan gugus fungsi alkohol (-OH). Sesuai aturan IUPAC, nama rantai alkana induk (metana) diganti akhiran -a menjadi -ol, menghasilkan nama Metanol."
            },
            {
                "soal": "Manakah gugus fungsi pereaksi di bawah ini yang mencirikan senyawa kelompok Keton (Alkanon)?",
                "pilihan": ["-OH", "-CHO", "-CO-CH3", "-COOH"],
                "kunci": "-CO-CH3",
                "pembahasan": "Gugus -CO-CH3 (karbonil di antara radikal alkil) merepresentasikan karakteristik senyawa golongan keton. Sedangkan -OH adalah alkohol, -CHO adalah aldehid, dan -COOH adalah asam karboksilat."
            },
            {
                "soal": "Senyawa asam karboksilat dengan rumus molekul CH3COOH sering kita temukan di dapur rumah sebagai asam cuka. Apa nama Trivial (umum) dari senyawa tersebut?",
                "pilihan": ["Asam Format", "Asam Propanoat", "Asam Asetat", "Asam Butanoat"],
                "kunci": "Asam Asetat",
                "pembahasan": "Senyawa CH3COOH memiliki nama resmi IUPAC Asam Etanoat, namun secara komersial dan trivial ia paling populer dikenal sebagai Asam Asetat (Asam Cuka)."
            }
        ]
        
        # Logika Render Kuis Berdasarkan Status Selesai
        if st.session_state.kuis_selesai:
            st.balloons()
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #55efc4, #00b894); padding: 40px; border-radius: 20px; text-align: center; color: white; box-shadow: 0 10px 25px rgba(0,184,148,0.25);">
                <h2 style="color: white; margin-top:0;">🏁 Selamat! Kuis Telah Selesai</h2>
                <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">Skor Akhir Anda: {st.session_state.kuis_score} / {len(KUIS_DATA)}</p>
                <p style="opacity: 0.9;">Kerja bagus Kelompok 11! Logika sistem kuis satu per satu soal berjalan lancar.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button("Ulangi Kuis Dari Awal 🔄", use_container_width=True):
                st.session_state.kuis_current_idx = 0
                st.session_state.kuis_score = 0
                st.session_state.kuis_jawab_status = None
                st.session_state.kuis_terjawab = False
                st.session_state.kuis_selesai = False
                st.rerun()
        else:
            current_idx = st.session_state.kuis_current_idx
            soal_aktif = KUIS_DATA[current_idx]
            
            # Header nomor soal aktif
            st.markdown(f"#### 📋 Pertanyaan No. {current_idx + 1} dari {len(KUIS_DATA)}")
            
            # Box Soal
            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #6c5ce7; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 20px;">
                <p style="font-size: 16px; font-weight: 500; color: #2d3436; margin: 0;">{soal_aktif['soal']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Pilihan Ganda menggunakan Radio Button Dinamis
            pilihan_user = st.radio(
                "Pilih salah satu jawaban di bawah ini:",
                soal_aktif["pilihan"],
                key=f"radio_soal_{current_idx}",
                disabled=st.session_state.kuis_terjawab
            )
            
            st.write("")
            
            # Tombol Aksi Kuis: Submit atau Lanjut
            if not st.session_state.kuis_terjawab:
                if st.button("Submit Jawaban ✔️", use_container_width=True):
                    st.session_state.kuis_terjawab = True
                    if pilihan_user == soal_aktif["kunci"]:
                        st.session_state.kuis_score += 1
                        st.session_state.kuis_jawab_status = "Benar"
                    else:
                        st.session_state.kuis_jawab_status = "Salah"
                    st.rerun()
            else:
                # Evaluasi Alert Banner Benar / Salah
                if st.session_state.kuis_jawab_status == "Benar":
                    st.success(f"🎉 Hebat! Jawaban Anda Benar: **{soal_aktif['kunci']}**")
                else:
                    st.error(f"❌ Kurang tepat! Jawaban yang benar adalah: **{soal_aktif['kunci']}**")
                
                # Menampilkan PEMBAHASAN langsung setelah submit di klik
                st.markdown(f"""
                <div style="background-color: #fff9f4; padding: 20px; border-radius: 10px; border-left: 5px solid #fdcb6e; margin-bottom: 25px; margin-top: 10px;">
                    <h5 style="color: #e67e22; margin-top: 0; font-weight: bold;">💡 Pembahasan Soal:</h5>
                    <p style="font-size: 14px; color: #2d3436; margin: 0; line-height: 1.5;">{soal_aktif['pembahasan']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Tombol navigasi dinamis (Lanjut No berikutnya / Lihat hasil)
                if current_idx < len(KUIS_DATA) - 1:
                    if st.button(f"Klik untuk Pembahasan & Lanjut ke No. {current_idx + 2} ➡️", use_container_width=True):
                        st.session_state.kuis_current_idx += 1
                        st.session_state.kuis_terjawab = False
                        st.session_state.kuis_jawab_status = None
                        st.rerun()
                else:
                    if st.button("Selesai & Lihat Hasil Akhir Kuis 🏁", use_container_width=True):
                        st.session_state.kuis_selesai = True
                        st.rerun()
