import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v41.0 - Kesin Bağlantı", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Bağlantısı")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: TC007 Montaj Motoru")
st.caption("Resmi Flux Motoru | Bina Dokusu Koruma & Geometrik Uygulama")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Uygulama Alanı")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Cephe", use_container_width=True)

with col2:
    st.subheader("📚 Referans Söve: TC007")
    # Imgur ham linki (Doğrulanmış)
    tc007_link = "https://i.imgur.com/Ukv1Wot.png"
    st.image(tc007_link, caption="Şekli Kopyalanacak Model", width=250)

st.divider()

if st.button("🚀 TC007 MODELİNİ BİNAYA İŞLE", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("AI mimariyi analiz ediyor ve söveyi yerleştiriyor..."):
            try:
                # 422 HATASINI BİTİREN RESMİ MODEL ADI (ID SİZ)
                model_name = "black-forest-labs/flux-fill" # Resmi 'Doldurma/Değiştirme' modeli
                
                output = replicate.run(
                    model_name,
                    input={
                        "image": building_file,
                        # Binayı 100% koruması için maske yerine prompt içinde 'modify' komutu veriyoruz
                        "prompt": f"Professional architectural photograph. Precisely add white decorative stone window moldings (söve) around every window frame. The molding profile must match the 3D double-bullnose geometry from {tc007_link}. STRICTLY KEEP the original red brick texture, construction scaffolding, and environment 100% the same. Do not touch the walls, only the window perimeters. High-end realistic shadows.",
                        "guidance_scale": 30.0, # Komuta sadakat seviyesi (Yüksek)
                        "num_inference_steps": 30,
                        "prompt_strength": 0.35 # Doku koruma kilidi
                    }
                )

                if output:
                    st.success("✅ Tasarım Uygulandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="TC007 Uygulama Sonucu", use_container_width=True)
                    
                    st.download_button("📥 Kaydet", requests.get(res_url).content, file_name="sove_uygulama.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")

st.caption("Sovetalya v41.0 | Antalya | Halit Telli")
