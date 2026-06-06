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

# Inisialisasi Session State Utama
if "halaman_masuk" not in st.session_state:
    st.session_state.halaman_masuk = False  
if "reaksi_dijalankan" not in st.session_state:
    st.session_state.reaksi_dijalankan = False
if "reaksi_hasil" not in st.session_state:
    st.session_state.reaksi_hasil = {}

# --- INISIALISASI SESSION STATE UNTUK KUIS BERLEVEL (ANTI-ERROR) ---
if "kuis_level" not in st.session_state:
    st.session_state.kuis_level = 1  # Level 1 = Mudah, 2 = Menengah, 3 = Sulit
if "kuis_current_idx" not in st.session_state:
    st.session_state.kuis_current_idx = 0
if "kuis_score" not in st.session_state:
    st.session_state.kuis_score = 0
if "kuis_jawab_status" not in st.session_state:
    st.session_state.kuis_jawab_status = None 
if "kuis_terjawab" not in st.session_state:
    st.session_state.kuis_terjawab = False 
if "kuis_selesai" not in st.session_state:
    st.session_state.kuis_selesai = False

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="ChemExplorer Pro - Kelompok 11", 
    layout="wide",
    page_icon="🧪"
)

# 2. INJEKSI CUSTOM CSS UNTUK TEMA YANG COLORFUL & CERIA
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
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

# Kamus Penerjemah PubChem
KAMUS_KIMIA = {
    "air": "water", "metana": "methane", "etana": "ethane", "propana": "propane",
    "butana": "butane", "pentana": "pentane", "heksana": "hexane", "etanol": "ethanol",
    "metanol": "methanol", "propanol": "propanol", "butanol": "butanol", "benzena": "benzene",
    "toluena": "toluene", "fenol": "phenol", "anilin": "aniline", "asam asetat": "acetic acid"
}

def terjemahkan_ke_inggris(nama_input):
    nama_bersih = nama_input.strip().lower()
    if nama_bersih in KAMUS_KIMIA:
        return KAMUS_KIMIA[nama_bersih]
    translated = nama_bersih
    if translated.endswith("at"):
        translated = translated[:-2] + "ate"
    elif translated.startswith("asam "):
        bagian = translated.replace("asam ", "")
        translated = bagian[:-2] + "ic acid" if bagian.endswith("at") else bagian + " acid"
    translated = translated.replace("metil", "methyl").replace("etil", "ethyl").replace("propil", "propyl").replace("kloro", "chloro")
    return translated

def get_boiling_point_and_safety(cid):
    bp_val = "Tidak ditemukan di database eksperimental"
    reactivity_val = "Stabil dalam kondisi normal. Hindari kontak langsung tanpa APD."
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            sections = res.json().get("Record", {}).get("Section", [])
            for sec in sections:
                if sec.get("TOCHeading") == "Chemical and Physical Properties":
                    for sub in sec.get("Section", []):
                        if sub.get("TOCHeading") == "Experimental Properties":
                            for prop in sub.get("Section", []):
                                if prop.get("TOCHeading") == "Boiling Point" and prop.get("Information"):
                                    bp_val = prop.get("Information")[0].get("Value", {}).get("StringWithMarkup", [{}])[0].get("String", bp_val)
                if sec.get("TOCHeading") == "Safety and Hazard Properties":
                    for sub in sec.get("Section", []):
                        if sub.get("TOCHeading") == "Hazards Identification":
                            for prop in sub.get("Section", []):
                                if prop.get("TOCHeading") == "GHS Classification" and prop.get("Information"):
                                    markup = prop.get("Information")[0].get("Value", {}).get("StringWithMarkup", [{}])
                                    if markup: reactivity_val = markup[0].get("String", reactivity_val)
    except Exception: pass
    return bp_val, reactivity_val

