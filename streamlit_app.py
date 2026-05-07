import streamlit as st
import replicate
import os
import requests
from io import BytesIO

# Sayfa Ayarı
st.set_page_config(page_title="Sovetalya Tanı Modülü", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    token = st.text_input("Replicate Token (r8_ ile başlamalı):", type="password")
    if token:
        os.environ["REPLICATE_API_TOKEN"] = token.strip()

st.title("🏠 Sovetalya: Hata Ayıklama ve Uygulama")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Bina Fotoğrafı Seç", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Yüklenen Dosya", use_container_width=True)

with col2:
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)]
    model_choice = st.selectbox("Söve Modeli", tc_codes)
    # GitHub'dan görsel çekme (halittelli - çift t)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{model_choice}.png"
    st.image(preview_url, width=200)

st.divider()

if st.button("🚀 AI Motorunu Test Et ve Uygula"):
    if not uploaded_file or not token:
        st.error("Lütfen fotoğraf ve token bilgilerini girin.")
    else:
        with st.spinner("Sistem analiz ediliyor..."):
            try:
                # STRATEJİ: Dosyayı Bytes olarak oku (En güvenli yol)
                file_bytes = uploaded_file.getvalue()
                
                # REPLICATE RESMİ SDXL-CANNY (Versiyon kodu içermeyen en stabil yol)
                # Bu çağırma yöntemi her zaman en güncel çalışan versiyona gider.
                model_name = "lucataco/sdxl-controlnet"
                
                output = replicate.run(
                    model_name,
                    input={
                        "image": BytesIO(file_bytes), # Dosyayı ham haliyle gönderiyoruz
                        "prompt": f"Professional architectural exterior, house facade, windows with white {model_choice} moldings, realistic white stone, photorealistic, 8k",
                        "negative_prompt": "cartoon, blur, low quality, distorted, messy",
                        "controlnet_conditioning_scale": 0.8,
                        "num_inference_steps": 25,
                        "guidance_scale": 7.5
                    }
                )

                if output:
                    st.success("BAŞARILI!")
                    st.image(output[0] if isinstance(output, list) else output)
            
            except Exception as e:
                # Hata 422 ise, detaylarını parçalayarak gösterelim
                st.error("⚠️ KRİTİK HATA TESPİT EDİLDİ")
                st.write(f"Hata Mesajı: {str(e)}")
                
                # Teknik Detay Analizi
                if "422" in str(e):
                    st.info("Teşhis: Gönderilen parametrelerden biri (image, prompt vb.) model tarafından reddedildi.")
                    st.warning("Çözüm Önerisi: Replicate panelinden 'API' sekmesine bakıp, parametre isimlerinin değişip değişmediğini kontrol ediyoruz.")

st.caption("Sovetalya v11.0 | Halit Telli")
