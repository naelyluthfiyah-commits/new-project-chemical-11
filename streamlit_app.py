import streamlit as st
import requests

# 1. JARING PENGAMAN IMPORT: Jika library kimia gagal dimuat, web tidak akan mati total
try:
    import pubchempy as pcp
    from stmol import showmol
    import py3Dmol
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    IMPORTS_SUCCESSFUL = False
    IMPORT_ERROR_MSG = str(e)

# Konfigurasi halaman
st.set_page_config(page_title="Kalkulator Senyawa Kimia", layout="wide")
st.title("🧪 Aplikasi Penjelajah Senyawa Organik")

# Cek apakah instalasi library di server berhasil
if not IMPORTS_SUCCESSFUL:
    st.error(f"❌ Gagal memuat pustaka kimia. Masalah: {IMPORT_ERROR_MSG}")
    st.info("Tips: Pastikan file 'requirements.txt' sudah di-upload ke GitHub di folder yang sama dengan app.py.")
else:
    # Input dari user
    st.write("Masukkan nama senyawa dalam bahasa Inggris (Contoh: *Ethanol*, *Benzene*, *Caffeine*, *Aspirin*)")
    nama_senyawa = st.text_input("Nama Senyawa:", "Butanol")

    if st.button("Cari Data"):
        with st.spinner("Sedang mencari di database PubChem..."):
            try:
                # Cari senyawa berdasarkan nama
                hasil_pencarian = pcp.get_compounds(nama_senyawa, 'name')
                
                if hasil_pencarian:
                    senyawa = hasil_pencarian[0]
                    
                    # Bagi menjadi 2 kolom
                    kol1, kol2 = st.columns(2)
                    
                    with kol1:
                        st.subheader("📝 Informasi Senyawa")
                        st.success(f"Senyawa ditemukan! (CID: {senyawa.cid})")
                        st.write(f"**Nama IUPAC:** {getattr(senyawa, 'iupac_name', 'Tidak tersedia')}")
                        st.write(f"**Rumus Molekul:** {getattr(senyawa, 'molecular_formula', 'Tidak tersedia')}")
                        st.write(f"**Berat Molekul:** {getattr(senyawa, 'molecular_weight', 'Tidak tersedia')} g/mol")
                        
                        st.info("💡 **Titik Didih & Reaktivitas:** Data ini memerlukan analisis teks dokumen (parsing) yang lebih mendalam dari server PubChem, sehingga belum dapat ditampilkan secara instan pada versi dasar ini.")
                    
                    with col2:
                        st.subheader("🧬 Visualisasi 3D (Gaya Molymod)")
                        # Ambil data koordinat 3D
                        url_3d = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{senyawa.cid}/record/SDF/?record_type=3d"
                        respon = requests.get(url_3d, timeout=10)
                        
                        # --- PERBAIKAN DI BARIS INI (Menghapus .strip() yang salah) ---
                        if respon.status_code == 200 and len(respon.text) > 100:
                            try:
                                # Render objek 3D
                                view = py3Dmol.view(width=400, height=400)
                                view.addModel(respon.text, 'sdf')
                                view.setStyle({'stick': {'radius': 0.2}, 'sphere': {'radius': 0.4}})
                                view.setBackgroundColor('#ffffff')
                                view.zoomTo()
                                showmol(view, height=400, width=400)
                            except Exception as err_render:
                                st.warning(f"Gagal merender struktur 3D: {err_render}")
                        else:
                            st.warning("⚠️ Struktur 3D tidak tersedia untuk senyawa ini di database PubChem.")
                            
                else:
                    st.error("❌ Senyawa tidak ditemukan. Pastikan ejaan benar dan gunakan bahasa Inggris.")
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan saat mengambil data: {e}")
                
