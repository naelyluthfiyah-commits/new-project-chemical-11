import streamlit as st
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
import pandas as pd
import random

# Konfigurasi halaman
st.set_page_config(
    page_title="Kimia Organik App",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================= COVER PAGE =======================
def cover_page():
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h1 style="font-size: 3.2em; color: #1E3A8A; margin-bottom: 10px;">
            Kimia Organik Interaktif
        </h1>
        <p style="font-size: 1.3em; color: #334155; margin-bottom: 50px;">
            Aplikasi Pembelajaran Tata Nama & Reaksi Senyawa Organik
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Daftar Anggota
    st.markdown("### 👥 Anggota Kelompok")
    members = [
        "ANDIKA DWI PRASHOJO",
        "JAWAHER SABRINA A",
        "NAELY LUTHFIYAH ARIF",
        "SALWA AZKA SABANA",
        "ALEX KUSUMAH"
    ]

    col1, col2 = st.columns(2)
    with col1:
        for i, name in enumerate(members[:3]):
            st.markdown(f"**{i+1}.** {name}")
    with col2:
        for i, name in enumerate(members[3:]):
            st.markdown(f"**{i+4}.** {name}")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Pilihan Menu
    st.markdown("### Pilih Menu")
    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🔬 Tata Penamaan Senyawa Organik", use_container_width=True, type="primary"):
            st.session_state.page = "tata_nama"
            st.rerun()

    with col_b:
        if st.button("📝 Latihan Soal", use_container_width=True):
            st.session_state.page = "latihan_soal"
            st.session_state.soal_index = 0
            st.session_state.score = 0
            st.session_state.history = []
            st.rerun()

# ======================= HALAMAN TATA NAMA =======================
def tata_nama_page():
    st.title("Tata Penamaan Senyawa Organik")
    st.caption("Masukkan nama senyawa (IUPAC atau trivial) → sistem akan mencari data PubChem")

    if "mol_data" not in st.session_state:
        st.session_state.mol_data = None
    if "reaction_data" not in st.session_state:
        st.session_state.reaction_data = None

    # Input Senyawa Awal
    col1, col2 = st.columns([3, 1])
    with col1:
        nama_senyawa = st.text_input(
            "Nama Senyawa",
            placeholder="Contoh: ethanol, asam asetat, benzene, propanol"
        )
    with col2:
        st.write("")
        st.write("")
        if st.button("Mulai", type="primary"):
            if nama_senyawa.strip():
                try:
                    compound = pcp.get_compounds(nama_senyawa, 'name')[0]
                    smiles = compound.isomeric_smiles or compound.canonical_smiles
                    mol = Chem.MolFromSmiles(smiles)
                    
                    if mol:
                        mw = round(compound.molecular_weight, 2) if compound.molecular_weight else "N/A"
                        boiling_point = compound.boiling_point if hasattr(compound, 'boiling_point') else "Tidak tersedia"
                        
                        st.session_state.mol_data = {
                            "nama": nama_senyawa,
                            "smiles": smiles,
                            "mw": mw,
                            "boiling_point": boiling_point,
                            "iupac": compound.iupac_name,
                            "formula": compound.molecular_formula,
                        }
                    else:
                        st.error("Tidak dapat membuat struktur dari senyawa tersebut.")
                except Exception as e:
                    st.error(f"Senyawa tidak ditemukan di PubChem. Coba nama lain.")
            else:
                st.warning("Harap masukkan nama senyawa.")

    # Tampilkan Hasil Senyawa Awal
    if st.session_state.mol_data:
        data = st.session_state.mol_data
        st.subheader(f"Struktur: {data['nama'].title()}")

        col_img, col_info = st.columns([1.2, 1])
        
        with col_img:
            mol = Chem.MolFromSmiles(data['smiles'])
            AllChem.EmbedMolecule(mol, randomSeed=42)
            img = Draw.MolToImage(mol, size=(400, 300))
            st.image(img, caption="Representasi Struktur 3D (Molymod Style)", width=380)

        with col_info:
            st.write("**Informasi Senyawa**")
            st.write(f"- **Rumus Kimia**: {data['formula']}")
            st.write(f"- **Nama IUPAC**: {data['iupac']}")
            st.write(f"- **Berat Molekul**: {data['mw']} g/mol")
            st.write(f"- **Titik Didih**: {data['boiling_point']}")
            st.write(f"- **Reaktivitas**: (Analisis otomatis tersedia di bawah)")

        st.divider()

        # Input Reaksi
        st.subheader("Reaksi dengan Senyawa Lain")
        reaktan = st.text_input(
            "Masukkan nama senyawa reaktan (opsional)", 
            placeholder="Contoh: HCl, Br2, NaOH, air"
        )

        if st.button("Lakukan Reaksi", type="secondary"):
            if reaktan.strip():
                # Simulasi reaksi sederhana (bisa diperluas)
                st.session_state.reaction_data = {
                    "reaktan": reaktan,
                    "produk": f"{data['nama']} + {reaktan}",
                    "reaksi": "Substitusi / Adisi (simulasi)"
                }
                st.rerun()

    # Tampilkan Hasil Reaksi
    if st.session_state.reaction_data:
        st.subheader("Hasil Reaksi")
        rd = st.session_state.reaction_data
        st.write(f"**Reaktan**: {rd['reaktan']}")
        st.write(f"**Jenis Reaksi**: {rd['reaksi']}")

        # Placeholder untuk produk (bisa dikembangkan lebih lanjut)
        st.info("Produk dan struktur 3D akan ditampilkan di sini setelah integrasi RDKit yang lebih lengkap.")

    # Tombol Kembali
    if st.button("Kembali ke Menu Utama"):
        st.session_state.page = "cover"
        st.session_state.mol_data = None
        st.session_state.reaction_data = None
        st.rerun()

# ======================= HALAMAN LATIHAN SOAL =======================
SOAL_BANK = [
    {"struktur": "CH3-CH2-OH", "iupac": "etanol", "trivial": "alkohol"},
    {"struktur": "CH3-COOH", "iupac": "asam etanoat", "trivial": "asam asetat"},
    {"struktur": "CH3-CH2-CH3", "iupac": "propana", "trivial": "propana"},
    {"struktur": "CH2=CH2", "iupac": "etena", "trivial": "etilena"},
    {"struktur": "C6H6", "iupac": "benzena", "trivial": "benzena"},
    {"struktur": "CH3-CHO", "iupac": "etanal", "trivial": "asetaldehida"},
    {"struktur": "CH3-CH2-Cl", "iupac": "kloroetana", "trivial": "etil klorida"},
    {"struktur": "CH3-C≡CH", "iupac": "propuna", "trivial": "metilasetilen"},
    {"struktur": "CH3-CH(OH)-CH3", "iupac": "propan-2-ol", "trivial": "isopropanol"},
    {"struktur": "HCOOH", "iupac": "asam metanoat", "trivial": "asam format"},
]

def latihan_soal_page():
    st.title("Latihan Soal Tata Nama Senyawa Organik")
    st.caption("Tebak nama senyawa berdasarkan rumus strukturnya (IUPAC atau Trivial)")

    if "soal_index" not in st.session_state:
        st.session_state.soal_index = 0
        st.session_state.score = 0
        st.session_state.history = []

    # Ambil 10 soal acak
    if "current_questions" not in st.session_state:
        st.session_state.current_questions = random.sample(SOAL_BANK, 10)

    q_list = st.session_state.current_questions
    idx = st.session_state.soal_index

    if idx < len(q_list):
        q = q_list[idx]
        st.progress((idx) / len(q_list))
        st.write(f"**Soal {idx + 1} dari {len(q_list)}**")

        st.markdown(f"""
        <div style="background-color:#f1f5f9; padding:20px; border-radius:10px; margin-bottom:20px;">
            <h3>Rumus Struktur:</h3>
            <h2 style="font-family:monospace;">{q['struktur']}</h2>
        </div>
        """, unsafe_allow_html=True)

        jawaban = st.text_input("Masukkan nama IUPAC atau Trivial:", key=f"jawab_{idx}")

        if st.button("Jawab"):
            jawab_benar = False
            if jawaban.strip().lower() in [q['iupac'].lower(), q['trivial'].lower()]:
                st.success("✅ Benar!")
                st.session_state.score += 1
                benar = True
            else:
                st.error("❌ Salah!")
                benar = False

            st.session_state.history.append({
                "soal": q['struktur'],
                "jawaban_user": jawaban,
                "jawaban_benar": q['iupac'],
                "benar": benar
            })

            st.session_state.soal_index += 1
            st.rerun()

    else:
        # Hasil Akhir
        st.balloons()
        total = len(q_list)
        skor = st.session_state.score
        st.subheader(f"Hasil Akhir: {skor} / {total}")

        if st.button("Lanjutkan ke 10 Soal Berikutnya"):
            st.session_state.current_questions = random.sample(SOAL_BANK, 10)
            st.session_state.soal_index = 0
            st.session_state.score = 0
            st.session_state.history = []
            st.rerun()

        if st.button("Kembali ke Menu Utama"):
            st.session_state.page = "cover"
            st.rerun()

# ======================= MAIN APP =======================
def main():
    if "page" not in st.session_state:
        st.session_state.page = "cover"

    if st.session_state.page == "cover":
        cover_page()
    elif st.session_state.page == "tata_nama":
        tata_nama_page()
    elif st.session_state.page == "latihan_soal":
        latihan_soal_page()

if __name__ == "__main__":
    main()
