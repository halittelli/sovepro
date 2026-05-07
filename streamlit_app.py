import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v20.0 PRO", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()
        st.success("Bağlantı Aktif")

st.title("🏠 Sovetalya: Profesyonel Söve Uygulaması")
st.caption("Flux.1-Dev Motoru | Gelişmiş Önizleme Sistemi")

col1, col2 = st.columns([3, 2])

# --- SOL SÜTUN: BİNA FOTOĞRAFI ---
with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Cephe", use_container_width=True)

# --- SAĞ SÜTUN: KATALOG (SENİN EN SON ÇALIŞAN SİSTEMİN) ---
with col2:
    st.subheader("📚 Söve Kütüphanesi")
    tc_codes = (
        [f"TC{i:03d}" for i in range(1, 25)] + 
        [f"TC{i:03d}" for i in range(35, 41)]
    )
    selected_code = st.selectbox("Model Seçin", tc_codes)
    
    # SENİN EN SON ÇALIŞAN URL YAPIN:
    # Kullanıcı adı: halitelli | Klasör: sove_images | Dosya: TCxxx.png
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/sove_images/{selected_code}.png"
    
    # Görseli çekmeyi dene
    try:
        res = requests.get(preview_url)
        if res.status_code == 200:
            st.image(preview_url, caption=f"Katalog: {selected_code}", use_container_width=True)
        else:
            # Eğer klasör içindeyse bulamazsa, ana dizini dene (B planı)
            fallback_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
            res_fallback = requests.get(fallback_url)
            if res_fallback.status_code == 200:
                st.image(fallback_url, caption=f"Katalog: {selected_code}", use_container_width=True)
            else:
                st.warning(f"⚠️ {selected_code} önizlemesi yüklenemedi. GitHub yolunu kontrol edin.")
    except:
        st.error("Bağlantı hatası.")

st.markdown("---")

# --- İŞLEME BUTONU ---
if st.button("🔥 SÖVEYİ OTURT (Flux Engine)", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Eksik bilgi: Fotoğraf yükleyin veya API Token girin.")
    else:
        with st.spinner("Flux motoru söveleri binaya giydiriyor..."):
            try:
                # Replicate'in en iyi sonuç veren Image-to-Image Flux versiyonu
                model_id = "black-forest-labs/flux-dev"
                
                output = replicate.run(
                    model_id,
                    input={
                        "image": building_file,
                        "prompt": f"Professional architectural photo. Perfectly fit white {selected_code} style decorative window moldings around every window. The moldings must have a realistic white stone texture with natural shadows. Do not change the building walls, roof or environment. 8k resolution.",
                        "prompt_strength": 0.40,  # Binayı korumak ve söveyi eklemek için ideal denge
                        "num_inference_steps": 30,
                        "guidance_scale": 4.5
                    }
                )

                if output:
                    st.success("✅ Tasarım Başarıyla Oluşturuldu!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Uygulama Sonucu", use_container_width=True)
                    
                    # İndirme
                    st.download_button("📥 Sonucu Bilgisayara Kaydet", 
                                     data=requests.get(res_url).content, 
                                     file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.divider()
st.caption("Sovetalya v20.0 | Halit Telli | Architectural AI Solutions")