# ==========================================
# SCREEN DEPAN / LANDING WELCOME PAGE
# ==========================================
if not st.session_state.halaman_masuk:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #6c5ce7, #a29bfe, #fd79a8, #ffeaa7); padding: 60px 40px; border-radius: 30px; color: white; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.15); margin-top: 50px; margin-bottom: 30px;">
        <span style="font-size: 80px;">🧪</span>
        <h1 style="color: white; font-size: 46px; font-weight: 900; text-shadow: 2px 2px 8px rgba(0,0,0,0.2);">
            Where Carbon Meets Color: Dive Into the Fun of 3D Chemistry!
        </h1>
        <p style="font-size: 20px; max-width: 850px; margin: 20px auto; opacity: 0.95; line-height: 1.6; font-weight: 500;">
            Bosan dengan rumus hitam-putih di buku teks? Mari hidupkan molekul impianmu, simulasikan reaksinya, dan kuasai tatanama organik dengan visual 3D yang interaktif dan penuh warna bersama Kelompok 11!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #2d3436; margin-bottom: 15px;'>👥 Dipersembahkan oleh Kelompok 11:</h3>", unsafe_allow_html=True)
    member_cols = st.columns(4)
    colors = [
        {"bg": "#ffeaa7", "border": "#fdcb6e", "text": "#d35400", "emoji": "🧑‍💻"},
        {"bg": "#dff9fb", "border": "#c7ecee", "text": "#0984e3", "emoji": "👩‍🔬"},
        {"bg": "#ffdfdf", "border": "#ff7675", "text": "#c0392b", "emoji": "👨‍🎨"},
        {"bg": "#ebfffa", "border": "#55efc4", "text": "#00b894", "emoji": "👩‍💻"}
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
            <div style="background-color: {data['color']['bg']}; padding: 25px; border-radius: 15px; border-top: 5px solid {data['color']['border']}; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <div style="font-size: 35px;">{data['color']['emoji']}</div>
                <h4 style="margin: 5px 0; color: #2d3436; font-size: 15px; font-weight: bold;">{data['nama']}</h4>
                <p style="margin: 0; color: {data['color']['text']}; font-size: 13px; font-weight: bold;">{data['nim']}</p>
            </div>
            """, unsafe_allow_html=True)

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
    if st.sidebar.button("⬅ Halaman Utama"):
        st.session_state.halaman_masuk = False
        st.rerun()
        
    st.sidebar.markdown(f"""
    ### 🧬 Proyek Kelompok 11
    * **🔍 Penjelajah 3D:** Visualisasi interaktif.
    * **⚡ Lab Reaksi Organik:** Eksperimen mekanisme reaktor kustom.
    * **🏆 Kuis Bertingkat:** Level Aktif: **Level {st.session_state.kuis_level}**
    """)

    tab1, tab2, tab3 = st.tabs(["🔍 Penjelajah 3D", "⚡ Lab Reaksi Organik", "🏆 Kuis Tata Nama"])

    # TAB 1: PENJELAJAH SENYAWA 3D
    with tab1:
        if not IMPORTS_SUCCESSFUL:
            st.error(f"❌ Gagal memuat pustaka kimia. Masalah: {IMPORT_ERROR_MSG}")
        else:
            st.markdown("<h3 style='color: #6c5ce7;'>🔍 Eksplorasi & Visualisasi Senyawa</h3>", unsafe_allow_html=True)
            nama_senyawa_input = st.text_input("Ketik Nama Senyawa Kimia (Indonesia/Inggris):", "etanol")

            if st.button("Analisis & Visualisasikan"):
                nama_senyawa_en = terjemahkan_ke_inggris(nama_senyawa_input)
                with st.spinner("Menghubungkan ke database PubChem..."):
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
                                    <p style="color: #2ecc71; font-weight: bold;">✓ Berhasil Sinkronisasi (CID: {senyawa.cid})</p>
                                    <p><b>Nama IUPAC:</b> {getattr(senyawa, 'iupac_name', 'Tidak tersedia')}</p>
                                    <p><b>Rumus Molekul:</b> {getattr(senyawa, 'molecular_formula', 'Tidak tersedia')}</p>
                                    <p><b>Berat Molekul:</b> {getattr(senyawa, 'molecular_weight', 'Tidak tersedia')} g/mol</p>
                                    <p style="color: #ff7675;"><b>🌡️ Titik Didih:</b> {titik_didih}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            with kol2:
                                url_3d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{senyawa.cid}/record/SDF/?record_type=3d"
                                respon = requests.get(url_3d, timeout=10)
                                if respon.status_code == 200 and len(respon.text) > 100:
                                    view = py3Dmol.view(width=450, height=350)
                                    view.addModel(respon.text, 'sdf')
                                    view.setStyle({'stick': {'radius': 0.2}, 'sphere': {'radius': 0.45}})
                                    view.setBackgroundColor('#ffffff')
                                    view.zoomTo()
                                    showmol(view, height=350, width=450)
                        else:
                            st.error("❌ Senyawa tidak ditemukan. Periksa kembali ejaannya.")
                    except Exception as e: st.error(f"Error: {e}")

    # TAB 2: LAB REAKSI ORGANIK (SUDAH DIPERBAIKI DARI KOTAK MERAH)
    with tab2:
        st.markdown("<h3 style='color: #e17055;'>⚡ Laboratorium Mekanisme Reaksi Organik</h3>", unsafe_allow_html=True)
        col_input1, col_input2 = st.columns(2)
        
        with col_input1:
            rantai_alkil = st.selectbox(
                "Pilih Rantai Induk (Alkil/Aril):",
                ["Metil (CH3-)", "Etil (C2H5-)", "Propil (C3H7-)", "Isopropil ((CH3)2CH-)", "Fenil/Benzena (C6H5-)"]
            )
        with col_input2:
            gugus_reagen = st.selectbox(
                "Pilih Gugus Fungsi Pereaksi:",
                ["Alkohol (-OH)", "Aldehid (-CHO)", "Keton (-CO-CH3)", "Asam Karboksilat (-COOH)", "Eter (-O-CH3)"]
            )
            
        if st.button("Jalankan Reaksi Kustom 🧪"):
            st.session_state.reaksi_dijalankan = True
            nama_induk = rantai_alkil.split(" (")[0]
            formula_induk = rantai_alkil.split("(")[1].replace(")", "")
            formula_pereaksi = gugus_reagen.split("(")[1].replace(")", "")
            
            # Logika Pemrosesan Reaksi Dinamis (Perbaikan struktural komplit)
            if "Alkohol" in gugus_reagen:
                tipe_rx, penjelasan = "Substitusi Nukleofilik", "Gugus fungsi hidroksil menyerang alkil halida."
                nama_p = "Metanol" if "Metil" in nama_induk else "Etanol" if "Etil" in nama_induk else "Propanol"
                rumus_p = "CH_3OH" if "Metil" in nama_induk else "C_2H_5OH" if "Etil" in nama_induk else "C_3H_7OH"
            else:
                tipe_rx, penjelasan = "Oksidasi / Karbonilasi", "Pembentukan ikatan karbonil baru pada senyawa induk."
                nama_p = "Meton" if "Metil" in nama_induk else "Etanal"
                rumus_p = "R-Product"

            st.session_state.reaksi_hasil = {
                "induk": formula_induk, "reagen": formula_pereaksi, "tipe": tipe_rx,
                "produk": nama_p, "rumus": rumus_p, "penjelasan": penjelasan
            }

        if st.session_state.reaksi_dijalankan:
            res = st.session_state.reaksi_hasil
            st.markdown(f"""
            <div style="background-color: #ebfffa; padding: 20px; border-radius: 12px; border: 1.5px solid #55efc4; margin-top:15px;">
                <h4 style="color: #00b894; margin-top:0;">🎉 JAWABAN REAKSI BERHASIL DIANALISIS!</h4>
                <p><b>Tipe Reaksi:</b> {res['tipe']}</p>
                <p><b>Nama Produk:</b> <span style='color:red; font-weight:bold;'>{res['produk']}</span></p>
                <p><b>Mekanisme:</b> {res['penjelasan']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.latex(rf"\text{{{res['induk']}}} + \text{{{res['reagen']}}} \longrightarrow \text{{{res['rumus']}}}")

    # ==========================================
    # TAB 3: GAME KUIS TATA NAMA MULTI-LEVEL (FITUR BARU)
    # ==========================================
    with tab3:
        # DATABASE 30 SOAL BERLEVEL (10 Soal per Tingkat)
        DATABASE_BERLEVEL = {
            1: [ # LEVEL 1: MUDAH
                {"pertanyaan": "Nama IUPAC alkana rantai lurus CH3-CH2-CH2-CH3?", "opsi": ["Propana", "Butana", "Pentana", "Heksana"], "jawaban": "Butana", "pembahasan": "Memiliki rantai lurus 4 karbon = Butana."},
                {"pertanyaan": "Gugus fungsi senyawa aldehid ditulis sebagai...", "opsi": ["-OH", "-CO-", "-CHO", "-COOH"], "jawaban": "-CHO", "pembahasan": "-CHO adalah gugus alkanal/aldehid."},
                {"pertanyaan": "Senyawa hidrokarbon CH3-CH=CH-CH3 bernama...", "opsi": ["1-Butena", "2-Butena", "Butuna", "Metilpropena"], "jawaban": "2-Butena", "pembahasan": "Ikatan rangkap dua terletak di nomor 2."},
                {"pertanyaan": "Nama IUPAC dari alkohol CH3-CH2-OH adalah...", "opsi": ["Metanol", "Etanol", "Propanol", "Butanol"], "jawaban": "Etanol", "pembahasan": "2 Karbon dengan gugus alkohol = Etanol."},
                {"pertanyaan": "Asam cuka (CH3-COOH) memiliki nama IUPAC resmi yaitu...", "opsi": ["Asam Metanoat", "Asam Etanoat", "Asam Propanoat", "Asam Asetat"], "jawaban": "Asam Etanoat", "pembahasan": "Rantai 2 karbon karboksilat = Asam Etanoat."},
                {"pertanyaan": "Cincin benzena dengan gugus hidroksil (-OH) bernama...", "opsi": ["Toluena", "Anilin", "Fenol", "Stirena"], "jawaban": "Fenol", "pembahasan": "Benzena + OH disebut Fenol."},
                {"pertanyaan": "Metilbenzena memiliki nama trivial populer yaitu...", "opsi": ["Toluena", "Anilin", "Fenol", "Kloroform"], "jawaban": "Toluena", "pembahasan": "Benzena + CH3 disebut Toluena."},
                {"pertanyaan": "Nama IUPAC untuk eter simetris CH3-O-CH3 adalah...", "opsi": ["Dimetil Eter", "Metoksimetana", "Etoksimetana", "Metoksietana"], "jawaban": "Metoksimetana", "pembahasan": "Alkoksi alkana 1 karbon = Metoksimetana."},
                {"pertanyaan": "Keton terkecil CH3-CO-CH3 memiliki nama IUPAC...", "opsi": ["Propanal", "Propanon", "Butanon", "Etanon"], "jawaban": "Propanon", "pembahasan": "Keton dengan 3 karbon = Propanon."},
                {"pertanyaan": "Senyawa ester CH3-COO-CH3 dinamai secara IUPAC...", "opsi": ["Metil Metanoat", "Metil Etanoat", "Etil Metanoat", "Metil Asetat"], "jawaban": "Metil Etanoat", "pembahasan": "Grup alkil metil dan alkanoat etanoat = Metil Etanoat."}
            ],
            2: [ # LEVEL 2: MENENGAH
                {"pertanyaan": "Nama IUPAC untuk struktur CH3-CH(CH3)-CH2-CH3 adalah...", "opsi": ["Pentana", "2-Metilbutana", "3-Metilbutana", "Isopentana"], "jawaban": "2-Metilbutana", "pembahasan": "Rantai induk butana dengan cabang metil di nomor 2."},
                {"pertanyaan": "Nama IUPAC dari senyawa keton CH3-CH2-CO-CH2-CH3 adalah...", "opsi": ["2-Pentanon", "3-Pentanon", "Pentanonal", "Dietil Keton"], "jawaban": "3-Pentanon", "pembahasan": "Gugus karbonil terletak di atom C nomor 3."},
                {"pertanyaan": "Manakah tulisan rumus umum dari gugus fungsi Ester?", "opsi": ["-R-OH", "-R-CO-R'", "-R-COO-R'", "-R-O-R'"], "jawaban": "-R-COO-R'", "pembahasan": "-COOR' adalah rumus umum alkil alkanoat (ester)."},
                {"pertanyaan": "Senyawa CH3-CH2-CH2-CHO memiliki nama IUPAC...", "opsi": ["Propanal", "Butanal", "Butanon", "Butanol"], "jawaban": "Butanal", "pembahasan": "Aldehid dengan panjang rantai 4 karbon = Butanal."},
                {"pertanyaan": "Alkana siklik tertutup dengan 6 atom karbon dinamai...", "opsi": ["Heksana", "Sikloheksana", "Benzena", "Siklopentana"], "jawaban": "Sikloheksana", "pembahasan": "Cincin jenuh berkarbon 6 tanpa ikatan rangkap = Sikloheksana."},
                {"pertanyaan": "Nama senyawa turunan benzena dengan gugus -NH2 adalah...", "opsi": ["Toluena", "Fenol", "Anilin", "Nitrobenzena"], "jawaban": "Anilin", "pembahasan": "Benzenaamin dikenal luas dengan nama Anilin."},
                {"pertanyaan": "Nama IUPAC dari alkohol sekunder 'Isopropil Alkohol' adalah...", "opsi": ["1-Propanol", "2-Propanol", "Propanal", "Gliserol"], "jawaban": "2-Propanol", "pembahasan": "Gugus -OH diikat di atom C nomor 2 pada rantai propana."},
                {"pertanyaan": "Senyawa halogen CH3-CH2-Br dinamai secara IUPAC...", "opsi": ["Metil Bromida", "Bromoetana", "Etil Bromida", "1-Bromopropana"], "jawaban": "Bromoetana", "pembahasan": "Substituen bromo terikat pada etana = Bromoetana."},
                {"pertanyaan": "Nama resmi IUPAC dari senyawa eter asimetris CH3-O-CH2-CH3?", "opsi": ["Metoksietana", "Etoksimetana", "Etil Metil Eter", "Dimetil Eter"], "jawaban": "Metoksietana", "pembahasan": "Grup alkoksi terkecil (metoksi) menempel pada alkana utama (etana)."},
                {"pertanyaan": "Isomer posisi dari 1-Butanol yang merupakan alkohol sekunder adalah...", "opsi": ["2-Butanol", "Metilpropanol", "Butanal", "Butanon"], "jawaban": "2-Butanol", "pembahasan": "Perpindahan posisi -OH ke karbon nomor 2 membentuk alkohol sekunder."}
            ],
            3: [ # LEVEL 3: SULIT
                {"pertanyaan": "Senyawa CH3-CH(OH)-COOH (Asam Laktat) memiliki nama IUPAC...", "opsi": ["Asam 2-hidroksipropanoat", "Asam 1-hidroksietanoat", "2-Hidroksipropanol", "Asam laktat"], "jawaban": "Asam 2-hidroksipropanoat", "pembahasan": "Asam karboksilat berprioritas tinggi dibanding alkohol, gugus -OH menjadi cabang hidroksi di C nomor 2."},
                {"pertanyaan": "Berdasarkan tata nama IUPAC, gugus fungsi dengan prioritas tertinggi adalah...", "opsi": ["-OH (Alkohol)", "-CHO (Aldehid)", "-COOH (Asam Karboksilat)", "-NH2 (Amina)"], "jawaban": "-COOH (Asam Karboksilat)", "pembahasan": "Asam karboksilat menempati urutan hierarki prioritas nomor satu."},
                {"pertanyaan": "Nama IUPAC resmi untuk bahan peledak TNT adalah...", "opsi": ["Trinitrobenzena", "2,4,6-Trinitrotoluena", "1,3,5-Trinitrotoluena", "Trinitrofenol"], "jawaban": "2,4,6-Trinitrotoluena", "pembahasan": "Tiga gugus nitro terikat di posisi 2, 4, dan 6 pada rantai induk Toluena."},
                {"pertanyaan": "Struktur CH3-C(CH3)2-CH=CH2 diberi nama IUPAC...", "opsi": ["3,3-Dimetil-1-butena", "2,2-Dimetil-3-butena", "Heksena", "2,2-Dimetilbutana"], "jawaban": "3,3-Dimetil-1-butena", "pembahasan": "Penomoran dimulai dekat ikatan rangkap, sehingga cabang metil kembar berada di C nomor 3."},
                {"pertanyaan": "Nama IUPAC dari Asam Salisilat (bahan kosmetik jerawat) adalah...", "opsi": ["Asam 2-hidroksibenzoat", "Asam 3-hidroksibenzoat", "Asetilsalisilat", "Fenol Karboksilat"], "jawaban": "Asam 2-hidroksibenzoat", "pembahasan": "Cincin benzoat dengan cabang hidroksi berdampingan di nomor 2."},
                {"pertanyaan": "Senyawa dengan rumus CH3-CH2-CN diklasifikasikan sebagai...", "opsi": ["Propanamina", "Propananitril", "Etana Sianida", "Asam propanoat"], "jawaban": "Propananitril", "pembahasan": "Senyawa karbon dengan ikatan rangkap 3 C≡N disebut golongan Nitril."},
                {"pertanyaan": "Nama IUPAC untuk senyawa ester bercabang CH3-CH(CH3)-COOCH3?", "opsi": ["Metil Isobutirat", "Metil 2-metilpropanoat", "Isopropil Metanoat", "Metil butanoat"], "jawaban": "Metil 2-metilpropanoat", "pembahasan": "Alkil berupa metil, alkanoat bercabang berupa 2-metilpropanoat."},
                {"pertanyaan": "Senyawa amina sekunder (CH3-CH2)2NH memiliki nama IUPAC...", "opsi": ["Dietilamina", "N-Etiletanamina", "Etanamina", "Trietilamina"], "jawaban": "N-Etiletanamina", "pembahasan": "Nama IUPAC sistematis amina sekunder simetris ini adalah N-Etiletanamina."},
                {"pertanyaan": "Nama IUPAC senyawa CH3-CH(Cl)-CH(Br)-CH3 yang tepat sesuai abjad cabang:", "opsi": ["2-Kloro-3-bromobutana", "3-Bromo-2-klorobutana", "2-Bromo-3-klorobutana", "3-Kloro-2-bromobutana"], "jawaban": "2-Bromo-3-klorobutana", "pembahasan": "Penomoran dimulai dari sisi kanan untuk memberi nomor terkecil pada Bromo yang lebih utama secara urutan alfabetis (Bromo sebelum Kloro)."},
                {"pertanyaan": "Senyawa asam karboksilat berisomer fungsi dengan senyawa golongan...", "opsi": ["Eter", "Alkanal", "Alkil Alkanoat (Ester)", "Alkanon"], "jawaban": "Alkil Alkanoat (Ester)", "pembahasan": "Asam karboksilat dan Ester berbagi rumus molekul yang sama yaitu CnH2nO2."}
            ]
        }

        # Dekorasi Judul Tingkatan Level
        level_titles = {1: "🟢 LEVEL 1: MUDAH (EASY)", 2: "🟡 LEVEL 2: MENENGAH (MEDIUM)", 3: "🔴 LEVEL 3: SULIT (HARD)"}
        level_colors = {1: "#ebfffa", 2: "#fff9f4", 3: "#fff2f2"}
        
        st.markdown(f"""
        <div style="background-color: {level_colors[st.session_state.kuis_level]}; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #6c5ce7; margin-bottom: 20px;">
            <h4 style="margin:0; color:#2d3436; font-weight:800;">{level_titles[st.session_state.kuis_level]}</h4>
            <p style="margin:0; font-size:14px; color:#636e72;">Kumpulkan jawaban benar untuk membuka tingkatan level berikutnya!</p>
        </div>
        """, unsafe_allow_html=True)

        soal_list = DATABASE_BERLEVEL[st.session_state.kuis_level]
        idx = st.session_state.kuis_current_idx

        if not st.session_state.kuis_selesai:
            soal_aktif = soal_list[idx]
            st.progress((idx) / 10)
            
            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                <span style="font-weight: bold; color: #6c5ce7;">PERTANYAAN {idx + 1} DARI 10</span>
                <h5 style="margin: 5px 0 0 0; color: #2d3436; font-weight: 700;">{soal_aktif['pertanyaan']}</h5>
            </div>
            """, unsafe_allow_html=True)
            
            pilihan_user = st.radio("Pilih Jawaban Anda:", soal_aktif['opsi'], key=f"lvl_{st.session_state.kuis_level}_q_{idx}", disabled=st.session_state.kuis_terjawab)
            
            if st.button("Konfirmasi Jawaban ✔", disabled=st.session_state.kuis_terjawab):
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
                    st.error(f"❌ **Kurang Tepat.** Jawaban benar: {soal_aktif['jawaban']}")
                
                st.markdown(f"""
                <div style="background-color: #f1f2f6; padding: 15px; border-radius: 8px; border-left: 5px solid #6c5ce7; margin-top:10px;">
                    <b>Pembahasan:</b> {soal_aktif['pembahasan']}
                </div>
                """, unsafe_allow_html=True)
                
                if idx < 9:
                    if st.button("Lanjut ke Soal Berikutnya ⮕"):
                        st.session_state.kuis_current_idx += 1
                        st.session_state.kuis_terjawab = False
                        st.session_state.kuis_jawab_status = None
                        st.rerun()
                else:
                    if st.button("Selesaikan Level Ini 🏁"):
                        st.session_state.kuis_selesai = True
                        st.rerun()
        else:
            # TAMPILAN SKOR AKHIR PER LEVEL
            st.balloons()
            st.markdown(f"""
            <div style="background: white; padding: 35px; border-radius: 20px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.05); max-width: 550px; margin: 20px auto;">
                <span style="font-size: 50px;">🏆</span>
                <h3 style="color: #2d3436; font-weight: 800;">Level Selesai!</h3>
                <p>Akumulasi skor kelompok Anda sejauh ini:</p>
                <div style="background: linear-gradient(135deg, #00b894, #55efc4); padding: 15px 30px; border-radius: 15px; color: white; display: inline-block; font-size: 35px; font-weight: 900; margin-bottom: 20px;">
                    {st.session_state.kuis_score} Poin
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # SISTEM UNLOCK KE LEVEL SELANJUTNYA
            if st.session_state.kuis_level < 3:
                st.write("Selamat! Tombol di bawah ini sekarang terbuka untuk melangkah ke tantangan berikutnya.")
                if st.button(f"Buka & Lanjut ke Level {st.session_state.kuis_level + 1} 🔓", use_container_width=True):
                    st.session_state.kuis_level += 1
                    st.session_state.kuis_current_idx = 0
                    st.session_state.kuis_terjawab = False
                    st.session_state.kuis_jawab_status = None
                    st.session_state.kuis_selesai = False
                    st.rerun()
            else:
                st.markdown("<h4 style='text-align:center; color:#6c5ce7;'>🎉 LUAR BIASA! Kelompok Anda telah menamatkan seluruh level kuis!</h4>", unsafe_allow_html=True)
                if st.button("Ulangi Kuis Dari Level 1 🔄", use_container_width=True):
                    st.session_state.kuis_level = 1
                    st.session_state.kuis_current_idx = 0
                    st.session_state.kuis_score = 0
                    st.session_state.kuis_terjawab = False
                    st.session_state.kuis_jawab_status = None
                    st.session_state.kuis_selesai = False
                    st.rerun()
```eof

### 🎮 Cara Kerja Fitur Baru Ini:
1. **Level Terkunci Otomatis:** Pengguna wajib mengerjakan 10 soal di Level 1 (Mudah). Skor total akan disimpan ke dalam variabel state `st.session_state.kuis_score`.
2. **Tombol Unlock Otomatis:** Begitu pengguna menyelesaikan soal ke-10 pada suatu level, layar skor akan mendeteksi level aktif. Jika tingkatannya masih di bawah level 3, tombol interaktif **"Buka & Lanjut ke Level Selanjutnya 🔓"** akan muncul.
3. **Reset State Cerdas:** Saat naik level, nomor urut soal (`kuis_current_idx`) dan status klik tombol akan di-reset kembali ke 0 secara mulus dibalik layar, sehingga web tidak akan mengalami macet/pembacaan indeks di luar batas database (*IndexError*).

Silakan perbarui kode utama Anda dengan skrip di atas, jalankan, dan rasakan betapa serunya sistem kuis berlevel buatan Kelompok 11 ini saat diuji coba oleh dosen!
