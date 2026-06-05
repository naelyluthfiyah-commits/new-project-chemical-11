import streamlit as st
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Draw

# Define function to draw molecule and save as image
def draw_molecule(smiles):
    mol = Chem.MolFromSmiles(smiles)
    img = Draw.MolToImage(mol)
    return img

# Cover Page
st.title("Aplikasi Tata Penamaan Senyawa Organik")
st.subheader("Anggota Kelompok:")
st.write("ANDIKA DWI PRASHOJO")
st.write("JAWAHER SABRINA A")
st.write("NAELY LUTHFIYAH ARIF")
st.write("SALWA AZKA SABANA")
st.write("ALEX KUSUMAH")

option = st.selectbox("Pilih fitur:", ["Tata Penamaan Senyawa", "Latihan Soal"])

if option == "Tata Penamaan Senyawa":
    st.header("Tata Penamaan Senyawa Organik")
    compound_name = st.text_input("Masukkan nama senyawa organik (IUPAC atau Trivial):")
    
    if st.button("Mulai"):
        try:
            compound = pcp.get_compounds(compound_name, 'name')[0]
            smiles = compound.isomeric_smiles

            st.image(draw_molecule(smiles), caption="Rumus Struktur Senyawa")
            st.write(f"Berat Molekul: {compound.molecular_weight} g/mol")
            st.write(f"Titik Didih: {compound.boiling_point} °C")
            st.write(f"Sifat Bahan: {compound.properties}")
            st.write(f"Reaktivitas: {compound.reactivity}")

            reaction_input = st.text_input("Senyawa lain untuk reaksi:")
            if st.button("Reaksikan"):
                # Placeholder for reaction logic
                # Introduce hypothetical reaction handling here
                st.write("Hasil reaksi senyawa...")
                st.image(draw_molecule(smiles), caption="Rumus Struktur Reaksi")

                # Display additional info for product
                # You would need to obtain new compound data here
                st.write(f"Berat Molekul produk: ...")
                st.write(f"Titik Didih produk: ...")
                st.write(f"Penamaan baru: ...")
                st.write("Jelaskan reaksi yang terjadi ...")

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

elif option == "Latihan Soal":
    st.header("Latihan Soal: Tebak Rumus Struktur")
    
    questions = [
        {"structure": "C1=CC=CC=C1", "answer": "Benzena"},  # Example: Cyclohexane
        # Add more questions here
    ]
    
    for index, question in enumerate(questions):
        st.image(draw_molecule(question["structure"]), caption=f"Soal {index + 1}")
        user_answer = st.text_input(f"Jawaban Anda untuk soal {index + 1}:")
        
        if st.button(f"Periksa Jawaban Soal {index + 1}"):
            if user_answer.lower() == question["answer"].lower():
                st.success("Benar!")
            else:
                st.error(f"Salah! Jawaban benar adalah: {question['answer']}")
                
    st.button("Lanjutkan ke soal berikutnya...")
