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

st.title("🏠 Evimde Gör: Akıllı Söve Uygulaması")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# --- SOL SÜTUN: BİNA FOTOĞRAFI ---
with col1:
    st.subheader("📸 Bina Analizi")
    uploaded_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Orijinal Cephe", use_container_width=True)

# --- SAĞ SÜTUN: KATALOG ---
with col2:
    st.subheader("🛠️ Söve Modeli")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Model Seçin", tc_codes)
    
    # GitHub Görseli (halittelli - çift t)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    try:
        if requests.get(preview_url).status_code == 200:
            st.image(preview_url, caption=f"Katalog: {selected_code}", width=250)
    except:
        st.warning("Görsel yüklenemedi.")

st.markdown("---")

if st.button("🚀 Söveyi Uygula", type="primary", use_container_width=True):
    if not uploaded_file or not api_token:
        st.error("Lütfen fotoğraf ve API Token bilgilerini eksiksiz girin!")
    else:
        with st.spinner("Yapay zeka binayı analiz edip söveleri yerleştiriyor..."):
            try:
                # PAYLAŞTIĞIN SNIPPET'TEKİ KESİN VERSİYON KODU (06d6fae3...):
                model_version = "lucataco/sdxl-controlnet:06d6fae3b75ab68a28cd2900afa6033166910dd09fd9751047043a5bbb4c184b"
                
                # Sadece modelin kesinlikle tanıdığı parametreleri gönderiyoruz:
                output = replicate.run(
                    model_version,
                    input={
                        "image": uploaded_file,
                        "prompt": f"professional architectural photography of a building facade, windows are decorated with white architectural {selected_code} moldings, realistic white stone texture, 8k resolution, clean design",
                        "negative_prompt": "cartoon, blurry, low quality, distorted windows, colorful frames",
                        "controlnet_conditioning_scale": 0.8,
                        "num_inference_steps": 30
                    }
                )

                if output:
                    st.success("✅ Tasarım Başarıyla Tamamlandı!")
                    res_url = output[0] if isinstance(output, list) else output
                    st.image(res_url, caption=f"Sonuç: {selected_code} Uygulaması", use_container_width=True)
                    
                    st.download_button("📥 Sonucu Bilgisayara Kaydet", 
                                     data=requests.get(res_url).content, 
                                     file_name=f"{selected_code}_sove_tasarim.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")
                st.info("Eğer hala 422 alıyorsak, 'prompt' kelimesini koddaki input listesinden geçici olarak çıkarıp sadece 'image' ile deneyeceğiz.")

st.divider()
st.caption("Sovetalya v12.0 PRO | Halit Telli | Architectural AI Solutions")
