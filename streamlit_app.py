import streamlit as st
import requests

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
    page_title="ChemExplorer Pro - Kelompok Kimia", 
    layout="wide",
    page_icon="🧪"
)

# 2. INJEKSI CUSTOM CSS UNTUK TEMA COLORFUL
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    /* Style untuk semua tombol utama */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ff7675, #6c5ce7);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.03);
        box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3);
    }
    /* Gaya untuk Tab */
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: bold;
        color: #636e72;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #6c5ce7;
    }
    .stTabs [aria-selected="true"] {
        color: #6c5ce7 !important;
        border-bottom-color: #6c5ce7 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. COVER WEB & BANNER SELAMAT DATANG
st.markdown("""
<div style="background: linear-gradient(135deg, #6c5ce7, #a29bfe, #fd79a8, #ffeaa7); padding: 40px; border-radius: 20px; color: white; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 25px;">
    <h1 style="color: white; margin: 0; font-size: 40px; font-weight: 800; font-family: 'Segoe UI', Arial, sans-serif; text-shadow: 2px 2px 4px rgba(0,0,0,0.15);">
        🧪 ChemExplorer Pro v2.0
    </h1>
    <p style="font-size: 17px; opacity: 0.95; margin-top: 10px; margin-bottom: 0; font-weight: 500; letter-spacing: 0.5px;">
        Pusat Edukasi Kimia Organik: Visualisasi 3D, Mekanisme Reaksi & Evaluasi Mandiri
    </p>
</div>
""", unsafe_allow_html=True)

# 4. BAGIAN ANGGOTA KELOMPOK
st.markdown("<h4 style='text-align: center; color: #2d3436; font-weight: 700; margin-bottom: 15px;'>👥 Tim Peneliti / Anggota Kelompok</h4>", unsafe_allow_html=True)
member_cols = st.columns(4)
colors = [
    {"bg": "#ffeaa7", "border": "#fdcb6e", "text": "#d35400", "emoji": "🧑‍💻"},
    {"bg": "#dff9fb", "border": "#c7ecee", "text": "#0984e3", "emoji": "👩‍🔬"},
    {"bg": "#ffdfdf", "border": "#ff7675", "text": "#c0392b", "emoji": "👨‍🎨"},
    {"bg": "#ebfffa", "border": "#55efc4", "text": "#00b894", "emoji": "👩‍💻"}
]

# SILAKAN EDIT DATA ANGGOTA DI SINI
members_data = [
    {"nama": "Andika Dwi Prashojo", "nim": "NIM. 2560571", "role": "Project Leader", "color": colors[0]},
    {"nama": "Jawaher Sabrina Alodya A. S.", "nim": "NIM. 2560648", "role": "Backend API Specialist", "color": colors[1]},
    {"nama": "Naely Luthfiyah Arif", "nim": "NIM. 2560698", "role": "3D Renderer Expert", "color": colors[2]},
    {"nama": "Salwa Azka Sabana", "nim": "NIM. 2560767", "role": "UI/UX & Content Writer", "color": colors[3]},
]

for idx, col in enumerate(member_cols):
    data = members_data[idx]
    with col:
        st.markdown(f"""
        <div style="background-color: {data['color']['bg']}; padding: 15px; border-radius: 12px; border-top: 5px solid {data['color']['border']}; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.03); min-height: 140px;">
            <div style="font-size: 24px;">{data['color']['emoji']}</div>
            <h5 style="margin: 5px 0 2px 0; color: #2d3436; font-size: 15px; font-weight: bold;">{data['nama']}</h5>
            <p style="margin: 0; color: {data['color']['text']}; font-size: 12px; font-weight: bold;">{data['nim']}</p>
            <p style="margin: 5px 0 0 0; color: #636e72; font-size: 11px; font-style: italic;">{data['role']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. MEMBUAT NAVIGASI TAB MENU UTAMA
tab1, tab2, tab3 = st.tabs(["🔍 Penjelajah 3D", "⚡ Simulasi Reaksi", "📝 Kuis Tata Nama"])

# ==========================================
# TAB 1: PENJELAJAH SENYAWA 3D
# ==========================================
with tab1:
    if not IMPORTS_SUCCESSFUL:
        st.error(f"❌ Gagal memuat pustaka kimia. Masalah: {IMPORT_ERROR_MSG}")
    else:
        st.markdown("<h3 style='color: #6c5ce7;'>🔍 Eksplorasi Senyawa Organik</h3>", unsafe_allow_html=True)
        nama_senyawa = st.text_input("Ketik Nama Senyawa (Bahasa Inggris):", "Caffeine", key="search_input")

        if st.button("Analisis & Visualisasikan", key="btn_search"):
            with st.spinner("Menghubungkan ke database PubChem..."):
                try:
                    hasil_pencarian = pcp.get_compounds(nama_senyawa, 'name')
                    if hasil_pencarian:
                        senyawa = hasil_pencarian[0]
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
                                </table>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with kol2:
                            st.markdown("""
                            <div style="background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 5px solid #fd79a8;">
                                <h4 style="color: #fd79a8; margin-top: 0;">🧬 Visualisasi Model 3D</h4>
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
                            else:
                                st.warning("⚠️ Struktur 3D tidak tersedia di database.")
                    else:
                        st.error("❌ Senyawa tidak ditemukan. Gunakan ejaan bahasa Inggris.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# TAB 2: SIMULASI REAKSI KIMIA
# ==========================================
with tab2:
    st.markdown("<h3 style='color: #e17055;'>⚡ Pusat Fitur Reaksi Kimia Organik</h3>", unsafe_allow_html=True)
    st.write("Pilih salah satu jenis reaksi di bawah ini untuk melihat simulasi persamaan reaksi dan mekanismenya:")

    opsi_reaksi = st.selectbox(
        "Pilih Contoh Reaksi Kimia:",
        ["Alkilasi Friedel-Crafts (Benzena + CH3Cl)", "Esterifikasi (Asam Asetat + Etanol)", "Hidrogenasi Alkena (Etena + H2)"]
    )

    if opsi_reaksi == "Alkilasi Friedel-Crafts (Benzena + CH3Cl)":
        st.markdown("""
        <div style="background-color: #fff9f4; padding: 25px; border-radius: 15px; border-left: 5px solid #e17055; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
            <h4 style="color: #d63031; margin-top:0;">🧪 Alkilasi Friedel-Crafts (Substitusi Elektrofilik Aromatik)</h4>
            <p>Reaksi ini memasukkan gugus alkil ke dalam cincin benzena menggunakan katalis asam Lewis seperti AlCl₃.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Menggunakan LaTeX bawaan Streamlit untuk merender rumus kimia yang rapi
        st.subheader("📝 Persamaan Reaksi:")
        st.latex(r"\text{C}_6\text{H}_6 \text{ (Benzena)} + \text{CH}_3\text{Cl} \text{ (Metil Klorida)} \xrightarrow{\text{AlCl}_3} \text{C}_6\text{H}_5\text{CH}_3 \text{ (Toluena)} + \text{HCl} \text{ (Asam Klorida)}")
        
        st.info("💡 **Mekanisme Singkat:** Katalis $AlCl_3$ akan menarik atom klorin dari $CH_3Cl$ membentuk elektrofil kuat $CH_3^+$ (karbokation). Karbokation ini kemudian menyerang awan elektron cincin Benzena yang kaya elektron, menggantikan salah satu atom hidrogen ($H^+$), dan menghasilkan senyawa produk bernama **Toluena**.")

    elif opsi_reaksi == "Esterifikasi (Asam Asetat + Etanol)":
        st.markdown("""
        <div style="background-color: #f5f6fa; padding: 25px; border-radius: 15px; border-left: 5px solid #0984e3;">
            <h4 style="color: #0984e3; margin-top:0;">🧪 Reaksi Esterifikasi Fischer</h4>
            <p>Reaksi pembentukan senyawa Ester berbau harum melalui pencampuran asam karboksilat dan alkohol dibantu katalis asam kuat ($H_2SO_4$).</p>
        </div>
        """, unsafe_allow_html=True)
        st.subheader("📝 Persamaan Reaksi:")
        st.latex(r"\text{CH}_3\text{COOH} + \text{CH}_3\text{CH}_2\text{OH} \xrightarrow{\text{H}_2\text{SO}_4} \text{CH}_3\text{COOCH}_2\text{CH}_3 \text{ (Etil Asetat)} + \text{H}_2\text{O}")

    elif opsi_reaksi == "Hidrogenasi Alkena (Etena + H2)":
        st.markdown("""
        <div style="background-color: #f7fff7; padding: 25px; border-radius: 15px; border-left: 5px solid #2ecc71;">
            <h4 style="color: #2ecc71; margin-top:0;">🧪 Reaksi Adisi Hidrogenasi</h4>
            <p>Reaksi pemutusan ikatan rangkap dua (tidak jenuh) menjadi ikatan tunggal (jenuh) menggunakan gas hidrogen dengan katalis logam seperti Pt, Pd, atau Ni.</p>
        </div>
        """, unsafe_allow_html=True)
        st.subheader("📝 Persamaan Reaksi:")
        st.latex(r"\text{CH}_2\text{=CH}_2 \text{ (Etena)} + \text{H}_2 \xrightarrow{\text{Ni/Pt}} \text{CH}_3\text{-CH}_3 \text{ (Etana)}")

# ==========================================
# TAB 3: FITUR LATIHAN SOAL (10 SOAL TATA NAMA)
# ==========================================
with tab3:
    st.markdown("<h3 style='color: #00b894;'>📝 Uji Kemampuan: Kuis Tata Nama IUPAC</h3>", unsafe_allow_html=True)
    st.write("Isi seluruh pertanyaan pilihan ganda di bawah ini, lalu klik tombol **Kirim Jawaban** di bagian paling bawah untuk melihat perolehan nilai Anda!")

    # Menggunakan form agar halaman tidak bolak-balik loading saat user memilih jawaban
    with st.form("kuis_tata_nama"):
        
        # Soal 1
        q1 = st.radio("1. Apa nama IUPAC untuk senyawa alkana rantai lurus dengan rumus struktur CH3-CH2-CH2-CH3?", 
                      ["Propana", "Butana", "Pentana", "Heksana"])
        # Soal 2
        q2 = st.radio("2. Nama yang tepat untuk senyawa bercabang CH3-CH(CH3)-CH3 adalah...", 
                      ["2-metilpropana", "Butana", "Metilbutana", "Dimetiletana"])
        # Soal 3
        q3 = st.radio("3. Senyawa hidrokarbon yang memiliki struktur CH3-CH=CH-CH3 dinamakan...", 
                      ["1-butena", "2-butena", "Butuna", "2-butuna"])
        # Soal 4
        q4 = st.radio("4. Gugus fungsi alkohol (-OH) terikat pada rantai etana (CH3-CH2-OH). Apa nama IUPAC-nya?", 
                      ["Metanol", "Etanol", "Propanol", "Eter"])
        # Soal 5
        q5 = st.radio("5. Senyawa asam karboksilat dengan rumus molekul CH3-COOH dikenal secara sistematis sebagai...", 
                      ["Asam Metanoat", "Asam Etanoat", "Asam Propanoat", "Asam Asetat"])
        # Soal 6
        q6 = st.radio("6. Cincin benzena yang salah satu atom H-nya disubstitusi oleh gugus hidroksil (-OH) diberi nama...", 
                      ["Toluena", "Anilin", "Fenol", "Nitrobenzena"])
        # Soal 7
        q7 = st.radio("7. Jika gugus metil (-CH3) melekat pada cincin benzena, nama senyawa turunan benzena tersebut adalah...", 
                      ["Fenol", "Toluena", "Asam Benzoat", "Stirena"])
        # Soal 8
        q8 = st.radio("8. Apa nama IUPAC untuk struktur eter berikut: CH3-O-CH3?", 
                      ["Dimetil Eter", "Metoksimetana", "Etoksimetana", "Metoksiatana"])
        # Soal 9
        q9 = st.radio("9. Senyawa keton komersial (aseton) memiliki nama resmi IUPAC berupa...", 
                      ["Propanal", "Propanon", "Etanon", "Butanon"])
        # Soal 10
        q10 = st.radio("10. Senyawa aldehid dengan rumus struktur CH3-CH2-CHO memiliki nama IUPAC...", 
                       ["Propanal", "Propanon", "Etanol", "Metanal"])

        # Tombol Submit di dalam form
        tombol_submit_kuis = st.form_submit_button("Kirim Jawaban & Hitung Skor")

    if tombol_submit_kuis:
        # Kunci Jawaban Benar
        skor = 0
        if q1 == "Butana": skor += 10
        if q2 == "2-metilpropana": skor += 10
        if q3 == "2-butena": skor += 10
        if q4 == "Etanol": skor += 10
        if q5 == "Asam Etanoat": skor += 10
        if q6 == "Fenol": skor += 10
        if q7 == "Toluena": skor += 10
        if q8 == "Metoksimetana": skor += 10
        if q9 == "Propanon": skor += 10
        if q10 == "Propanal": skor += 10

        # Menampilkan Hasil Kelulusan / Skor Berdasarkan Nilai
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("📊 Hasil Evaluasi Kuis Anda:")
        if skor >= 70:
            st.success(f"🎉 Selamat! Anda lulus dengan nilai yang sangat baik: **{skor} / 100**")
        else:
            st.warning(f"📚 Skor Anda adalah **{skor} / 100**. Tetap semangat belajar dan baca kembali materi tata nama IUPAC!")                
