import streamlit as st
import requests
import base64
import os

VERSION = "v2.0 - 30 Nisan 2026 - API Key Güvenli"

st.set_page_config(page_title="Söve Oturucu", page_icon="🏠", layout="wide")

st.markdown("<h1 style='text-align: center;'>Söve Oturucu</h1>", unsafe_allow_html=True)
st.caption(f"Versiyon: {VERSION}")

# API Key Railway Variables'dan okunuyor (güvenli)
XAI_API_KEY = os.getenv("XAI_API_KEY")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG, PNG veya WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, use_container_width=True)

with col2:
    st.subheader("📚 Sovetalya Söve Kütüphanesi")
    tc_codes = (
        [f"TC{i:03d}" for i in range(1, 25)] + 
        [f"TC{i:03d}" for i in range(35, 41)]
    )
    selected_code = st.selectbox("Söve Kodunu Seçin", tc_codes)

    # Gerçek ürün önizlemesi
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/sove_images/sove_{selected_code}.jpg"
    st.image(preview_url, caption=f"{selected_code} - Gerçek Ürün", use_container_width=True)

if st.button("🔥 SÖVEYİ OTURT - Grok Imagine ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Bina fotoğrafı yükleyin!")
    elif not XAI_API_KEY:
        st.error("❌ API Key bulunamadı. Railway Variables'a XAI_API_KEY ekleyin.")
    else:
        with st.spinner("Grok Imagine çalışıyor... (15-40 saniye)"):
            try:
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"""
                Bu binadaki TÜM pencerelere {selected_code} kodlu Sovetalya XPS söve modelini 
                mükemmel perspektif, gerçekçi ışık, gölge, cam yansıması ve seamless blending ile oturt. 
                Söve tam olarak orijinal ürün gibi dursun. Binada başka hiçbir şeyi değiştirme. 
                Çok profesyonel mimari render kalitesinde olsun.
                """

                response = requests.post(
                    "https://api.x.ai/v1/images/edits",
                    headers={"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "grok-imagine-image",
                        "prompt": prompt,
                        "image": {"url": f"data:image/jpeg;base64,{building_b64}"}
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    image_url = None
                    if "data" in result and len(result["data"]) > 0:
                        image_url = result["data"][0].get("url")
                    elif "output" in result:
                        image_url = result["output"].get("url")
                    elif "url" in result:
                        image_url = result.get("url")

                    if image_url:
                        img_data = requests.get(image_url).content
                        st.success("✅ Grok Imagine ile oturtuldu!")
                        st.image(img_data, caption="Sonuç", use_container_width=True)

                        st.download_button(
                            label="📥 Sonucu İndir (JPG)",
                            data=img_data,
                            file_name=f"sove_{selected_code}.jpg",
                            mime="image/jpeg"
                        )
                    else:
                        st.error("Sonuç URL'si alınamadı.")
                else:
                    st.error(f"API Hatası: {response.status_code}")

            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.caption(f"Versiyon: {VERSION}")
