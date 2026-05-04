import streamlit as st
import requests
import base64
import os

VERSION = "v3.3 - HF Stabil"

st.set_page_config(page_title="Evimde Gör", page_icon="🏠", layout="wide")

st.markdown("<h1 style='text-align: center; margin-bottom: 8px;'>Evimde Gör</h1>", unsafe_allow_html=True)
st.caption(f"<p style='text-align: center; color: #555;'>Versiyon: {VERSION}</p>", unsafe_allow_html=True)

HF_TOKEN = os.getenv("HF_TOKEN")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG, PNG veya WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, use_container_width=True)

with col2:
    st.subheader("📚 ÜRÜNLER")
    tc_codes = (
        [f"TC{i:03d}" for i in range(1, 25)] + 
        [f"TC{i:03d}" for i in range(35, 41)]
    )
    selected_code = st.selectbox("Söve Kodunu Seçin", tc_codes)

    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"{selected_code} - Gerçek Ürün", use_container_width=True)

if st.button("🔥 Sonucu Gör", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Bina fotoğrafı yükleyin!")
    elif not HF_TOKEN:
        st.error("❌ HF_TOKEN bulunamadı.")
    else:
        with st.spinner("Ücretsiz model çalışıyor... (50-90 saniye)"):
            try:
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"Bu binadaki tüm pencerelere {selected_code} kodlu Sovetalya XPS söve yerleştir. Gerçekçi, profesyonel mimari render."

                API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "height": 1024,
                        "width": 1024,
                        "num_inference_steps": 20
                    }
                }

                response = requests.post(API_URL, headers=headers, json=payload)

                if response.status_code == 200:
                    st.success("✅ İşlem tamamlandı!")
                    st.image(response.content, caption="Sonuç", use_container_width=True)
                    st.download_button("📥 İndir", response.content, f"sove_{selected_code}.jpg", "image/jpeg")
                else:
                    st.error(f"API Hatası {response.status_code}: {response.text[:400]}")

            except Exception as e:
                st.error(f"Genel Hata: {str(e)}")

st.caption(f"Versiyon: {VERSION}")
