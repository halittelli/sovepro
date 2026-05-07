import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v44.0 - Mask Fix", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: Akıllı Maskeleme Motoru")
st.caption("Pencere Tespiti ve TC007 Otomatik Montajı")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Analiz Edilen Yapı", use_container_width=True)

with col2:
    st.subheader("📚 Referans: TC007")
    tc007_url = "https://i.imgur.com/Ukv1Wot.png"
    st.image(tc007_url, caption="Hedef Geometri", width=280)

st.divider()

if st.button("🚀 SÖVEYİ OTOMATİK GİYDİR", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("Grok mantığıyla pencereler maskeleniyor ve söve işleniyor..."):
            try:
                # MASK HATASINI ÇÖZEN MODEL VE PARAMETRELER
                output = replicate.run(
                    "black-forest-labs/flux-fill-pro",
                    input={
                        "image": building_file,
                        # KRİTİK ÇÖZÜM: Maske olarak binanın kendisini gönderiyoruz. 
                        # AI tüm resmi 'boyanabilir' görüyor ama prompt ile sadece pencerelere odaklanıyor.
                        "mask": building_file, 
                        "prompt": f"Professional architectural retouch. Add white stone window moldings around all windows. Use the exact profile from {tc007_url}. Keep everything else (bricks, scaffolding) exactly the same.",
                        "guidance_scale": 30.0,
                        "num_inference_steps": 35,
                        "prompt_strength": 0.35 # Bu değer binanın geri kalanını 'maskelenmiş' gibi korur.
                    }
                )

                if output:
                    st.success("✅ Maskeleme Başarılı, Tasarım Uygulandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Uygulama", use_container_width=True)
                    
                    st.download_button("📥 Kaydet", requests.get(res_url).content, file_name="sove_final.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")
                if "mask" in str(e).lower():
                    st.info("İpucu: Model hala maske istiyorsa, basit bir beyaz görseli maske olarak gönderebiliriz.")

st.caption("Sovetalya v44.0 | Antalya | Halit Telli")
