import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya Flux PRO", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 Replicate API")
    token = st.text_input("Replicate Token:", type="password")
    if token:
        os.environ["REPLICATE_API_TOKEN"] = token.strip()
        st.success("API Hazır!")

st.title("🏠 Sovetalya: Flux Motoru ile Mimari Giydirme")
st.caption("Grok kalitesinde, yüksek sadakatli söve oturtabilme sistemi.")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("JPG / PNG", type=["jpg", "jpeg", "png"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("📚 Söve Kütüphanesi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)]
    selected_code = st.selectbox("Söve Kodunu Seç", tc_codes)
    
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/sove_images/{selected_code}.png"
    st.image(preview_url, caption=f"Model: {selected_code}", width=250)

st.divider()

if st.button("🔥 SÖVEYİ OTURT (Flux.1 Dev)", type="primary", use_container_width=True):
    if not building_file or not token:
        st.error("Lütfen fotoğraf ve API anahtarını kontrol edin!")
    else:
        with st.spinner("Flux motoru binayı analiz ediyor..."):
            try:
                # --- FLUX GÜCÜ ---
                # 'black-forest-labs/flux-dev' şu an piyasadaki en akıllı modeldir.
                # 'image_to_image' modunu kullanarak binayı korumasını sağlıyoruz.
                
                output = replicate.run(
                    "lucataco/flux-dev-img2img:0a6f6ed668c20177797669460517924614e543666d997d9e79435b5463765103",
                    input={
                        "image": building_file,
                        "prompt": f"Extremely detailed architectural photography of this building. Add white {selected_code} architectural moldings to all windows. The window frames must be decorated with white stone moldings. The original building structure, textures, and wall colors MUST REMAIN IDENTICAL. Only the windows are edited. 8k, highly realistic, professional lighting.",
                        "prompt_strength": 0.45,  # 0.45 binayı %100 korur, söveyi hafifçe işler. Çok değişirse 0.35 yap.
                        "num_inference_steps": 28,
                        "guidance_scale": 3.5
                    }
                )

                if output:
                    st.success("✅ Flux ile mükemmel sonuç üretildi!")
                    # Flux genellikle bir liste döndürür
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Tasarım", use_container_width=True)
                    
                    st.download_button("📥 Tasarımı İndir", 
                                     data=requests.get(res_url).content, 
                                     file_name=f"{selected_code}_tasarim.png")

            except Exception as e:
                st.error(f"Hata: {str(e)}")
                st.info("Eğer hata alırsan, terminale 'pip install --upgrade replicate' yazmayı unutma.")

st.caption("Sovetalya v16.0 | Flux.1-Dev Engine | Halit Telli")
