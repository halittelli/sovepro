import streamlit as st
import replicate
import os
import requests
from PIL import Image
from io import BytesIO

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Evimde Gör PRO", page_icon="🏠", layout="wide")

# --- GÜVENLİK VE API AYARI ---
with st.sidebar:
    st.header("🔑 Pro Bağlantı")
    replicate_api_token = st.text_input("Replicate API Token giriniz:", type="password")
    if replicate_api_token:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
        st.success("Bağlantı Başarılı!")
    else:
        st.warning("Lütfen API Token giriniz.")

st.title("🏠 Evimde Gör: Akıllı Söve Katalog Sistemi")
st.markdown("---")

# --- ARAYÜZ ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    uploaded_file = st.file_uploader("Binanın yüksek çözünürlüklü fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uygulama Yapılacak Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🛠️ Model Kütüphanesi")
    
    # Söve kodlarını oluştur (TC001 - TC024)
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    
    # Seçim Kutusu
    selected_code = st.selectbox("Uygulanacak Söve Modelini Seçin", tc_codes, index=0)
    
    # --- ANLIK ÖN İZLEME BÖLÜMÜ ---
    # Seçim yapıldığı anda (açılır liste kapandığında) görsel burada belirir
    st.markdown(f"**Seçilen Model Ön İzlemesi:** `{selected_code}`")
    
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    
    try:
        # Görseli çekip gösteriyoruz
        response = requests.get(preview_url)
        if response.status_code == 200:
            st.image(preview_url, caption=f"Model: {selected_code} (Kesit Görünümü)", width=300)
        else:
            st.error("Model görseli kütüphanede bulunamadı.")
    except:
        st.warning("Görsel yüklenirken bir sorun oluştu.")

st.markdown("---")

# --- PRO İŞLEMCİ (SDXL CANNY) ---
if st.button("🚀 Seçili Söveyi Binaya Giydir", type="primary", use_container_width=True):
    if not uploaded_file or not replicate_api_token:
        st.error("Eksik bilgi: Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner(f"AI İşleniyor: {selected_code} modeli binaya uyarlanıyor..."):
            try:
                # Replicate Resmi SDXL Canny Modeli
                model_name = "replicate/sdxl-controlnet-canny:da770d1033f9e8a7199416a246835be293526da25701a57e335532588b39447d"
                
                # Talimat (Prompt)
                prompt = (f"professional architectural photography of a building facade, "
                          f"windows are decorated with white {selected_code} architectural moldings, "
                          f"high quality, clean sharp design, detailed texture, realistic shadows")
                
                negative_prompt = "cartoon, drawing, anime, low quality, distorted, messy windows, colorful frames"

                # Replicate Çalıştır
                output = replicate.run(
                    model_name,
                    input={
                        "image": uploaded_file,
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "condition_scale": 0.8,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                )

                if output:
                    st.success(f"✅ {selected_code} Modeli Başarıyla Uygulandı!")
                    result_url = output[0] if isinstance(output, list) else output
                    
                    # Sonucu yan yana karşılaştırmalı göstermek istersen bir düzen daha eklenebilir
                    st.image(result_url, caption="AI Uygulama Sonucu", use_container_width=True)
                    
                    # İndirme Seçeneği
                    img_res = requests.get(result_url)
                    st.download_button("📥 Tasarımı Kaydet (PNG)", data=img_res.content, file_name=f"{selected_code}_tasarim.png")

            except Exception as e:
                st.error(f"Teknik bir hata oluştu: {str(e)}")

st.divider()
st.caption("Evimde Gör v8.2 PRO - Katalog Ön İzleme Modülü Aktif | Halit Telli")
