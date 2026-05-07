import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya Cerrahi Müdahale v14.0", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Bağlantısı")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()
        st.success("Yetkilendirildi!")

st.title("🏠 Sovetalya: Cerrahi Söve Uygulaması")
st.warning("Bu sürüm, sadece söveyi pencerelere eklemeye odaklanır ve binayı korumaya çalışır.")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Analizi")
    uploaded_file = st.file_uploader("Fotoğraf yükle", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Orijinal Cephe", use_container_width=True)

with col2:
    st.subheader("🛠️ Katalog")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Söve Seç", tc_codes)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    try:
        if requests.get(preview_url).status_code == 200:
            st.image(preview_url, caption=f"Model: {selected_code}", width=250)
    except:
        st.warning("Görsel yüklenemedi.")

st.markdown("---")

if st.button("🚀 Söveyi Uygula (Maksimum Hassasiyet)", type="primary", use_container_width=True):
    if not uploaded_file or not api_token:
        st.error("Lütfen fotoğraf ve API Token girin!")
    else:
        with st.spinner(f"Cerrahi müdahale yapılıyor: Binanın her yeri korunarak sadece pencerelere {selected_code} sövesi ekleniyor..."):
            try:
                # JS kodundaki çalışan ID
                model_version = "lucataco/sdxl-controlnet:06d6fae3b75ab68a28cd2900afa6033166910dd09fd9751047043a5bbb4c184b"
                
                # --- KRİTİK GÜÇLENDİRİLMİŞ PROMPT ---
                # "PERFECTLY PRESERVED", "ALL architectural details remain identical", "UNTOUCHED" gibi sert ifadeler kullandık.
                strong_prompt = (
                    f"Professional architectural photography of a building. "
                    f"The original building facade is PERFECTLY PRESERVED. ALL architectural details, textures, colors, and structure remain identical to the source. "
                    f"Only the window frames have been surgically modified to precisely include the specific {selected_code} decorative molding design. "
                    f"The new moldings are white stone texture and applied exclusively to the window perimeters. "
                    f"No other part of the building is changed, untouched and unchanged. realistic, 8k resolution, clean design."
                )
                
                # Yasaklı kelimeleri arttırdık
                strong_negative_prompt = (
                    "change, alteration, color change, new texture, modernizing, removing details, cartoon, drawing, painting, blurry, artifacts, colorful, distorted windows, messy facade"
                )

                output = replicate.run(
                    model_version,
                    input={
                        "image": uploaded_file,
                        "prompt": strong_prompt,
                        "negative_prompt": strong_negative_prompt,
                        # Binayı korumak için maksima yakın hassasiyet
                        "controlnet_conditioning_scale": 0.95,
                        # Daha fazla adım, daha fazla detay
                        "num_inference_steps": 50,
                        # Prompt'u dinlemesi için yüksek zorlama
                        "guidance_scale": 12.0
                    }
                )

                if output:
                    st.success("✅ İşlem Tamamlandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption=f"Sonuç: {selected_code} Uygulaması", use_container_width=True)
                    st.download_button("📥 Sonucu Kaydet", requests.get(res_url).content, file_name="tasarim.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")

st.caption("Sovetalya v14.0 | Cerrahi Müdahale Sürümü")
