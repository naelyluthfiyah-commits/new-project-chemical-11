import streamlit as st

st.set_page_config(
page_title="Chem Analysis",
page_icon="🧪",
layout="wide"
)

# =========================

# COVER PAGE

# =========================

st.title("🧪 CHEM ANALYSIS")
st.subheader("Aplikasi Pembelajaran Kimia Organik")

st.markdown("---")

st.markdown("""

### Anggota Kelompok

* ANDIKA DWI PRASHOJO
* JAWAHER SABRINA A
* NAELY LUTHFIYAH ARIF
* SALWA AZKA SABANA
* ALEX KUSUMAH
  """)

st.markdown("---")

menu = st.sidebar.selectbox(
"Pilih Menu",
[
"Beranda",
"Tata Penamaan Senyawa",
"Latihan Soal"
]
)

# =========================

# TATA PENAMAAN

# =========================

if menu == "Tata Penamaan Senyawa":

```
st.header("Tata Penamaan Senyawa Organik")

nama = st.text_input(
    "Masukkan nama senyawa (IUPAC atau trivial)"
)

if st.button("Mulai"):

    st.success("Data senyawa ditemukan")

    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Ethanol-3D-balls.png/640px-Ethanol-3D-balls.png",
        width=300
    )

    st.write("### Informasi Senyawa")

    st.write("Nama IUPAC : Ethanol")
    st.write("Rumus Molekul : C₂H₆O")
    st.write("Berat Molekul : 46.07 g/mol")
    st.write("Titik Didih : 78.37 °C")
    st.write("Sifat : Cairan tidak berwarna")
    st.write("Reaktivitas : Mudah terbakar")

    st.markdown("---")

    st.subheader("Prediksi Reaksi")

    reaktan = st.text_input(
        "Masukkan reagen tambahan"
    )

    if st.button("Prediksi Reaksi"):

        st.write(
            "Jenis reaksi: Oksidasi"
        )

        st.write(
            "Produk: Asam asetat"
        )

        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Acetic-acid-3D-balls.png/640px-Acetic-acid-3D-balls.png",
            width=300
        )
```

# =========================

# LATIHAN SOAL

# =========================

elif menu == "Latihan Soal":

```
st.header("Latihan Tata Nama Senyawa")

soal = [
    {
        "gambar":"https://upload.wikimedia.org/wikipedia/commons/6/63/Butane-2D-skeletal.png",
        "jawaban":"butana"
    }
]

st.image(soal[0]["gambar"])

jawab = st.text_input(
    "Nama senyawa?"
)

if st.button("Periksa"):

    if jawab.lower() == soal[0]["jawaban"]:
        st.success("Benar")
    else:
        st.error("Salah")

    st.write(
        "Pembahasan: Struktur tersebut adalah butana."
    )
```
