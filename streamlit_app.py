import streamlit as st
import requests
import base64
from PIL import Image
import io

VERSION = "v1.4 - Debug Mod - 18 Mayıs 2026"

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")

st.title("🏠 Söve Oturucu Pro - Grok Imagine (xAI)")
st.caption(f"**Versiyon:** {VERSION} | API Debug Modu Aktif")

# Sidebar
with st.sidebar:
    st.header("🔑 xAI API Key")
    xai_api_key = st.text_input("xAI API Key", type="password", 
                                help="https://console.x.ai → API Keys")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG / PNG / WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, caption="Yüklenen Bina", use_container_width=True)

with col2:
    st.subheader("📚 Sovetalya Söve Kütüphanesi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Söve Kodunu Seçin", tc_codes)
    
    # Fotoğraflar ana dizinde olduğu için
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"{selected_code} - Sovetalya Söve", use_container_width=True)

if st.button("🔥 SÖVEYİ OTURT - Grok Imagine ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Lütfen bina fotoğrafı yükleyin!")
    elif not xai_api_key or xai_api_key.strip() == "":
        st.error("❌ Lütfen xAI API Key girin!")
    else:
        with st.spinner("Grok Imagine çalışıyor... (15-40 saniye)"):
            try:
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"""
                Bu binadaki TÜM pencerelere ve balkon kapılarına {selected_code} kodlu 
                Sovetalya XPS söve modelini mükemmel perspektif, gerçekçi ışık, gölge, 
                cam yansıması ve seamless blending ile oturt. 
                Söve tam olarak orijinal ürün gibi dursun. Binada başka hiçbir şeyi değiştirme.
                Çok profesyonel mimari render kalitesinde olsun.
                """

                response = requests.post(
                    "https://api.x.ai/v1/images/edits",
                    headers={
                        "Authorization": f"Bearer {xai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-imagine-image",
                        "prompt": prompt.strip(),
                        "image": {"url": f"data:image/jpeg;base64,{building_b64}"}
                    },
                    timeout=90
                )

                # Debug
                st.subheader("🔍 API Debug Bilgisi")
                st.json(response.json())

                if response.status_code == 200:
                    result = response.json()
                    image_url = None
                    
                    if isinstance(result.get("output"), dict):
                        image_url = result["output"].get("url")
                    elif result.get("url"):
                        image_url = result.get("url")
                    elif isinstance(result.get("data"), list) and len(result["data"]) > 0:
                        image_url = result["data"][0].get("url")
                    elif isinstance(result.get("images"), list) and len(result["images"]) > 0:
                        image_url = result["images"][0].get("url")

                    if image_url:
                        img_data = requests.get(image_url).content
                        st.success("✅ Grok Imagine ile başarıyla tamamlandı!")
                        st.image(img_data, caption="Sonuç", use_container_width=True)
                        
                        st.download_button(
                            label="📥 Sonucu İndir",
                            data=img_data,
                            file_name=f"sove_{selected_code}.jpg",
                            mime="image/jpeg"
                        )
                    else:
                        st.error("❌ Sonuç URL'si bulunamadı.")
                else:
                    st.error(f"API Hatası: {response.status_code}")
                    st.code(response.text[:1500])

            except Exception as e:
                st.error(f"Genel Hata: {str(e)}")

st.caption(f"**Versiyon:** {VERSION}")
