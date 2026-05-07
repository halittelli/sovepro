import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Evimde Gör PRO", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 Pro Bağlantı")
    # Önceki hatayı önlemek için input alanını temiz tutalım
    replicate_api_token = st.text_input("Yeni Replicate API Token giriniz:", type="password")
    if replicate_api_token:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token.strip() # Boşlukları otomatik siler
        st.success("Yeni bağlantı kuruldu!")

st.title("🏠 Evimde Gör: Profesyonel Söve Uygulaması")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    uploaded_file = st.file_uploader("Fotoğraf yükle", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)

with col2:
    st.subheader("🛠️ Model Seçimi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Söve Seçin", tc_codes)
    
    # Kütüphane linkini halittelli olarak sabitledik
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    try:
        if requests.get(preview_url).status_code == 200:
            st.image(preview_url, width=250)
    except: pass

st.markdown("---")

if st.button("🚀 Söveyi Uygula", type="primary", use_container_width=True):
    if not uploaded_file or not replicate_api_token:
        st.error("Eksik bilgi!")
    else:
        with st.spinner("AI İşlem Yapıyor..."):
            try:
                # BU SEFER REPLICATE'İN RESMİ VE EN GÜNCEL SDXL-CANNY MODELİNİ KULLANIYORUZ
                # Bu model 'official' olduğu için 422 hatası alma ihtimalimiz en düşüktür.
                output = replicate.run(
                    "replicate/sdxl-controlnet-canny:da770d1033f9e8a7199416a246835be293526da25701a57e335532588b39447d",
                    input={
                        "image": uploaded_file,
                        "prompt": f"Professional real estate photography of a building, white {selected_code} window moldings, sharp edges, architectural detail, white stone texture",
                        "negative_prompt": "blurry, lowres, bad anatomy, worst quality, artifacts",
                        "condition_scale": 0.85,
                        "num_inference_steps": 30
                    }
                )

                if output:
                    st.success("Başarılı!")
                    res_url = output[0] if isinstance(output, list) else output
                    st.image(res_url, use_container_width=True)
                    st.download_button("Kaydet", requests.get(res_url).content, file_name="tasarim.png")

            except Exception as e:
                # Hata mesajını tam olarak görelim
                st.error(f"Hata Detayı: {str(e)}")
                if "422" in str(e):
                    st.warning("Hala 422 alıyorsan: Replicate web sitesinde bir kez bu modeli çalıştırıp şartları kabul etmelisin.")
