import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Evimde Gör PRO", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 Replicate Yetkilendirme")
    api_token = st.text_input("API Token girin:", type="password")
    if api_token:
        # Görünmez boşlukları temizleyerek hata riskini sıfıra indiriyoruz
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()
        st.success("API Bağlantısı Aktif!")

st.title("🏠 Evimde Gör: Akıllı Söve Uygulaması")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    uploaded_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🛠️ Söve Seçimi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Model Seçin", tc_codes)
    
    # Katalog Ön İzleme (halittelli - çift t)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    try:
        res = requests.get(preview_url, timeout=5)
        if res.status_code == 200:
            st.image(preview_url, caption=f"Katalog: {selected_code}", width=280)
    except:
        st.warning("Katalog görseli yüklenemedi.")

st.markdown("---")

if st.button("🚀 Söveyi Binaya Uygula", type="primary", use_container_width=True):
    if not uploaded_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner(f"AI Motoru Çalışıyor: {selected_code} pencerelere giydiriliyor..."):
            try:
                # EKRAN GÖRÜNTÜSÜNDEKİ 'LATEST' (EN GÜNCEL) VERSİYON KODU:
                # '06d6fae3...' ile başlayan tam ID kullanılmıştır.
                model_version = "lucataco/sdxl-controlnet:06d6fae3a62866994a53e660ef093a8c62c2e557b4430e79147e4529a6742a"
                
                output = replicate.run(
                    model_version,
                    input={
                        "image": uploaded_file,
                        "prompt": f"High quality architectural photography, a house facade, windows are decorated with white decorative {selected_code} style window moldings, white architectural details, sharp realistic shadows, 8k resolution",
                        "negative_prompt": "blurry, low quality, messy, distorted windows, colors, cartoon, drawing",
                        "controlnet_conditioning_scale": 0.8,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                )

                if output:
                    st.success("✅ Tasarım Tamamlandı!")
                    res_url = output[0] if isinstance(output, list) else output
                    st.image(res_url, caption="AI Uygulama Sonucu", use_container_width=True)
                    
                    # İndirme Seçeneği
                    img_data = requests.get(res_url).content
                    st.download_button("📥 Sonucu İndir", data=img_data, file_name=f"{selected_code}_tasarim.png")

            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")
                st.info("İpucu: Token'ı kopyalarken 'r8_' ile başladığından emin ol.")

st.caption("Evimde Gör v9.2 PRO | Halit Telli")
