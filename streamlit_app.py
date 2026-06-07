Deeimport streamlit as st
import requests

# ==============================================================================
# 🛡️ 1. JARING PENGAMAN IMPORT & KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(page_title="Sains Organik Kelompok 11", page_icon="🧪", layout="wide")

try:
    import pubchempy as pcp
    from stmol import showmol
    import py3Dmol
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    IMPORTS_SUCCESSFUL = False
    IMPORT_ERROR_MSG = str(e)

# Inisialisasi Session State agar data interaksi tetap terjaga
if "halaman_masuk" not in st.session_state:
    st.session_state.halaman_masuk = False

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

if "quiz_terjawab" not in st.session_state:
    st.session_state.quiz_terjawab = False

# ==============================================================================
# 🎨 2. HALAMAN MASUK (LANDING PAGE - SENSASI BELAJAR MENARIK)
# ==============================================================================
if not st.session_state.halaman_masuk:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 50px; border-radius: 20px; text-align: center; color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
        <h1 style="font-size: 45px; font-weight: bold; margin-bottom: 10px;">🧪 SELAMAT DATANG DI DUNIA SENYAWA ORGANIK</h1>
        <p style="font-size: 18px; opacity: 0.9; margin-bottom: 30px;">Rasakan sensasi belajar kimia yang interaktif, dinamis, dan visualisasi 3D yang memukau bersama Kelompok 11!</p>
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; display: inline-block; text-align: left; margin-bottom: 30px;">
            <p style="margin: 5px 0;">🔬 <b>Penjelajah 3D:</b> Lihat struktur molekul nyata secara langsung.</p>
            <p style="margin: 5px 0;">🎛️ <b>Reaktor Kustom:</b> Prediksi otomatis hasil reaksi alkil & gugus fungsi.</p>
            <p style="margin: 5px 0;">🎯 <b>Kuis Interaktif:</b> Uji pemahaman Anda dengan pembahasan instan.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    col_center1, col_center2, col_center3 = st.columns([2, 1, 2])
    with col_center2:
        if st.button("🚀 Klik untuk Masuk ke Aplikasi", use_container_width=True):
            st.session_state.halaman_masuk = True
            st.rerun()

