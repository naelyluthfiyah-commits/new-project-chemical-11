import streamlit as st
import requests
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
import numpy as np

# Judul Aplikasi
st.title("Aplikasi Tata Penamaan Senyawa Organik")

# Cover depan
st.markdown("""
## Anggota Kelompok:
- ANDIKA DWI PRASHOJO
- JAWAHER SABRINA A
- NAELY LUTHFIYAH ARIF
- SALWA AZKA SABANA
- ALEX KUSUMAH
""")

# Pilihan Menu
option = st.selectbox("Pilih Menu:", ("Tata Penamaan Senyawa", "Latihan Soal"))

if option == "Tata Penamaan Senyawa":
    st.header("Tata Penamaan Senyawa Organik")

    # Input nama senyawa
    compound_name = st.text_input("Masukkan nama senyawa (IUPAC atau Trivial):")
    
    if st.button("Mulai"):
        # Mengambil data dari PubChem
        try:
            compound_info = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/JSON").json()
            compound_data = compound_info['PC_Compounds'][0]
            smiles = compound_data['props'][0]['value']['sval']
            mol = Chem.MolFromSmiles(smiles)
            img = Draw.MolToImage(mol, size=(300, 300))

            # Menampilkan informasi
            st.image(img, caption=f"Struktur Senyawa: {compound_name}")
            st.write("Berat Molekul:", compound_data['props'][1]['value']['fval'])
            st.write("Titik Didih:", compound_data['props'][2]['value']['fval'])
            st.write("Sifat dan reaktivitas:", compound_data['props'][3]['value']['sval'])

            # Input untuk reaksi
            reactant = st.text_input("Masukkan senyawa reaktan:")
            if st.button("Reaksi"):
                # Proses reaksi (simulasi)
                # Untuk demonstrasi, kita akan menggunakan placeholder
                st.write(f"Melakukan reaksi antara {compound_name} dan {reactant}...")
                st.write("Hasil reaksi: [Gambar reaksi di sini]")
                st.write("Reaksi: [Jenis reaksi]")
                st.write("Berat Molekul hasil reaksi:", "X g/mol")
                st.write("Titik Didih hasil reaksi:", "Y °C")
                st.write("Sifat bahan dan reaktivitas hasil reaksi:", "[Info]")
        except:
            st.error("Data senyawa tidak ditemukan. Pastikan nama senyawa benar.")

elif option == "Latihan Soal":
    st.header("Latihan Soal")
    st.write("Tebak rumus struktur berikut dengan nama IUPAC atau Trivial.")

    # Simulasi soal
    questions = [
        ("Soal 1: Struktur 1", "Etilena"), 
        ("Soal 2: Struktur 2", "Propana"),
        # Tambahkan 8 soal lainnya di sini...
    ]

    for question in questions:
        st.subheader(question[0])
        answer = st.text_input("Jawaban Anda:")
        if st.button("Cek Jawaban"):
            if answer.lower() == question[1].lower():
                st.success("Benar!")
            else:
                st.error("Salah! Jawaban yang benar adalah: " + question[1])
