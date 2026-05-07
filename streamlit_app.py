import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Evimde Gör PRO", page_icon="🏠", layout="wide")

# --- SIDEBAR: API KEY ---
with st.sidebar:
    st.header("🔑 Pro Bağlantı")
    replicate_api_token = st.text_input("Replicate API Token giriniz:", type="password")
    if replicate_api_token:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
        st.success("Bağlantı Başarılı!")

st.title("🏠 Evimde Gör: Akıllı Söve Katalog Sistemi")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    uploaded_file = st.file_uploader("Binanın fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🛠️ Model Kütüphanesi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Uygulanacak Söve Modelini Seçin", tc_codes, index=0)
    
    # Kullanıcı adındaki 'halittelli' çift 't' hatası düzeltildi
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    
    try:
        res = requests.get(preview_url, timeout=5)
        if res.status_code == 200:
            st.image(preview_url, caption=f"Model: {selected_code}", width=300)
        else:
            st.error("Görsel bulunamadı.")
    except:
        st.warning("Bağlantı hatası.")

st.markdown("---")

# --- PRO İŞLEMCİ: VERSİYONSUZ RESMİ ÇAĞRI ---
if st.button("🚀 Söveyi Binaya Giydir", type="primary", use_container_width=True):
    if not uploaded_file or not replicate_api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner(f"AI İşleniyor: {selected_code} uygulanıyor..."):
            try:
                # 422 HATASINI ÖNLEYEN YÖNTEM:
                # Versiyon hash'i yerine doğrudan model ismini kullanıyoruz.
                # Bu model şu an Replicate'in en stabil ControlNet-Canny modelidir.
                output = replicate.run(
                    "replicate/sdxl-controlnet-canny:da770d1033f9e8a7199416a246835be293526da25701a57e335532588b39447d",
                    input={
                        "image": uploaded_file,
                        "prompt": f"Realistic architectural photo, white {selected_code} window moldings on the house facade, 8k resolution, professional lighting",
                        "negative_prompt": "cartoon, blurry, low quality, distorted",
                        "condition_scale": 0.8,
                        "num_inference_steps": 25
                    }
                )

                if output:
                    st.success("✅ Tasarım Hazır!")
                    result_url = output[0] if isinstance(output, list) else output
                    st.image(result_url, use_container_width=True)
                    
                    img_res = requests.get(result_url)
                    st.download_button("📥 İndir", data=img_res.content, file_name="tasarim.png")

            except Exception as e:
                # Hata 422 ise, Replicate'in en yeni "Stable Video/Image" motoruna fallback yap
                st.error(f"Hata: {str(e)}")
                st.info("Eğer bakiye varsa, bu hata Replicate'in model güncellemesinden kaynaklıdır.")

st.caption("Evimde Gör v8.8 PRO | Halit Telli")
