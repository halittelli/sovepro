import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v43.0 - Pro Engine", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: TC007 Profesyonel Entegrasyon")
st.caption("Flux-Fill-Pro Motoru | Görsel Referanslı Mimari Uygulama")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Hedef Bina")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Uygulama Alanı", use_container_width=True)

with col2:
    st.subheader("📚 Referans Model: TC007")
    # Doğrulanmış Imgur Linki
    tc007_url = "https://i.imgur.com/Ukv1Wot.png"
    st.image(tc007_url, caption="Kopyalanacak Şekil", width=280)

st.divider()

if st.button("🚀 TC007 MODELİNİ BİNAYA MONTE ET", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("Flux-Fill-Pro motoru pencereleri analiz ediyor..."):
            try:
                # EKRAN GÖRÜNTÜSÜNDEKİ PROFESYONEL MODEL
                # Versiyon ID yazmıyoruz, doğrudan model adı ile çağırıyoruz.
                output = replicate.run(
                    "black-forest-labs/flux-fill-pro",
                    input={
                        "image": building_file,
                        # PROMPT: Grok mantığıyla binayı dondurup söveyi işleyen özel komut
                        "prompt": f"Professional architectural edit. Apply the white decorative stone molding (söve) with the exact double-bullnose profile of {tc007_url} around every window frame. CRITICAL: Keep the original red brick texture, scaffolding, and lighting 100% identical. Only modify the window perimeters. High-resolution output.",
                        "guidance_scale": 30.0, # Komuta tam sadakat
                        "num_inference_steps": 35,
                        "prompt_strength": 0.35 # Bina dokusunu koruma kilidi
                    }
                )

                if output:
                    st.success("✅ Uygulama Tamamlandı!")
                    # Pro model genellikle bir URL döndürür
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Sonuç (TC007)", use_container_width=True)
                    
                    st.download_button("📥 Kaydet", requests.get(res_url).content, file_name="sovetalya_output.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")
                if "402" in str(e):
                    st.warning("Not: Flux-Fill-Pro modeli için Replicate hesabınızda kredi/bakiye olması gerekebilir.")

st.caption("Sovetalya v43.0 | Antalya | Halit Telli")
