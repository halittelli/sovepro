import streamlit as st
import replicate
import os
import requests
from PIL import Image
from io import BytesIO

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Evimde Gör PRO", page_icon="🏢", layout="wide")

# --- GÜVENLİK VE API AYARI ---
# API Key'i doğrudan koda yazmıyoruz, sidebar'dan alıyoruz (Güvenlik için)
with st.sidebar:
    st.header("🔑 Pro Bağlantı")
    replicate_api_token = st.text_input("Replicate API Token giriniz:", type="password")
    if replicate_api_token:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
        st.success("Bağlantı Başarılı!")
    else:
        st.warning("Lütfen API Token giriniz.")

st.title("🏢 Evimde Gör: Profesyonel Söve Uygulaması")
st.markdown("---")

# --- ARAYÜZ ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    uploaded_file = st.file_uploader("Binanın yüksek çözünürlüklü fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🛠️ Söve Seçimi")
    # GitHub'daki resim listene göre ayarlandı
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Uygulanacak Söve Modelini Seçin", tc_codes)
    
    # GitHub'dan önizleme
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Seçilen Model: {selected_code}", width=200)

# --- PRO İŞLEMCİ (REPLICATE SDXL CANNY) ---
if st.button("🚀 Söveyi Binaya Giydir (Profesyonel İşlem)", type="primary", use_container_width=True):
    if not uploaded_file or not replicate_api_token:
        st.error("Lütfen önce bina fotoğrafını yükleyin ve API Token'ı girin!")
    else:
        with st.spinner("AI Analiz Yapıyor: Pencereler tespit ediliyor ve söveler yerleştiriliyor..."):
            try:
                # 1. Fotoğrafı Replicate'e gönderilecek formata hazırla
                # SDXL Canny Modeli (En stabil ve kaliteli olanlardan biri)
                model_version = "lucataco/sdxl-controlnet:db21e45d3f051393749a435ad9998e75147348ca3ca30467a84594c736561110"
                
                # 2. AI Talimatı (Prompt)
                # Senin söve modelini ve beyaz rengi vurguluyoruz
                prompt = (f"Ultra-realistic architectural photography of a building. "
                          f"The windows are decorated with thick white decorative {selected_code} style window moldings. "
                          f"High quality exterior design, clean lines, professional construction.")
                
                negative_prompt = "distorted, blurry, low quality, deformed windows, messy colors, messy architecture"

                # 3. Replicate Çalıştır
                output = replicate.run(
                    model_version,
                    input={
                        "image": uploaded_file,
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "controlnet_conditioning_scale": 0.8, # Binayı ne kadar koruyacağı (0.8 idealdir)
                        "canney_low_threshold": 100,
                        "canney_high_threshold": 200,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                )

                # 4. Sonucu Göster
                if output:
                    st.success("✅ İşlem Tamamlandı!")
                    # Replicate genellikle bir liste döner
                    result_url = output[0] if isinstance(output, list) else output
                    st.image(result_url, caption=f"Uygulanan Söve: {selected_code}", use_container_width=True)
                    
                    # İndirme butonu
                    img_res = requests.get(result_url)
                    st.download_button("📥 Sonucu İndir", data=img_res.content, file_name=f"{selected_code}_uygulama.png")

            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")

st.divider()
st.caption("Evimde Gör v8.0 PRO | Powered by Replicate & SDXL")
