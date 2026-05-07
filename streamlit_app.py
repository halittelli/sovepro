import streamlit as st
import replicate
import os
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Sovetalya v23.0 - Auto Engine", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: Tam Otomatik Mimari Giydirme")
st.caption("Grok-Imagine Algoritması ile Bina Dokusunu Koruma")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe Fotoğrafı", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina (Korunacak)", use_container_width=True)

with col2:
    st.subheader("📚 Söve Modeli")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Söve Seçin", tc_codes)
    
    # Görüntülediğimiz ekran görüntüsüne göre kesinleşen URL
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Uygulanacak Model: {selected_code}", width=250)

st.divider()

if st.button("🚀 OTOMATİK SÖVE GİYDİR", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf ve token girin!")
    else:
        with st.spinner("Grok motoru hassasiyetinde analiz ediliyor..."):
            try:
                # Binayı KORUYAN ve sadece söveyi EKLEYEN matematiksel ayarlar
                version_id = "06d6fae3b75ab68a28cd2900afa6033166910dd09fd9751047043a5bbb4c184b"
                
                output = replicate.run(
                    f"lucataco/sdxl-controlnet:{version_id}",
                    input={
                        "image": building_file,
                        # Prompt: Binayı olduğu gibi bırak, sadece pencerelere bu görseldeki söveyi ekle
                        "prompt": f"Architectural photo. KEEP THE ORIGINAL BUILDING EXACTLY AS IT IS. Add only white {selected_code} style architectural window moldings around every window. The moldings must look like {preview_url}. No wall changes, no texture changes. Realistic lighting and shadows.",
                        "negative_prompt": "changing wall texture, changing building color, modernizing building, removing construction details, different windows",
                        "num_inference_steps": 40,
                        "guidance_scale": 8.0,
                        # Binanın orijinal hattını %100 korumak için scale değerini artırdık
                        "controlnet_conditioning_scale": 0.95 
                    }
                )

                if output:
                    st.success("✅ Otomatik Giydirme Tamamlandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Uygulama", use_container_width=True)
                    
                    st.download_button("📥 Tasarımı Kaydet", requests.get(res_url).content, file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.caption("Sovetalya v23.0 | Otomatik Perspektif ve Doku Koruma")
