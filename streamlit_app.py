import streamlit as st
import replicate
import os
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Sovetalya v28.0 PRO", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: Profesyonel Mimari Giydirme")
st.caption("Şekil Referanslı Motor (Binayı Koru - Söveyi Kopyala)")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Orijinal Bina")
    building_file = st.file_uploader("Cephe Fotoğrafı", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Korunacak Orijinal Doku", use_container_width=True)

with col2:
    st.subheader("📚 Referans Söve")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Model Seçin", tc_codes)
    
    # Kesinleşen GitHub Linki
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Şekli Kopyalanacak Model: {selected_code}", width=250)

st.divider()

if st.button("🚀 ŞEKLİ REFERANS ALARAK UYGULA", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf ve token girin!")
    else:
        with st.spinner("AI sövenin geometrisini analiz ediyor ve binaya giydiriyor..."):
            try:
                # Bu model, hem binanın hatlarını korur hem de söveyi 'görsel' olarak kopyalar.
                model_id = "xirf/flux-controlnet-canny" # Flux'ın Canny (Kenar koruma) modeli
                
                output = replicate.run(
                    model_id,
                    input={
                        "image": building_file,
                        "control_image": building_file, # Binanın kenarlarını korumak için
                        "prompt": f"Architectural photo. High-end white stone {selected_code} window moldings. "
                                  f"The moldings must have the exact physical shape and profile of {preview_url}. "
                                  f"KEEP THE BRICK WALLS, SCAFFOLDING AND ENVIRONMENT 100% SAME. "
                                  f"Only replace the empty window frames with these white moldings. 8k resolution.",
                        "control_strength": 0.85, # Binayı koruma gücü (Çok Yüksek)
                        "num_inference_steps": 30,
                        "guidance_scale": 4.0
                    }
                )

                if output:
                    st.success("✅ İşlem Tamamlandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Uygulama Sonucu", use_container_width=True)
                    
                    st.download_button("📥 Kaydet", requests.get(res_url).content, file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")
