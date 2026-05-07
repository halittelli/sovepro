import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v30.0 PRO", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol Paneli")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: Profesyonel Mimari Giydirme")
st.caption("Grok-Style Image Projection Engine | Doku Koruma ve Şekil Entegrasyonu")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Orijinal Bina Analizi")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Korunacak Orijinal Cephe", use_container_width=True)

with col2:
    st.subheader("📚 Söve Referans Geometrisi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Model Seçin", tc_codes)
    
    # GitHub URL (halittelli)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Referans Şekil: {selected_code}", width=250)

st.divider()

if st.button("🚀 SÖVEYİ BİNAYA MONTE ET", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("Grok Algoritması çalışıyor: Bina dokusu donduruluyor ve söveler işleniyor..."):
            try:
                # 404/422 HATASI VERMEYEN EN GÜNCEL RESMİ MOTOR
                model_id = "black-forest-labs/flux-dev"
                
                # GROK'UN ARKADA YAPTIĞI "PROFESYONEL PROMPT" KURGUSU
                complex_prompt = (
                    f"A high-quality architectural photography of the provided building. "
                    f"Maintain the existing red brick walls, construction scaffolding, and overall atmosphere 100% identically. "
                    f"Using the geometric profile of the molding from {preview_url}, "
                    f"precisely install white decorative {selected_code} stone moldings around every window frame. "
                    f"The moldings must show realistic depth, 3D profile, and soft shadows on the brick. "
                    f"NO changes to the building's color, structure, or texture. "
                    f"Ensure the moldings follow the perspective of the original photo perfectly."
                )

                output = replicate.run(
                    model_id,
                    input={
                        "image": building_file,
                        "prompt": complex_prompt,
                        "guidance_scale": 4.5,
                        "num_inference_steps": 35,
                        # Binayı korumak için 0.35 - 0.42 arası en güvenli 'Grok' bölgesidir.
                        "prompt_strength": 0.40,
                        "extra_lora_scale": 0.8
                    }
                )

                if output:
                    st.success("✅ İşlem Başarılı! Bina dokusu korundu, söveler eklendi.")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Uygulama Sonucu", use_container_width=True)
                    
                    st.download_button("📥 Tasarımı Kaydet", requests.get(res_url).content, file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")

st.caption("Sovetalya v30.0 | Antalya | Architectural AI Solutions")
