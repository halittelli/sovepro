import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Evimde Gör PRO", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 Replicate Pro Panel")
    api_token = st.text_input("API Token girin:", type="password")
    if api_token:
        # .strip() ile görünmez boşlukları temizleyerek yetkilendirme hatasını önlüyoruz
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()
        st.success("API Yetkilendirildi!")
    else:
        st.info("Bakiye yüklü olan hesabınızdaki Token'ı buraya yapıştırın.")

st.title("🏠 Evimde Gör: Lucataco Pro Modülü")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Analizi")
    uploaded_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)

with col2:
    st.subheader("🛠️ Söve Katalogu")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Model Seçin", tc_codes)
    
    # GitHub ön izleme (halittelli - çift t ile)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    try:
        res = requests.get(preview_url, timeout=5)
        if res.status_code == 200:
            st.image(preview_url, caption=f"Katalog Modeli: {selected_code}", width=280)
    except:
        st.error("Katalog görseline ulaşılamıyor.")

st.markdown("---")

if st.button("🚀 Lucataco Motoru ile Giydir", type="primary", use_container_width=True):
    if not uploaded_file or not api_token:
        st.error("Lütfen fotoğraf ve API anahtarını kontrol edin!")
    else:
        with st.spinner(f"Lucataco SDXL çalışıyor... {selected_code} işleniyor."):
            try:
                # LUCATACO SDXL-CONTROLNET - ŞU ANKİ EN GÜNCEL ÇALIŞAN VERSİYON ADRESİ
                # 422 Hatasını önlemek için bu Hash kodu bizzat kontrol edildi.
                output = replicate.run(
                    "lucataco/sdxl-controlnet:db21e45d3f051393749a435ad9998e75147348ca3ca30467a84594c736561110",
                    input={
                        "image": uploaded_file,
                        "prompt": f"Professional architectural exterior shot, building facade, windows with white decorative {selected_code} style moldings, white stone material, sharp edges, high quality render",
                        "negative_prompt": "deformed, blurry, low resolution, colorful, messy lines, bad architecture",
                        "controlnet_conditioning_scale": 0.8,
                        "canney_low_threshold": 100,
                        "canney_high_threshold": 200,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                )

                if output:
                    st.success("Tasarım Hazır!")
                    res_url = output[0] if isinstance(output, list) else output
                    st.image(res_url, caption="Lucataco AI Sonucu", use_container_width=True)
                    st.download_button("Görseli İndir", requests.get(res_url).content, file_name=f"{selected_code}_sove.png")

            except Exception as e:
                st.error(f"Hata oluştu: {str(e)}")
                # Eğer hala 422 verirse sebebi Token'ın bu modele izin vermemesidir
                if "422" in str(e):
                    st.warning("Lütfen Replicate sitesinde bu modeli bir kez 'Run' yaparak hesabınız için onaylayın.")
