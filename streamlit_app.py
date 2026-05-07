import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v17.0 PRO", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol Paneli")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()
        st.success("API Bağlantısı Aktif")

st.title("🏠 Sovetalya: Akıllı Söve Uygulaması")
st.caption("Flux.1 Dev Motoru - Dinamik Versiyon Kontrolü")

col1, col2 = st.columns([3, 2])

# --- SOL SÜTUN: BİNA FOTOĞRAFI ---
with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Cephe", use_container_width=True)

# --- SAĞ SÜTUN: KATALOG ---
with col2:
    st.subheader("📚 Söve Kütüphanesi")
    # Kod aralıklarını senin listene göre güncelledim
    tc_codes = (
        [f"TC{i:03d}" for i in range(1, 25)] + 
        [f"TC{i:03d}" for i in range(35, 41)]
    )
    selected_code = st.selectbox("Model Seçin", tc_codes)
    
    # DÜZELTİLMİŞ URL: 'halitelli' (Tek 't') ve 'sove_images' klasörü eklendi
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/sove_images/{selected_code}.png"
    
    try:
        response = requests.get(preview_url)
        if response.status_code == 200:
            st.image(preview_url, caption=f"Katalog: {selected_code}", use_container_width=True)
        else:
            st.warning(f"Görsel bulunamadı: {selected_code}. URL kontrol ediliyor...")
    except:
        st.error("Katalog bağlantı hatası.")

st.markdown("---")

if st.button("🔥 SÖVEYİ OTURT (Flux Engine)", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("AI Motoru en güncel sürümü doğruluyor ve söve giydiriliyor..."):
            try:
                # --- DİNAMİK VERSİYON ÇEKME (KESİN ÇÖZÜM) ---
                # Modelin ismini veriyoruz, en güncel ID'yi Python kendi buluyor
                model = replicate.models.get("lucataco/flux-dev-img2img")
                version_id = model.latest_version.id
                
                output = replicate.run(
                    f"lucataco/flux-dev-img2img:{version_id}",
                    input={
                        "image": building_file,
                        "prompt": f"Extremely detailed architectural photography. Add white {selected_code} style architectural window moldings to the windows of this building. The moldings should be white stone texture, perfectly integrated with realistic shadows. Keep the rest of the building exactly the same. 8k resolution.",
                        "prompt_strength": 0.45, # Binayı korumak için 0.45 idealdir
                        "num_inference_steps": 28,
                        "guidance_scale": 3.5
                    }
                )

                if output:
                    st.success("✅ İşlem Başarılı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Uygulama Sonucu", use_container_width=True)
                    
                    # İndirme Butonu
                    btn_data = requests.get(res_url).content
                    st.download_button("📥 Tasarımı Kaydet", data=btn_data, file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")

st.divider()
st.caption("Sovetalya v17.0 | Halit Telli | Antalya")
