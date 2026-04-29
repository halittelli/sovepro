import streamlit as st
import requests
import base64

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")
st.title("🏠 Söve Oturucu Pro - Gerçek Grok Imagine")

# Sidebar - API Key
with st.sidebar:
    st.header("🔑 Ayarlar")
    fal_api_key = st.text_input("fal.ai API Key", type="password", 
                                help="fal.ai → Dashboard → API Keys → Yeni key oluştur")
    st.caption("Ücretsiz hesap aç, key al (ilk krediler bedava).")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG / PNG / WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, caption="Yüklenen Bina", use_column_width=True)

with col2:
    st.subheader("📚 Söve Kütüphanesi")
    sove_options = {
        "Modern Beyaz Söve": "Modern Beyaz Söve",
        "Klasik Ahşap Söve": "Klasik Ahşap Söve",
        "Siyah Metal Çerçeve": "Siyah Metal Çerçeve",
        "Lüks Taş Görünümlü": "Lüks Taş Görünümlü",
        "Minimal Gri Söve": "Minimal Gri Söve"
    }
    selected_sove_name = st.selectbox("Hazır söve seç", list(sove_options.keys()))
    st.caption(f"Seçilen: **{selected_sove_name}**")
    
    st.divider()
    st.subheader("Veya kendi söveni yükle (PNG)")
    custom_sove = st.file_uploader("Şeffaf PNG", type=["png"])

if st.button("🔥 SÖVEYİ OTURT - Grok Imagine ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Lütfen bina fotoğrafı yükleyin!")
    elif not fal_api_key or fal_api_key.strip() == "":
        st.error("❌ fal.ai API Key girin (sol taraftaki sidebar'dan)")
    else:
        with st.spinner("Grok Imagine çalışıyor... Pencerelere mükemmel perspektif, ışık ve gölge uyumu yapılıyor..."):
            try:
                # Bina resmini base64'e çevir
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"Bu binadaki TÜM pencerelere {selected_sove_name} modelini mükemmel perspektif, foreshortening, gerçekçi ışık, gölge, cam yansıması ve seamless blending ile oturt. Binada başka hiçbir şeyi değiştirme. Çok profesyonel ve gerçekçi olsun."

                # Düzeltilmiş endpoint (fal.run)
                response = requests.post(
                    "https://fal.run/xai/grok-imagine-image/edit",
                    json={
                        "image_url": f"data:image/jpeg;base64,{building_b64}",
                        "prompt": prompt,
                        "num_images": 1
                    },
                    headers={
                        "Authorization": f"Key {fal_api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=180
                )

                if response.status_code == 200:
                    result = response.json()
                    image_url = result.get("images", [{}])[0].get("url")
                    if image_url:
                        img_data = requests.get(image_url).content
                        st.image(img_data, caption="✅ Grok Imagine ile oturtuldu!", use_column_width=True)
                        st.download_button(
                            label="📥 Sonucu İndir (JPG)",
                            data=img_data,
                            file_name="sove_oturtulmus_grok.jpg",
                            mime="image/jpeg"
                        )
                    else:
                        st.error("Sonuç alınamadı.")
                else:
                    st.error(f"API Hatası: {response.status_code} - {response.text[:300]}")
            except Exception as e:
                st.error(f"Bağlantı hatası: {str(e)}")

st.caption("✅ Artık gerçek Grok Imagine kullanıyorsun. Hata alırsan fal.ai key’ini kontrol et.")
