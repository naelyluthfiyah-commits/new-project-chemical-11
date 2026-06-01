import streamlit as st
import pandas as pd

# Judul
st.title("🧪 Pencarian Nama Senyawa Kimia")

# Membaca data
data = pd.read_csv("senyawa.csv")

# Input pengguna
cari = st.text_input("Masukkan nama atau rumus kimia")

# Tombol cari
if st.button("Cari"):

    ditemukan = False

    for i in range(len(data)):

        if (cari.lower() == str(data.loc[i, "nama_iupac"]).lower()
            or cari.lower() == str(data.loc[i, "nama_trivial"]).lower()
            or cari.lower() == str(data.loc[i, "rumus"]).lower()):

            st.success("Data ditemukan!")

            st.write("Nama IUPAC :", data.loc[i, "nama_iupac"])
            st.write("Nama Trivial :", data.loc[i, "nama_trivial"])
            st.write("Rumus :", data.loc[i, "rumus"])

            ditemukan = True

    if ditemukan == False:
        st.error("Data tidak ditemukan")
