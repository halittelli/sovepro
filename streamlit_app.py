import streamlit as st
import requests
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Evimde Gör - Test Modu", page_icon="🏠", layout="wide")
st.markdown("<h1 style='text-align: center;'>🏠 Evimde Gör: Ücretsiz Test</h1>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    # Hugging Face Token'ını buraya girmen gerekiyor
    hf_token = st.text_input("Hugging Face Token (HF_...)", type="password")
    st.info("Ücretsiz test için Hugging Face Token gereklidir.")

# --- ARAYÜZ ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("Binanın fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🏠 Söve Seçimi")
    # GitHub'daki dosya isimlerine tam uyumlu liste
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Söve Modelini Seçin", tc_codes)
    
    # GitHub'dan görsel referansı (Ekran görüntündeki konuma göre ayarlandı)
    repo_url = "https://raw.githubusercontent.com/halitelli/sovepro/main"
    preview_url = f"{repo_url}/{selected_code}.png"
    
    st.image(preview_url, caption=f"Seçilen Model: {selected_code}", use_container_width=True)

# --- ÜCRETSİZ MOTOR (HF INFERENCE) ---
def run_test(image_bytes, instruction, token):
    API_URL = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "inputs": instruction,
        "image": image_bytes,
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
        st.error(f"Hata Kodu: {response.status_code} - {response.text}")
        return None

# --- İŞLEM ---
if st.button("🚀 Söveyi Binaya Giydirmeyi Dene", type="primary", use_container_width=True):
    if not building_file or not hf_token:
        st.error("Lütfen fotoğraf yükleyin ve HF Token girin!")
    else:
        with st.spinner("Ücretsiz model pencereleri analiz ediyor..."):
            try:
                img_data = building_file.getvalue()
                # Talimatı net veriyoruz
                prompt = f"add white architectural {selected_code} window frames to all windows of this building"
                
                result = run_test(img_data, prompt, hf_token)
                
                if result:
                    st.success("✅ Test tamamlandı!")
                    st.image(result, caption="AI Uygulama Sonucu", use_container_width=True)
            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.divider()
st.caption("Evimde Gör v7.1 | GitHub Entegrasyonu Hazır")
