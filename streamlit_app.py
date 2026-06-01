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

st.title("🔍 Pencarian Senyawa")

try:
    df = pd.read_csv("data/senyawa.csv")

    keyword = st.text_input(
        "Masukkan nama IUPAC, nama trivial, atau rumus"
    )

    if keyword:

        hasil = df[
            df["nama_iupac"].str.contains(keyword, case=False, na=False) |
            df["nama_trivial"].str.contains(keyword, case=False, na=False) |
            df["rumus"].str.contains(keyword, case=False, na=False)
        ]

        if not hasil.empty:
            st.dataframe(hasil)
        else:
            st.warning("Data tidak ditemukan")

except Exception as e:
    st.error(f"Terjadi error: {e}")
