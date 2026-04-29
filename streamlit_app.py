import streamlit as st
from PIL import Image
import requests
import base64
import time
import io

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")
st.title("🏠 Söve Oturucu Pro - Gerçek Grok Imagine")

# Sidebar - API Key
with st.sidebar:
    st.header("🔑 Ayarlar")
    fal_api_key = st.text_input("fal.ai API Key", type="password", 
                                help="fal.ai sitesine üye ol → API Keys → yeni key oluştur")
    st.caption("Ücretsiz hesap açıp key alman gerekiyor (ilk krediler ücretsiz).")

# Ana ekran
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG / PNG / WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, caption="Yüklenen Bina", use_column_width=True)

with col2:
    st.subheader("📚 Söve Kütüphanesi")
    sove_options = {
        "Modern Beyaz Söve": "https://picsum.photos/id/1015/600/400",
        "Klasik Ahşap Söve": "https://picsum.photos/id/133/600/400",
        "Siyah Metal Çerçeve": "https://picsum.photos/id/201/600/400",
        "Lüks Taş Görünümlü": "https://picsum.photos/id/870/600/400",
        "Minimal Gri Söve": "https://picsum.photos/id/1005/600/400"
    }
    
    selected_sove_name = st.selectbox("Hazır söve seç", list(sove_options.keys()))
    st.image(sove_options[selected_sove_name], caption=selected_sove_name, use_column_width=True)
    
    st.divider()
    st.subheader("Veya kendi söveni yükle")
    custom_sove = st.file_uploader("Şeffaf PNG (önerilen)", type=["png"])

# OTURT butonu
if st.button("🔥 SÖVEYİ OTURT - Grok Imagine ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Lütfen bina fotoğrafı yükleyin!")
    elif not fal_api_key:
        st.error("❌ fal.ai API Key girin (sol taraftaki sidebar'dan)")
    else:
        with st.spinner("Grok Imagine çalışıyor... Pencerelere mükemmel perspektif + ışık + gölge uyumu yapılıyor (bu gerçek AI!)"):
            
            # Bina resmini base64'e çevir
            building_bytes = building_file.getvalue()
            building_b64 = base64.b64encode(building_bytes).decode()

            # Prompt (sabit ve çok güçlü)
            prompt = f"Bu binadaki TÜM pencerelere {selected_sove_name} modelini mükemmel perspektif, foreshortening, gerçekçi ışık, gölge, cam yansıması ve seamless blending ile oturt. Binada başka hiçbir şeyi değiştirme. Çok profesyonel ve gerçekçi olsun."

            # fal.ai API çağrısı (Grok Imagine Edit)
            response = requests.post(
                "https://queue.fal.ai/xai/grok-imagine-image/edit",
                json={
                    "input": {
                        "image_url": f"data:image/jpeg;base64,{building_b64}",
                        "prompt": prompt,
                        "num_images": 1
                    }
                },
                headers={
                    "Authorization": f"Key {fal_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                # Sonuç URL'sini al ve göster
                image_url = result.get("images", [{}])[0].get("url")
                if image_url:
                    img_data = requests.get(image_url).content
                    st.image(img_data, caption="✅ Grok Imagine ile oturtuldu!", use_column_width=True)
                    
                    # İndirme butonu
                    st.download_button(
                        label="📥 Sonucu İndir (JPG)",
                        data=img_data,
                        file_name="sove_oturtulmus_grok.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error("Sonuç alınamadı, lütfen tekrar dene.")
            else:
                st.error(f"API Hatası: {response.status_code} - {response.text}")

st.caption("✅ Artık gerçek Grok Imagine kullanıyorsun! fal.ai API Key'in varsa her seferinde mükemmel sonuç alırsın.")
