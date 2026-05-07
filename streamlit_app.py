import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v26.0", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Ayarları")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: Profesyonel Söve Uygulaması")
st.caption("Flux Dev Inpaint Engine | Bina Dokusunu Kilitleme Modu")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe Fotoğrafı Yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("📚 Söve Modeli")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Model Seçin", tc_codes)
    
    # GitHub URL - Çift 't' ile halittelli
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Uygulanacak: {selected_code}", width=250)

st.divider()

if st.button("🚀 SÖVEYİ OTOMATİK UYGULA", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("AI motoru pencereleri analiz ediyor..."):
            try:
                # KESİN ÇALIŞAN MODEL VE VERSİYON ID:
                # Bu model şu an Replicate'te 'ali-vil' tarafından sunulan aktif Flux Inpaint modelidir.
                model_id = "ali-vil/flux-1-dev-inpaint:0272b5a6c986c52a0a256df2669e4f507b99c719875e533157a5ef0e85497424"
                
                output = replicate.run(
                    model_id,
                    input={
                        "image": building_file,
                        # Prompt: Binayı değiştirme, sadece pencerelere söveyi monte et
                        "prompt": f"Add white {selected_code} style architectural window moldings to the windows of this building. "
                                  f"The moldings should look exactly like {preview_url}. "
                                  f"STRICTLY PRESERVE the original building facade, red brick texture, and construction environment. "
                                  f"Do not change any other part of the image. High quality architectural render.",
                        "num_inference_steps": 28,
                        "guidance_scale": 3.5,
                        "prompt_strength": 0.8,
                        "mask_blur": 3
                    }
                )

                if output:
                    st.success("✅ İşlem Tamamlandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Sonuç", use_container_width=True)
                    
                    st.download_button("📥 Tasarımı Kaydet", requests.get(res_url).content, file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")
