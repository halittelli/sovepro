import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya PRO", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 Replicate Bağlantısı")
    api_token = st.text_input("API Token giriniz:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()
        st.success("API Yetkilendirildi!")

st.title("🏠 Evimde Gör: Profesyonel Söve Uygulaması")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Analizi")
    uploaded_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Orijinal Cephe", use_container_width=True)

with col2:
    st.subheader("🛠️ Söve Modeli")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Model Seçin", tc_codes)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    try:
        if requests.get(preview_url).status_code == 200:
            st.image(preview_url, caption=f"Katalog: {selected_code}", width=250)
    except:
        st.warning("Görsel yüklenemedi.")

st.markdown("---")

if st.button("🚀 Söveyi Uygula", type="primary", use_container_width=True):
    if not uploaded_file or not api_token:
        st.error("Lütfen fotoğraf ve API Token bilgilerini girin!")
    else:
        with st.spinner("AI Motoru çalışıyor, görsel oluşturuluyor..."):
            try:
                # Paylaştığın JS kodundaki çalışan kesin ID
                model_version = "lucataco/sdxl-controlnet:06d6fae3b75ab68a28cd2900afa6033166910dd09fd9751047043a5bbb4c184b"
                
                output = replicate.run(
                    model_version,
                    input={
                        "image": uploaded_file,
                        "prompt": f"professional architectural photography, white {selected_code} moldings on windows, realistic facade, 8k",
                        "negative_prompt": "cartoon, blurry, low quality, distorted",
                        "controlnet_conditioning_scale": 0.8
                    }
                )

                if output:
                    st.success("✅ İşlem Başarılı!")
                    
                    # --- HATA DÜZELTME NOKTASI ---
                    # Çıktıyı (FileOutput objesini) string linkine dönüştürüyoruz
                    if isinstance(output, list):
                        res_url = str(output[0])
                    else:
                        res_url = str(output)
                    
                    # Artık Streamlit bu linki (string) sorunsuzca okuyabilir
                    st.image(res_url, caption=f"Sonuç: {selected_code} Uygulaması", use_container_width=True)
                    
                    # İndirme işlemi
                    img_data = requests.get(res_url).content
                    st.download_button("📥 Sonucu Kaydet", data=img_data, file_name=f"{selected_code}_tasarim.png")

            except Exception as e:
                st.error(f"Teknik hata: {str(e)}")

st.caption("Sovetalya v13.0 | Halit Telli")
