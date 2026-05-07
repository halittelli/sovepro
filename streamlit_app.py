import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v22.0", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Ayarları")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()
        st.success("Bağlantı Kuruldu!")

st.title("🏠 Sovetalya: Mimari Söve Uygulaması")
st.caption("GitHub ve Replicate Senkronize Sürüm")

col1, col2 = st.columns([3, 2])

# --- SOL SÜTUN: BİNA YÜKLEME ---
with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("Cephe fotoğrafı seçin", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Mevcut Durum", use_container_width=True)

# --- SAĞ SÜTUN: KATALOG (EKRAN GÖRÜNTÜSÜNE GÖRE GÜNCELLENDİ) ---
with col2:
    st.subheader("📚 Söve Kütüphanesi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] # TC001'den başlıyor
    selected_code = st.selectbox("Söve Seçin", tc_codes)
    
    # EKRAN GÖRÜNTÜSÜNDEKİ GERÇEK YOL:
    # Kullanıcı: halittelli (çift t) | Dal: main | Dosya: Doğrudan ana dizinde
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    
    # Önizlemeyi zorla göster
    st.image(preview_url, caption=f"Seçilen Model: {selected_code}", use_container_width=True)

st.divider()

if st.button("🚀 SÖVEYİ UYGULA", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("Söve giydiriliyor..."):
            try:
                # EKRAN GÖRÜNTÜSÜNDEKİ TAM VERSİYON ID:
                version_id = "06d6fae3b75ab68a28cd2900afa6033166910dd09fd9751047043a5bbb4c184b"
                
                output = replicate.run(
                    f"lucataco/sdxl-controlnet:{version_id}",
                    input={
                        "image": building_file,
                        # AI'ya hem yazılı hem görsel referans veriyoruz
                        "prompt": f"Professional architectural photo of a house. Windows are decorated with {selected_code} style white stone moldings. The molding style is exactly like {preview_url}. High quality, realistic shadows, unchanged walls.",
                        "negative_prompt": "deforming building, changing colors, low quality, distorted architecture",
                        "controlnet_conditioning_scale": 0.8,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                )

                if output:
                    st.success("✅ İşlem Tamam!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Tasarım Sonucu", use_container_width=True)
                    
                    st.download_button("📥 İndir", requests.get(res_url).content, file_name=f"{selected_code}_tasarim.png")

            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.caption("Sovetalya v22.0 | Halit Telli | Antalya")
