import streamlit as st
import pubchempy as pcp
import py3Dmol
from stmol import showmol
import requests

# Konfigurasi Halaman Web
st.set_page_config(page_title="Penjelajah Senyawa Organik", layout="wide", page_icon="🧪")

st.title("🧪 Web Visualisasi & Properti Senyawa Organik")
st.write("Masukkan nama senyawa secara IUPAC atau Trivial (Disarankan menggunakan bahasa Inggris untuk akurasi database yang lebih tinggi, misal: Acetic acid, Benzene, Ethanol).")

# Input user
compound_name = st.text_input("Masukkan Nama Senyawa:", "Aspirin")

if st.button("Cari Senyawa"):
    with st.spinner("Mengambil data dari database PubChem..."):
        try:
            # Mencari senyawa menggunakan PubChemPy berdasarkan nama
            compounds = pcp.get_compounds(compound_name, 'name')
            
            if compounds:
                c = compounds[0]
                
                # Membagi layar menjadi 2 kolom
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📝 Properti Senyawa")
                    st.write(f"*Nama IUPAC:* {c.iupac_name}")
                    st.write(f"*Rumus Molekul:* {c.molecular_formula}")
                    st.write(f"*Berat Molekul:* {c.molecular_weight} g/mol")
                    st.write(f"*SMILES:* {c.canonical_smiles}")
                    
                    # Catatan Realitas Database:
                    # Titik didih dan reaktivitas eksperimental tersimpan dalam struktur JSON 
                    # yang sangat kompleks di PubChem PUG REST, sehingga kita berikan placeholder informatif.
                    st.write("---")
                    st.write("*Titik Didih & Reaktivitas:*")
                    st.info("💡 Catatan Realitas Data: Data seperti titik didih (Boiling Point) dan reaktivitas spesifik membutuhkan parsing lanjutan dari literatur eksperimental atau API PubChem tingkat lanjut. Pada tahap ini, web memprioritaskan kalkulasi struktur fisik dasar.")
                
                with col2:
                    st.subheader("🧬 Struktur 3D (Gaya Molymod)")
                    # Mengambil data koordinat 3D (SDF) langsung dari PubChem REST API
                    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{c.cid}/record/SDF/?record_type=3d"
                    response = requests.get(url)
                    
                    if response.status_code == 200:
                        sdf_data = response.text
                        
                        # Render 3D menggunakan py3Dmol
                        view = py3Dmol.view(width=450, height=450)
                        view.addModel(sdf_data, 'sdf')
                        
                        # Styling 'Molymod' (Ball and Stick)
                        view.setStyle({'stick': {'radius': 0.15}, 'sphere': {'radius': 0.4}})
                        view.setBackgroundColor('#ffffff')
                        view.zoomTo()
                        
                        # Tampilkan di Streamlit
                        showmol(view, height=450, width=450)
                    else:
                        st.warning("Koordinat 3D tidak tersedia di database untuk senyawa ini. Menampilkan struktur 2D tidak didukung pada blok ini.")
            else:
                st.error("Senyawa tidak ditemukan. Coba gunakan istilah bahasa Inggris (Contoh: gunakan 'Water' untuk Air).")
                
        except Exception as e:
            st.error(f"Terjadi kesalahan sistem: {e}")
