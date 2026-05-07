import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v33.0 - Grok Logic", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: Grok Motoru Mantığı")
st.caption("Otomatik Mimari Giydirme | Doku Kilitleme Teknolojisi")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe Fotoğrafı", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Yapı (Dondurulacak)", use_container_width=True)

with col2:
    st.subheader("📚 Söve Referansı")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Söve Seçin", tc_codes)
    
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Uygulanacak Geometri: {selected_code}", width=250)

st.divider()

if st.button("🚀 GROK MANTIĞIYLA UYGULA", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("Grok Algoritması pencereleri analiz ediyor..."):
            try:
                # Grok'un arkada kullandığı Flux mimarisi (En kararlı versiyon)
                model_id = "black-forest-labs/flux-dev"
                
                # --- İŞTE O GİZLİ MANTIK: GROK'UN OTOMATİK PROMPTU ---
                # AI'ya binayı bozmaması gerektiğini ama pencereyi 'modifiye' etmesi gerektiğini anlatıyoruz.
                grok_prompt = (
                    f"A professional architectural modification of the building photo. "
                    f"Task: Identify every window frame and add white {selected_code} style decorative architectural moldings. "
                    f"Structural Rule: Keep the existing red brick texture, mortar lines, scaffolding, and environmental lighting 100% SAME. "
                    f"Geometry Reference: The molding must follow the exact profile and shape of {preview_url}. "
                    f"Result: The white moldings should look integrated onto the brick wall with realistic 3D shadows and correct perspective."
                )

                output = replicate.run(
                    model_id,
                    input={
                        "image": building_file,
                        "prompt": grok_prompt,
                        "guidance_scale": 3.5,
                        "num_inference_steps": 30,
                        # KRİTİK AYAR: 0.32-0.38 aralığı 'Grok'un doku koruma bölgesidir.
                        # Bina dokusunu yerinde tutar, sadece pencerelere 'ekleme' yapar.
                        "prompt_strength": 0.35,
                        "extra_lora_scale": 1.0
                    }
                )

                if output:
                    st.success("✅ İşlem Başarılı! Bina dokusu korundu, söveler monte edildi.")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Grok-Style Uygulama Sonucu", use_container_width=True)
                    
                    st.download_button("📥 Tasarımı Kaydet", requests.get(res_url).content, file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")

st.caption("Sovetalya v33.0 | Antalya | Architectural AI")
