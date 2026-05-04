import streamlit as st
import requests
import base64
from io import BytesIO

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Evimde Gör - Ücretsiz Test", page_icon="🏠", layout="wide")
st.markdown("<h1 style='text-align: center;'>🏠 Evimde Gör: Ücretsiz Test Modu</h1>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    hf_token = st.text_input("Hugging Face Token (HF_...)", type="password")
    st.info("Ücretsiz test için Hugging Face 'Access Token' gereklidir.")

# --- ARAYÜZ ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("Binanın fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🏠 Söve Seçimi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Söve Modelini Seçin", tc_codes)
    
    # GitHub'daki görselini referans alıyoruz
    repo_url = "https://raw.githubusercontent.com/halitelli/sovepro/main"
    preview_url = f"{repo_url}/{selected_code}.png"
    st.image(preview_url, caption=f"Seçilen Model: {selected_code}", use_container_width=True)

# --- ÜCRETSİZ MOTOR FONKSİYONU ---
def query_pix2pix(image_file, prompt, token):
    # Bu model görsel düzenleme için en iyi ücretsiz seçenektir
    API_URL = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Görseli base64 formatına çeviriyoruz (JSON hatasını bu çözer)
    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    payload = {
        "inputs": prompt,
        "image": encoded_image,
        "parameters": {
            "num_inference_steps": 20,
            "image_guidance_scale": 1.5,
            "guidance_scale": 7.5
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"API Hatası ({response.status_code}): {response.text}")
        return None

# --- İŞLEM ---
if st.button("🚀 Ücretsiz Söve Giydirmeyi Dene", type="primary", use_container_width=True):
    if not building_file or not hf_token:
        st.error("Lütfen fotoğraf yükleyin ve Hugging Face Token girin!")
    else:
        with st.spinner("Yapay zeka pencereleri analiz ediyor..."):
            try:
                # Görseli en başa sar (okunabilir olması için)
                building_file.seek(0)
                
                # Talimat: 'Pencere kenarlarına beyaz söve ekle'
                instruction = f"add white architectural {selected_code} style window moldings to all windows of this building. keep the building original."
                
                result = query_pix2pix(building_file, instruction, hf_token)
                
                if result:
                    st.success("✅ Test tamamlandı!")
                    st.image(result, caption="AI Uygulama Sonucu (Ücretsiz Model)", use_container_width=True)
                    st.info("Not: Bu ücretsiz bir modeldir. Profesyonel ve binayı hiç bozmayan sonuç için bakiye yükleyip Replicate (ControlNet) motoruna geçeceğiz.")
            except Exception as e:
                st.error(f"Hata oluştu: {str(e)}")

st.divider()
st.caption("Evimde Gör v7.2 - Freelance 3D Artist Halit Telli")
