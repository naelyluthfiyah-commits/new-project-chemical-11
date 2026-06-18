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
    page_title="Name the Molecul - Kelompok 11", 
    layout="wide",
    page_icon="🧪"
)

# 2. INJEKSI CUSTOM CSS UNTUK TEMA YANG SANGAT COLORFUL & CERIA (Sesuai Desain Awal)
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

# 3. KAMUS PENERJEMAH KIMIA INDONESIA -> INGGRIS (Menghindari Kegagalan Pencarian PubChem)
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
    elif translated.endswith("al"):
        pass 
    elif translated.endswith("on"):
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
    translated = translated.replace("benz", "benz")
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

# 4. FUNGSI DINAMIS UNTUK MENGAMBIL TITIK DIDIH DAN REAKTIVITAS DARI PUBCHEM API
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
# HALAMAN UTAMA APLIKASI (Setelah Tombol "Masuk" Diklik)
# ==========================================
else:
    if st.sidebar.button("⬅ Kembali ke Halaman Selamat Datang"):
        st.session_state.halaman_masuk = False
        st.rerun()
        
    st.sidebar.markdown("### 🧬 Menu Navigasi")
    st.sidebar.write("Silahkan klik menu di bawah ini untuk berpindah halaman:")

    # PERBAIKAN 1: Mengubah navigasi agar bisa diklik di sidebar
    menu_pilihan = st.sidebar.radio(
        "Pilih Halaman:",
        ["🔍 Penjelajah Senyawa", "⚡ Lab Reaksi Organik", "📝 Kuis Tata Nama"]
    )
    
    # ==========================================
    # TAB 1: PENJELAJAH SENYAWA 3D
    # ==========================================
    if menu_pilihan == "🔍 Penjelajah Senyawa":
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

                                    # --- TAMBAHKAN KODE LEGENDA DI SINI ---
                                    st.markdown("""
                                    <div style="display: flex; gap: 15px; font-size: 13px; margin-top: 10px; background: #f8f9fa; padding: 10px; border-radius: 8px;">
                                        <span>🔵 N (Nitrogen)</span>
                                        <span>🔴 O (Oksigen)</span>
                                        <span>🔘 C (Karbon)</span>
                                        <span>⚪ H (Hidrogen)</span>
                                        <span>🟢 Cl (Klorin)</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    # --------------------------------------
                                    
                                    st.caption("👆 Tarik molekul dengan mouse untuk memutar. Scroll untuk memperbesar/memperkecil.")
                                else:
                                    st.warning("⚠️ Struktur 3D tidak tersedia di database.")
                        else:
                            st.error(f"❌ Senyawa '{nama_senyawa_input}' (Pola: '{nama_senyawa_en}') tidak ditemukan. Pastikan ejaan benar atau coba sinonim trivial lainnya.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ==========================================
    # TAB 2: LAB REAKSI ORGANIK
    # ==========================================
    elif menu_pilihan == "⚡ Lab Reaksi Organik":
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
                    rumus_produk = r"CH_3OH" #Gunakan raw string
                    penjelasan_kustom = "Metil halida diserang oleh nukleofil hidroksida (OH⁻) melalui reaksi satu tahap (SN2) menghasilkan Metanol."
                elif "Etil" in nama_induk:
                    nama_produk = "Etanol"
                    rumus_produk = "C_2H_5OH"
                    penjelasan_kustom = "Etil halida bereaksi dengan basa kuat encer (seperti NaOH encer) menghasilkan Etanol."
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

            st.session_state.reaksi_hasil = {
                "induk": formula_induk,
                "reagen": formula_pereaksi,
                "tipe": tipe_reaksi_kustom,
                "produk": nama_produk,
                "rumus": rumus_produk,
                "penjelasan": penjelasan_kustom
            }

        # Merender Hasil Reaksi secara persist (tetap ada di layar)
        # --- PERBAIKAN: Format penulisan kode latex agar terender rapi ---
        if st.session_state.reaksi_dijalankan:
            res = st.session_state.reaksi_hasil
            st.markdown(f"""
            <div style="background-color: #ebfffa; padding: 25px; border-radius: 12px; border: 1.5px solid #55efc4; margin-top: 20px;">
                <h4 style="color: #00b894; margin-top: 0;">🎉 JAWABAN REAKSI BERHASIL DIANALISIS!</h4>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                    <tr><td style="width:30%; font-weight:bold;">Tipe Reaksi:</td><td>{res['tipe']}</td></tr>
                    <tr><td style="font-weight:bold;">Nama IUPAC Produk:</td><td style="color:#0984e3; font-weight:bold; font-size:16px;">{res['produk']}</td></tr>
                </table>
                <p><b>Mekanisme Reaksi:</b> {res['penjelasan']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Merender persamaan kimia LaTeX dengan format matematis murni
            induk_rapi = res['induk'].replace("2", "_2").replace("3", "_3").replace("5", "_5").replace("7", "_7")
            reagen_rapi = res['induk'].replace("2", "_2").replace("3", "_3")
            st.latex(rf"\mathrm{{{induk_rapi}}} + \mathrm{{{reagen_rapi}}} \longrightarrow \mathrm{{{res['rumus']}}}")
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
            st.latex(r"\text{C}_6\text{H}_6 \text{ (Benzena)} + \text{CH}_3\text{Cl} \xrightarrow{\text{AlCl}_3} \text{C}_6\text{H}_5\text{CH}_3 \text{ (Toluena)} + \text{HCl}")

        elif "2." in opsi_reaksi:
            st.markdown("""
            <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #0984e3;">
                <h4 style="color: #0984e3; margin-top:0;">🧪 Esterifikasi Fischer (Kondensasi Asam)</h4>
                <p>Kombinasi asam karboksilat dan alkohol di bawah pengaruh asam sulfat pekat untuk menghasilkan ester aromatik buah-buahan.</p>
            </div>
            """, unsafe_allow_html=True)
            st.latex(r"\text{CH}_3\text{COOH} + \text{CH}_3\text{CH}_2\text{OH} \xrightarrow{\text{H}_2\text{SO}_4} \text{CH}_3\text{COOCH}_2\text{CH}_3 \text{ (Etil Asetat)} + \text{H}_2\text{O}")

        elif "3." in opsi_reaksi:
            st.markdown("""
            <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #2ecc71;">
                <h4 style="color: #2ecc71; margin-top:0;">🧪 Hidrogenasi Katalitik (Reaksi Adisi)</h4>
                <p>Reaksi penjenuhan hidrokarbon alifatik dengan menambahkan gas hidrogen pada ikatan rangkap dua alkena.</p>
            </div>
            """, unsafe_allow_html=True)
            st.latex(r"\text{CH}_2\text{=CH}_2 + \text{H}_2 \xrightarrow{\text{Ni, Pt, atau Pd}} \text{CH}_3\text{-CH}_3 \text{ (Etana)}")

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
    # TAB 3: GAME KUIS TATA NAMA
    # ==========================================
    elif menu_pilihan == "📝 Kuis Tata Nama":
        st.markdown("<h3 style='color: #00b894;'>🏆 Tantangan Cerdas: Kuis Tata Nama IUPAC</h3>", unsafe_allow_html=True)
        st.write("Uji pemahaman Anda! Jawab soal satu per satu, dapatkan skor langsung, serta ulasan pembahasan mendalam.")

        DATABASE_SOAL = [
            {
                "pertanyaan": "Apa nama IUPAC alkana rantai lurus dengan struktur CH3-CH2-CH2-CH3?",
                "opsi": ["Propana", "Butana", "Pentana", "Heksana"],
                "jawaban": "Butana",
                "warna_kartu": "#ffeaa7",
                "pembahasan": "CH3-CH2-CH2-CH3 memiliki rantai lurus beranggotakan 4 atom karbon. Berdasarkan aturan deret homolog alkana jenuh, senyawa berkarbon 4 diberi awalan 'but-' dengan akhiran '-ana', sehingga dinamai **Butana**."
            },
            {
                "pertanyaan": "Gugus fungsi aldehid dituliskan secara sistematis sebagai...",
                "opsi": ["-OH", "-CO-", "-CHO", "-COOH"],
                "jawaban": "-CHO",
                "warna_kartu": "#dff9fb",
                "pembahasan": "Gugus fungsi senyawa aldehid (alkanal) dituliskan secara sistematis sebagai **-CHO** (karbonil di ujung rantai). Sebagai tambahan: -OH adalah alkohol, -CO- adalah keton, dan -COOH adalah asam karboksilat."
            },
            {
                "pertanyaan": "Senyawa hidrokarbon tidak jenuh CH3-CH=CH-CH3 diberi nama...",
                "opsi": ["1-Butena", "2-Butena", "Butuna", "Metilpropena"],
                "jawaban": "2-Butena",
                "warna_kartu": "#ffdfdf",
                "pembahasan": "Senyawa CH3-CH=CH-CH3 memiliki ikatan rangkap dua (alkene) yang terletak di antara atom karbon nomor 2 dan 3. Dengan panjang rantai utama 4 karbon, penamaan yang tepat adalah **2-Butena**."
            },
            {
                "pertanyaan": "Nama IUPAC dari senyawa alkohol CH3-CH2-OH adalah...",
                "opsi": ["Metanol", "Etanol", "Propanol", "Gliserol"],
                "jawaban": "Etanol",
                "warna_kartu": "#ebfffa",
                "pembahasan": "Gugus fungsi alkohol (-OH) melekat pada rantai induk dengan 2 atom karbon (Et-). Berdasarkan aturan tata nama IUPAC, senyawa alkohol ini diberi nama resmi **Etanol**."
            },
            {
                "pertanyaan": "Asam cuka (CH3-COOH) memiliki nama IUPAC sistematis berupa...",
                "opsi": ["Asam Metanoat", "Asam Etanoat", "Asam Propanoat", "Asam Asetat"],
                "jawaban": "Asam Etanoat",
                "warna_kartu": "#ffeaa7",
                "pembahasan": "CH3-COOH merupakan asam karboksilat dengan 2 atom karbon. Oleh karena itu, nama IUPAC sistematisnya adalah **Asam Etanoat** (sedangkan Asam Asetat adalah nama trivial/umumnya)."
            },
            {
                "pertanyaan": "Cincin Benzena yang berikatan langsung dengan gugus hidroksil (-OH) disebut...",
                "opsi": ["Toluena", "Anilin", "Fenol", "Asam Benzoat"],
                "jawaban": "Fenol",
                "warna_kartu": "#dff9fb",
                "pembahasan": "Senyawa turunan benzena yang memiliki substituen gugus fungsi alkohol (-OH) pada cincinnya dikenal secara IUPAC dengan nama khusus **Fenol**."
            },
            {
                "pertanyaan": "Jika gugus metil (-CH3) melekat pada cincin benzena, nama senyawa tersebut adalah...",
                "opsi": ["Toluena", "Klorobenzena", "Stirena", "Nitrobenzena"],
                "jawaban": "Toluena",
                "warna_kartu": "#ffdfdf",
                "pembahasan": "Senyawa metilbenzena memiliki nama trivial yang telah diakui dan disahkan oleh IUPAC sebagai nama sistematis resmi, yaitu **Toluena**."
            },
            {
                "pertanyaan": "Apa nama IUPAC untuk struktur eter simetris CH3-O-CH3?",
                "opsi": ["Dimetil Eter", "Metoksimetana", "Etoksimetana", "Metoksietana"],
                "jawaban": "Metoksimetana",
                "warna_kartu": "#ebfffa",
                "pembahasan": "Senyawa eter (alkoksialkana) dengan struktur CH3-O-CH3 terdiri dari gugus alkoksi terkecil (metoksi, CH3-O-) yang terikat pada rantai alkana utama (metana, -CH3). Sehingga nama resminya adalah **Metoksimetana**."
            },
            {
                "pertanyaan": "Senyawa keton terkecil CH3-CO-CH3 (aseton) memiliki nama resmi IUPAC...",
                "opsi": ["Propanal", "Propanon", "Butanon", "Etanon"],
                "jawaban": "Propanon",
                "warna_kartu": "#ffeaa7",
                "pembahasan": "Senyawa keton (alkanon) CH3-CO-CH3 memiliki total 3 atom karbon dengan gugus karbonil di tengah. Sesuai aturan akhiran homolog '-on', nama IUPAC senyawa ini adalah **Propanon**."
            },
            {
                "pertanyaan": "Senyawa ester CH3-COO-CH3 tersusun atas metanol dan asam asetat. Apa nama IUPAC ester tersebut?",
                "opsi": ["Metil Metanoat", "Metil Etanoat", "Etil Metanoat", "Asetil Metilat"],
                "jawaban": "Metil Etanoat",
                "warna_kartu": "#dff9fb",
                "pembahasan": "Senyawa ester (alkil alkanoat) CH3-COO-CH3 memiliki rantai alkil ester berupa metil (-CH3) dan rantai asam alkanoat berupa etanoat (CH3-COO-). Kombinasinya menghasilkan nama IUPAC **Metil Etanoat**."
            }
        ]

        if not st.session_state.kuis_selesai:
            idx = st.session_state.kuis_current_idx
            soal_aktif = DATABASE_SOAL[idx]
            
            st.progress((idx) / len(DATABASE_SOAL))
            
            st.markdown(f"""
            <div style="background-color: {soal_aktif['warna_kartu']}; padding: 22px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                <span style="font-size: 14px; font-weight: bold; color: #636e72;">PERTANYAAN {idx + 1} DARI {len(DATABASE_SOAL)}</span>
                <h4 style="margin: 8px 0 0 0; color: #2d3436; font-size: 18px; font-weight: 700;">{soal_aktif['pertanyaan']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            pilihan_user = st.radio(
                "Pilih Jawaban Anda:",
                soal_aktif['opsi'],
                key=f"kuis_radio_{idx}",
                disabled=st.session_state.kuis_terjawab
            )
            
            col_k_1, col_k_2 = st.columns([1, 4])
            
            with col_k_1:
                if st.button("Analisis ✔", disabled=st.session_state.kuis_terjawab):
                    st.session_state.kuis_terjawab = True
                    if pilihan_user == soal_aktif['jawaban']:
                        st.session_state.kuis_score += 10
                        st.session_state.kuis_jawab_status = "Benar"
                    else:
                        st.session_state.kuis_jawab_status = "Salah"
                    st.rerun()
            
            if st.session_state.kuis_terjawab:
                if st.session_state.kuis_jawab_status == "Benar":
                    st.success("✨ **Jawaban Anda Benar! (+10 Poin)**")
                else:
                    st.error(f"❌ **Jawaban Kurang Tepat.** Jawaban benar: *{soal_aktif['jawaban']}*")
                
                st.markdown(f"""
                <div style="background-color: #f1f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #6c5ce7; margin: 15px 0;">
                    <h5 style="color: #6c5ce7; margin-top: 0; font-weight:bold;">🔍 Pembahasan Jawaban:</h5>
                    <p style="font-size: 14px; color: #2d3436; margin: 0; line-height:1.5;">{soal_aktif['pembahasan']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if idx < len(DATABASE_SOAL) - 1:
                    if st.button("Lanjut ke Soal Berikutnya ⮕"):
                        st.session_state.kuis_current_idx += 1
                        st.session_state.kuis_terjawab = False
                        st.session_state.kuis_jawab_status = None
                        st.rerun()
                else:
                    if st.button("Lihat Hasil Skor Akhir Kuis 🏁"):
                        st.session_state.kuis_selesai = True
                        st.rerun()
                        
        else:
            st.balloons()
            st.markdown(f"""
            <div style="background: white; padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.08); max-width: 600px; margin: 30px auto;">
                <span style="font-size: 60px;">🏆</span>
                <h2 style="color: #2d3436; font-weight: 800; margin-top:10px;">Tantangan Selesai!</h2>
                <p style="font-size: 16px; color: #636e72; margin: 5px 0 20px 0;">Berikut adalah perolehan skor akhir kelompok Anda:</p>
                <div style="background: linear-gradient(135deg, #00b894, #55efc4); padding: 20px; border-radius: 15px; color: white; display: inline-block; margin-bottom: 25px;">
                    <span style="font-size: 45px; font-weight: 900;">{st.session_state.kuis_score}</span> <span style="font-size: 20px; font-weight:700;">/ 100</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Ulangi Kuis dari Awal 🔄"):
                st.session_state.kuis_current_idx = 0
                st.session_state.kuis_score = 0
                st.session_state.kuis_terjawab = False
                st.session_state.kuis_jawab_status = None
                st.session_state.kuis_selesai = False
                st.rerun()