# ==============================================================================
# 💻 3. DASHBOARD UTAMA APLIKASI (SETELAH KLIK MASUK)
# ==============================================================================
else:
    # Tombol Kembali ke Landing Page di Sidebar
    if st.sidebar.button("⬅️ Keluar / Menu Utama"):
        st.session_state.halaman_masuk = False
        st.rerun()
        
    st.sidebar.markdown("### 🧬 Navigasi Fitur")
    tab1, tab2, tab3 = st.tabs(["🔍 Penjelajah 3D", "🧪 Reaktor Kustom Dinamis", "📝 Kuis Interaktif"])

    # --------------------------------------------------------------------------
    # TAB 1: PENJELAJAH 3D (MENDUKUNG BAHASA INDONESIA)
    # --------------------------------------------------------------------------
    with tab1:
        st.header("🔍 Penjelajah Struktur Molekul 3D")
        st.write("Ketik nama senyawa kimia organik (Bisa menggunakan Bahasa Indonesia atau Inggris).")
        
        # Kamus terjemahan otomatis nama Indonesia ke Inggris untuk PubChem
        kamus_kimia = {
            "air": "water", "metana": "methane", "etana": "ethane", "propana": "propane",
            "butana": "butane", "metanol": "methanol", "etanol": "ethanol", "propanol": "propanol",
            "aseton": "acetone", "glukosa": "glucose", "asam asetat": "acetic acid",
            "benzena": "benzene", "klorobenzena": "chlorobenzene", "metil klorida": "methyl chloride",
            "asam format": "formic acid", "formaldehid": "formaldehyde", "fenol": "phenol"
        }
        
        nama_input = st.text_input("Masukkan Nama Senyawa Kimia:", value="Metanol")
        nama_proses = nama_input.lower().strip()
        
        # Cari di kamus, jika ada gunakan versi Inggrisnya
        nama_final = kamus_kimia.get(nama_proses, nama_input)
        
        if IMPORTS_SUCCESSFUL:
            if nama_input:
                try:
                    compounds = pcp.get_compounds(nama_final, 'name')
                    if compounds:
                        cid = compounds[0].cid
                        st.success(f"Senyawa ditemukan! Nama Sistem: {compounds[0].iupac_name} (CID: {cid})")
                        
                        # Render 3D Mol View
                        xyz_view = py3Dmol.view(query=f'cid:{cid}', options={'doNotRender':False})
                        xyz_view.setStyle({'stick':{}})
                        xyz_view.setBackgroundColor('#f9f9f9')
                        showmol(xyz_view, height=400, width=700)
                    else:
                        st.error("Senyawa tidak ditemukan di database. Coba periksa ejaan Anda.")
                except Exception as ex:
                    st.warning("Gagal memuat visualisasi 3D. Pastikan koneksi internet stabil.")
        else:
            st.error(f"Fitur 3D dinonaktifkan karena library gagal dimuat: {IMPORT_ERROR_MSG}")

    # --------------------------------------------------------------------------
    # TAB 2: REAKTOR KUSTOM DINAMIS (ANTI-ERROR & 40 KOMBINASI LENGKAP)
    # --------------------------------------------------------------------------
    with tab2:
        st.header("🧪 Reaktor Kustom Kimia Organik")
        st.write("Tentukan senyawa alkil (rantai induk) Anda, lalu reaksikan dengan berbagai reagen pilihan di bawah ini:")

        # 1. Dropdown Rantai Induk Lengkap
        rantai_alkil = st.selectbox(
            "Pilih Rantai Induk (Alkil/Aril):", 
            ["Metil (CH3-)", "Etil (C2H5-)", "Propil (C3H7-)", "Isopropil ((CH3)2CH-)", "Fenil/Benzena (C6H5-)"]
        )

        # 2. Dropdown Gugus Fungsi Lengkap
        gugus_reagen = st.selectbox(
            "Pilih Gugus Fungsi Pereaksi:", 
            [
                "Alkohol (-OH)", "Aldehid (-CHO)", "Keton (-CO-CH3)", 
                "Asam Karboksilat (-COOH)", "Eter (-O-CH3)", "Ester (-COOCH3)",          
                "Halogen / Klorida (-Cl)", "Halogen / Bromida (-Br)"    
            ]
        )

        # 3. Klasifikasi Struktur untuk Variabel LaTeX Dinamis
        if "Metil" in rantai_alkil:
            key_alkil, f_alkil = "Metil", r"\text{CH}_3"
        elif "Etil" in rantai_alkil:
            key_alkil, f_alkil = "Etil", r"\text{C}_2\text{H}_5"
        elif "Propil" in rantai_alkil:
            key_alkil, f_alkil = "Propil", r"\text{C}_3\text{H}_7"
        elif "Isopropil" in rantai_alkil:
            key_alkil, f_alkil = "Isopropil", r"\text{(CH}_3\text{)}_2\text{CH}"
        else:
            key_alkil, f_alkil = "Fenil", r"\text{C}_6\text{H}_5"

        # 4. Matriks Data Nama Produk Akurat (5 Rantai x 8 Gugus Fungsi)
        nama_produk_matrix = {
            "Alkohol (-OH)": {
                "Metil": "Metanol", "Etil": "Etanol", "Propil": "1-Propanol", "Isopropil": "2-Propanol", "Fenil": "Fenol"
            },
            "Halogen / Klorida (-Cl)": {
                "Metil": "Metil Klorida (Klorometana)", "Etil": "Etil Klorida (Kloroetana)", "Propil": "Propil Klorida", "Isopropil": "Isopropil Klorida", "Fenil": "Klorobenzena"
            },
            "Halogen / Bromida (-Br)": {
                "Metil": "Metil Bromida (Bromometana)", "Etil": "Etil Bromida (Bromoetana)", "Propil": "Propil Bromida", "Isopropil": "Isopropil Bromida", "Fenil": "Bromobenzena"
            },
            "Aldehid (-CHO)": {
                "Metil": "Metanal (Formaldehid)", "Etil": "Etanal (Asetaldehid)", "Propil": "Propanal", "Isopropil": "2-Metilpropanal", "Fenil": "Benzaldehid"
            },
            "Keton (-CO-CH3)": {
                "Metil": "Propanon (Aseton)", "Etil": "Butanon", "Propil": "2-Pentanon", "Isopropil": "3-Metil-2-butanon", "Fenil": "Asetofenon"
            },
            "Asam Karboksilat (-COOH)": {
                "Metil": "Asam Metanoat", "Etil": "Asam Etanoat (Asetat)", "Propil": "Asam Propanoat", "Isopropil": "Asam Isobutanoat", "Fenil": "Asam Benzoat"
            },
            "Eter (-O-CH3)": {
                "Metil": "Metoksi Metana", "Etil": "Metoksi Etana", "Propil": "Metoksi Propana", "Isopropil": "Metoksi Isopropana", "Fenil": "Metoksibenzena (Anisol)"
            },
            "Ester (-COOCH3)": {
                "Metil": "Metil Metanoat", "Etil": "Metil Etanoat", "Propil": "Metil Propanoat", "Isopropil": "Metil Isobutanoat", "Fenil": "Metil Benzoat"
            }
        }

        # 5. Eksekusi Tombol Analisis Reaksi
        if st.button("Jalankan Reaksi Kustom 🧪"):
            nama_p = nama_produk_matrix[gugus_reagen][key_alkil]
            
            # Logika Kimia Dinamis & Pemetaan Rumus LaTeX Sesuai Pilihan Dropdown
            if "Alkohol" in gugus_reagen:
                tipe_rx = "Substitusi Nukleofilik (Pembentukan Alkohol)"
                penjelasan = f"Gugus fungsi halida pada {key_alkil} diserang oleh nukleofil hidroksida (OH⁻) menghasilkan senyawa {nama_p}."
                rumus_latex = f"{f_alkil}\\text{{-X}} + \\text{{OH}}^- \\longrightarrow {f_alkil}\\text{{OH}} + \\text{{X}}^-"
                
            elif "Klorida" in gugus_reagen or "Bromida" in gugus_reagen:
                halogen_name = "Klorida (Cl2)" if "Klorida" in gugus_reagen else "Bromida (Br2)"
                halogen_sym = "Cl" if "Klorida" in gugus_reagen else "Br"
                tipe_rx = "Halogenasi Radikal Bebas / Substitusi"
                penjelasan = f"Substitusi radikal bebas hidrokarbon {key_alkil} dengan gas {halogen_name} di bawah paparan panas/cahaya menghasilkan {nama_p}."
                rumus_latex = f"{f_alkil}\\text{{-H}} + \\text{{{halogen_sym}}}_2 \\longrightarrow {f_alkil}\\text{{{halogen_sym}}} + \\text{{H}}{halogen_sym}"
                
            elif "Aldehid" in gugus_reagen:
                tipe_rx = "Oksidasi Alkohol Primer"
                penjelasan = f"Oksidasi parsial terkontrol alkohol primer pada rantai {key_alkil} menggunakan agen pengoksidasi menghasilkan {nama_p}."
                rumus_latex = f"{f_alkil}\\text{{-CH}}_2\\text{{OH}} \\xrightarrow{{\\text{{[O]}}}} {f_alkil}\\text{{-CHO}}"
                
            elif "Keton" in gugus_reagen:
                tipe_rx = "Oksidasi Alkohol Sekunder"
                penjelasan = f"Oksidasi alkohol sekunder atau modifikasi rantai samping menghasilkan gugus karbonil keton berupa {nama_p}."
                rumus_latex = f"{f_alkil}\\text{{-CO-CH}}_3"
                
            elif "Asam Karboksilat" in gugus_reagen:
                tipe_rx = "Oksidasi Penuh Hidrokarbon Primer"
                penjelasan = f"Oksidasi menyeluruh alkohol primer atau alkil benzena menggunakan oksidator kuat menghasilkan senyawa {nama_p}."
                rumus_latex = f"{f_alkil}\\text{{-COOH}}"
                
            elif "Eter" in gugus_reagen:
                tipe_rx = "Sintesis Eter Williamson"
                penjelasan = f"Reaksi antara ion alkoksida rantai {key_alkil} dengan metil halida primer membentuk jembatan eter menghasilkan {nama_p}."
                rumus_latex = f"{f_alkil}\\text{{-O}}^- + \\text{{CH}}_3\\text{{-X}} \\longrightarrow {f_alkil}\\text{{-O-CH}}_3 + \\text{{X}}^-"
                
            else:
                tipe_rx = "Esterifikasi Fischer"
                penjelasan = f"Kondensasi asam karboksilat berbasis rantai {key_alkil} dengan metanol membentuk ikatan senyawa ester berupa {nama_p}."
                rumus_latex = f"{f_alkil}\\text{{-COOH}} + \\text{{CH}}_3\\text{{OH}} \\longrightarrow {f_alkil}\\text{{-COOCH}}_3 + \\text{{H}}_2\\text{{O}}"

            # Render HTML Box (Warna Hijau Toska)
            st.markdown(f"""
            <div style="background-color: #ebfffa; padding: 22px; border-radius: 12px; border: 1px solid #00b894; margin-top: 20px;">
                <h4 style="color: #00b894; margin-top: 0; font-weight: bold;">🧬 JAWABAN REAKSI BERHASIL DIANALISIS!</h4>
                <table style="width:100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #dfe6e9;">
                        <td style="padding: 10px 8px; font-weight: bold; width: 30%; color: #2d3436;">Tipe Reaksi:</td>
                        <td style="padding: 10px 8px; color: #2d3436;">{tipe_rx}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 8px; font-weight: bold; color: #2d3436;">Nama IUPAC Produk:</td>
                        <td style="padding: 10px 8px; color: #d63031; font-weight: bold;">{nama_p}</td>
                    </tr>
                </table>
                <p style="margin-top: 15px; font-size: 14px; color: #2d3436; line-height: 1.5;">
                    <b>Mekanisme Reaksi:</b> {penjelasan}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan Rumus Struktur Kimia LaTeX Akademik Bawaan Streamlit
            st.latex(rumus_latex)

        # Pembatas Garis Putus-Putus Aman dari Indentasi
        st.markdown("<hr style='border: 0.5px dashed #b2bec3; margin: 30px 0;'>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 3: KUIS INTERAKTIF (PER NOMOR + TOMBOL PEMBAHASAN)
    # --------------------------------------------------------------------------
    with tab3:
        st.header("📝 Kuis Interaktif Senyawa Organik")
        
        # Bank Soal & Pembahasan
        daftar_soal = [
            {
                "soal": "Apakah nama IUPAC dari senyawa alkohol yang memiliki rantai induk Metil?",
                "pilihan": ["Etanol", "Metanol", "Propanol", "Butanol"],
                "jawaban": "Metanol",
                "pembahasan": "Metil memiliki 1 atom karbon ($C_1$). Golongan alkohol dengan 1 atom karbon dinamakan Metanol."
            },
            {
                "soal": "Reaksi substitusi alkana dengan gas klorida ($Cl_2$) bantuan sinar UV disebut reaksi...",
                "pilihan": ["Esterifikasi", "Oksidasi", "Halogenasi Radikal Bebas", "Hidrolisis"],
                "jawaban": "Halogenasi Radikal Bebas",
                "pembahasan": "Gas halogen ($Cl_2, Br_2$) yang menyerang ikatan hidrokarbon jenuh di bawah sinar UV membentuk radikal bebas bernama reaksi Halogenasi."
            },
            {
                "soal": "Senyawa organik dengan gugus fungsi '-CHO' termasuk kedalam golongan...",
                "pilihan": ["Keton", "Eter", "Ester", "Aldehid"],
                "jawaban": "Aldehid",
                "pembahasan": "Gugus fungsi karbonil terminal '-CHO' merupakan ciri khas utama dari golongan senyawa Aldehid (Alkanal)."
            }
        ]
        
        id_sekarang = st.session_state.quiz_index
        
        if id_sekarang < len(daftar_soal):
            soal_aktif = daftar_soal[id_sekarang]
            
            st.markdown(f"#### **Soal No. {id_sekarang + 1} dari {len(daftar_soal)}**")
            st.write(soal_aktif["soal"])
            
            pilihan_user = st.radio("Pilih jawaban yang menurut Anda benar:", soal_aktif["pilihan"], key=f"radio_soal_{id_sekarang}")
            
            col_k1, col_k2 = st.columns([1, 4])
            with col_k1:
                if st.button("Kirim Jawaban ✔️"):
                    st.session_state.quiz_terjawab = True
            
            # Jika user sudah klik kirim jawaban, langsung munculkan pembahasan di bawahnya
            if st.session_state.quiz_terjawab:
                if pilihan_user == soal_aktif["jawaban"]:
                    st.success("🎉 Jawaban Anda Benar!")
                else:
                    st.error(f"❌ Jawaban kurang tepat. Jawaban yang benar adalah: {soal_aktif['jawaban']}")
                
                # Kotak pembahasan
                st.markdown(f"""
                <div style="background-color: #f1f2f6; padding: 15px; border-radius: 8px; border-left: 5px solid #74b9ff; margin-bottom: 15px;">
                    <b style="color: #2f3542;">📘 Pembahasan:</b><br>{soal_aktif['pembahasan']}
                </div>
                """, unsafe_allow_html=True)
                
                # Tombol lanjut ke nomor berikutnya
                if st.button("Lanjut ke Soal Berikutnya ➡️"):
                    st.session_state.quiz_index += 1
                    st.session_state.quiz_terjawab = False
                    st.rerun()
        else:
            st.balloons()
            st.success("🏆 Selamat! Anda telah menyelesaikan seluruh soal kuis Kelompok 11 dengan baik.")
            if st.button("Ulangi Kuis dari Awal 🔄"):
                st.session_state.quiz_index = 0
                st.session_state.quiz_terjawab = False
                st.rerun()
        
