import streamlit as st

st.set_page_config(
    page_title="ChemName Explorer",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 ChemName Explorer")

st.markdown("""
### Website Tata Nama Senyawa Organik

Mencari:
- Nama IUPAC
- Nama Trivial
- Rumus Molekul
- Struktur Senyawa

Menggunakan database kimia organik.
""")

pages/1_Pencarian.py

import streamlit as st
import pandas as pd

df = pd.read_csv("data/senyawa.csv")

st.title("🔍 Pencarian Senyawa")

keyword = st.text_input("Masukkan nama atau rumus")

if keyword:

    hasil = df[
        df["nama_iupac"].str.contains(keyword, case=False) |
        df["nama_trivial"].str.contains(keyword, case=False) |
        df["rumus"].str.contains(keyword, case=False)
    ]

    if len(hasil) > 0:
        st.dataframe(hasil)

    else:
        st.error("Data tidak ditemukan")
