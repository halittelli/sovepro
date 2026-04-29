import streamlit as st
from huggingface_hub import InferenceClient
import requests
from PIL import Image
import io

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")
st.title("🏠 Söve Oturucu Pro - Ücretsiz Hugging Face AI")

# Sidebar - HF Token
with st.sidebar:
    st.header("🔑 Hugging Face Token")
    hf_token = st.text_input("HF Access Token (hf_ ile başlayan)", type="password")
    st.caption("huggingface.co/settings/tokens adresinden ücretsiz al.")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG / PNG / WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, caption="Yüklenen Bina", use_column_width=True)

with col2:
    st.subheader("📚 Söve Seçimi")
    sove_name = st.selectbox("Söve tipi seç", [
        "Modern Beyaz Söve", "Klasik Ahşap Söve", "Siyah Metal Çerçeve",
        "Lüks Taş Görünümlü", "Minimal Gri Söve"
    ])
    st.caption(f"Seçilen: **{sove_name}**")

if st.button("🔥 SÖVEYİ OTURT - Ücretsiz AI ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Bina fotoğrafı yükleyin!")
    elif not hf_token or "hf_" not in hf_token:
        st.error("❌ Hugging Face token girin!")
    else:
        with st.spinner("Qwen Image Edit çalışıyor... Pencerelere perspektif + ışık + gölge uyumu yapılıyor (gerçek AI!)"):
            try:
                client = InferenceClient(token=hf_token)
                
                # Bina resmini byte yap
                building_bytes = building_file.getvalue()
                
                # Güçlü prompt (söve oturtma için optimize edildi)
                prompt = f"Bu binadaki TÜM pencerelere {sove_name} modelini mükemmel perspektif, doğru orantı, gerçekçi ışık, gölge, cam yansıması ve kusursuz blending ile oturt. Söve orijinal detaylarını koru. Binada başka hiçbir şeyi değiştirme. Çok profesyonel ve gerçekçi olsun."

                # Qwen Image Edit ile çağrı
                result = client.image_to_image(
                    model="Qwen/Qwen-Image-Edit",
                    image=building_bytes,
                    prompt=prompt,
                    guidance_scale=7.5,
                    num_inference_steps=30
                )
                
                # Sonucu göster
                st.image(result, caption="✅ Ücretsiz AI ile oturtuldu!", use_column_width=True)
                
                # İndirme
                buf = io.BytesIO()
                result.save(buf, format="JPEG")
                st.download_button(
                    label="📥 Sonucu İndir (JPG)",
                    data=buf.getvalue(),
                    file_name="sove_oturtulmus.jpg",
                    mime="image/jpeg"
                )
                
            except Exception as e:
                st.error(f"Hata: {str(e)} - Token’ını veya internet bağlantını kontrol et.")

st.caption("✅ Bu tamamen ücretsiz Hugging Face AI’dir. Günlük limitin biterse ertesi gün devam edersin.")
