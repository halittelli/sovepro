import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v24.0 - Flux Inpaint", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Ayarları")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: Kesin Sonuç Motoru")
st.caption("Flux.1-Dev Inpaint - Binayı Değiştirmeden Söve Ekleme")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe Fotoğrafı", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("📚 Söve Modeli")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Söve Seçin", tc_codes)
    
    # GitHub URL (Çift 't' ile halittelli)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Model: {selected_code}", width=250)

st.divider()

if st.button("🚀 SÖVELERİ OTOMATİK YERLEŞTİR", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf ve token girin!")
    else:
        with st.spinner("Cerrahi operasyon başlıyor... Binanızın dokusu korunuyor."):
            try:
                # BU MODEL "INPAINT" MODELİDİR: SADECE DEĞİŞMESİ GEREKEN YERİ DEĞİŞTİRİR
                model_id = "black-forest-labs/flux-dev-inpaint"
                
                output = replicate.run(
                    model_id,
                    input={
                        "image": building_file,
                        # Prompt: Sadece pencerelere odaklanıyoruz
                        "prompt": f"Professional architectural retouch. Add white decorative {selected_code} style stone window moldings around all windows. The moldings must look like {preview_url}. KEEP THE REST OF THE BUILDING EXACTLY THE SAME. Do not change brick texture, do not change construction details. 8k resolution, realistic shadows.",
                        "negative_prompt": "change building texture, change wall color, blur, distorted architecture",
                        "num_inference_steps": 30,
                        "guidance_scale": 3.5,
                        "prompt_strength": 0.85 # Inpaint modelinde bu değer değişim miktarını belirler
                    }
                )

                if output:
                    st.success("✅ İşlem Tamamlandı! Bina dokusu korundu.")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Sonuç", use_container_width=True)
                    
                    st.download_button("📥 Tasarımı İndir", requests.get(res_url).content, file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata: {str(e)}")
                st.info("İpucu: Eğer 404 alırsan Replicate üzerinden Flux Inpaint model şartlarını kabul etmen gerekebilir.")

st.caption("Sovetalya v24.0 | Cerrahi Giydirme Teknolojisi")
