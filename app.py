import streamlit as st
import re
import time

def clean_text(raw_text):
    """Fungsi untuk membersihkan teks mentah dari media sosial."""
    
    text = raw_text
    
    # 1. Hapus username/mention (Menangkap karakter strip spt @user-u2n)
    text = re.sub(r'@[\w-]+', '', text)
    
    # 2. Hapus UI Spesifik, deskripsi gambar, titik tengah "·", dll
    ui_patterns = [
        r'\bShow (more )?replies\b', 
        r'\bReply\b', 
        r'\bQuote\b', 
        r'\bParody account\b', 
        r'\bCommentary account\b',
        r'\bLihat terjemahan\b',
        r'\bBalas\b',
        r'\bDiedit\b',
        r'Mungkin gambar teks yang menyatakan.*', # Hapus deskripsi alt text gambar
        r'Mungkin berisi.*',                      # Hapus deskripsi alt text gambar lainnya
        r'\(edited\)',
        r'\s*·\s*',          # Menghapus titik tengah (middle dot) beserta spasinya
        r'^\s*\.\s*$',        # Menghapus titik yang berdiri sendirian di satu baris
        r'\bprofile picture\b'
    ]
    for pattern in ui_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
    # 3. Hapus pola waktu/tanggal bahasa Inggris
    text = re.sub(r'\b\d+\s*(h|m|s|w|weeks? ago|days? ago|hours? ago)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d+\b', '', text, flags=re.IGNORECASE)
    
    # 4. Hapus pola waktu/tanggal bahasa Indonesia
    text = re.sub(r'\b\d+\s?(minggu|hari|jam|menit|detik)\b', '', text, flags=re.IGNORECASE)
    
    # 5. Hapus angka tunggal dalam satu baris (seperti jumlah Like/View)
    text = re.sub(r'^\s*\d+(\.\d+[KkMm]?)?\s*$', '', text, flags=re.MULTILINE)
    
    # 6. Hilangkan spasi dan baris kosong (enter) untuk menghemat token
    text = re.sub(r' +', ' ', text)       # Ubah spasi ganda menjadi 1 spasi saja
    text = re.sub(r'\n+', '\n', text)     # Ubah enter berkali-kali menjadi 1 enter saja
    
    return text.strip()


# --- STREAMLIT UI ---
st.set_page_config(page_title="Data Text Cleaner", page_icon="🧹", layout="wide")

st.title("🧹 Pembersih Teks Media Sosial")
st.write("Bersihkan data *scraping* kotor (X/Twitter, YouTube, dll) untuk menghemat token **(Teks padat, Username bersih sempurna, Emotikon dipertahankan)**.")
st.markdown("---")

# Inisialisasi state untuk text area dan tracking file
if 'text_input_area' not in st.session_state:
    st.session_state.text_input_area = ""
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None

# --- FASILITAS UPLOAD FILE ---
uploaded_file = st.file_uploader("📂 Upload file .txt (Opsional, jika file besar)", type=["txt"])

# Deteksi jika ada file baru yang diunggah
if uploaded_file is not None:
    # Hanya menimpa teks jika file yang diupload berbeda/baru (agar tidak mereset editan manual user)
    if st.session_state.last_uploaded_file != uploaded_file.name:
        string_data = uploaded_file.getvalue().decode("utf-8")
        st.session_state.text_input_area = string_data
        st.session_state.last_uploaded_file = uploaded_file.name
        st.success("File berhasil diunggah! Teks telah dimasukkan ke kotak di bawah.")
else:
    # Reset tracking jika file dihapus/disilang
    st.session_state.last_uploaded_file = None

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Teks Mentah (Raw Text)")
    # Menggunakan session_state key secara langsung
    input_text = st.text_area(
        "Masukkan atau edit teks di sini:", 
        height=400, 
        key="text_input_area"
    )
    
    if st.button("🧹 Bersihkan Teks", type="primary", use_container_width=True):
        if input_text:
            with st.spinner('Sedang membersihkan teks dan memadatkan token...'):
                time.sleep(1) 
                cleaned_result = clean_text(input_text)
                st.session_state.cleaned_text = cleaned_result
                
            st.success("Selesai! Teks berhasil dibersihkan dan dipadatkan.")
        else:
            st.warning("Silakan masukkan teks atau upload file terlebih dahulu.")

with col2:
    st.subheader("Hasil Bersih (Cleaned Text)")
    
    if 'cleaned_text' in st.session_state:
        # Kotak ini bisa di-blok (Ctrl+A) dan diedit secara bebas
        st.text_area(
            "Teks yang sudah dibersihkan (Bisa diblok/select & edit manual):", 
            value=st.session_state.cleaned_text, 
            height=300
        )
        
        # Fitur 1-klik copy
        st.markdown("**Atau gunakan fitur 1-Klik Copy di bawah ini (Klik ikon 📋 di pojok kanan atas):**")
        st.code(st.session_state.cleaned_text, language="text")
        
        st.download_button(
            label="⬇️ Download Hasil (.txt)",
            data=st.session_state.cleaned_text,
            file_name="cleaned_text.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.text_area(
            "Teks yang sudah dibersihkan akan muncul di sini.", 
            height=400, 
            disabled=True
        )
