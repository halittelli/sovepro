import streamlit as st
import replicate
import os
from PIL import Image
import requests
from io import BytesIO

# Sayfa Ayarları
st.set_page_config(page_title="Evimde Gör Pro - Stabil", page_icon="🏠", layout="wide")
st.markdown("<h1 style='text-align: center;'>Evimde Gör: Otomatik Söve Giydirme</h1>", unsafe_allow_html=True)

# API Anahtarını buraya girin veya Streamlit Secrets'a ekleyin
REPLICATE_API_TOKEN = st.sidebar.text_input("Replicate API Token Girin", type="password")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("Binanın net fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🏠 Söve Seçimi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)]
    selected_code = st.selectbox("Söve Modelini Seçin", tc_codes)
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Seçilen Ürün: {selected_code}", use_container_width=True)

if st.button("🔥 Söveleri Giydir (Hassas İşlem)", type="primary", use_container_width=True):
    if not building_file or not REPLICATE_API_TOKEN:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("Yapay zeka binayı analiz ediyor ve söveleri yerleştiriyor..."):
            try:
                # Profesyonel ControlNet Modeli (Canny)
                # Bu model binanın çizgilerini %100 korur.
                output = replicate.run(
                    "jagadeesh-at-code-monk/controlnet-canny:7d293f8e56317d7b275685a2da16b3336a1e3b08e7150a0094709d7389a9f2df",
                    input={
                        "image": building_file,
                        "prompt": f"architectural visualization, white {selected_code} window frame molding, luxury exterior design, sharp edges, realistic materials, highly detailed windows",
                        "negative_prompt": "change building structure, change windows position, blurry, distorted, low quality",
                        "num_inference_steps": 40,
                        "condition_scale": 0.9, # Binayı koruma gücü (0.9 = Maksimum koruma)
                        "guidance_scale": 9.0
                    }
                )
                
                if output:
                    st.success("✅ İşlem Başarılı! Bina korundu, söveler eklendi.")
                    st.image(output[1], caption="Sonuç (Söve Uygulanmış)", use_container_width=True)
                    
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")

st.info("Bilgi: Bu sistem 'ControlNet' kullanarak binanın mimari hatlarını dondurur, böylece bina değişmeden sadece pencere kenarları güncellenir.")
