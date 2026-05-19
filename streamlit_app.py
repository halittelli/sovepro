import streamlit as st
import requests
import base64
import time
from PIL import Image

VERSION = "v1.5 - Nano Banana 2 Polling Edition - 19 Mayıs 2026"

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")

st.title("🏠 Söve Oturucu Pro - Nano Banana 2")
st.caption(f"**Versiyon:** {VERSION}")

with st.sidebar:
    st.header("🔑 Replicate API Key")
    replicate_api_key = st.text_input("Replicate API Key", type="password", 
                                      help="replicate.com/account/api-tokens")

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
    
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"{selected_code} - Sovetalya Söve", use_container_width=True)

if st.button("🔥 SÖVEYİ OTURT - Nano Banana 2 ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Bina fotoğrafı yükleyin!")
    elif not replicate_api_key:
        st.error("❌ Replicate API Key girin!")
    else:
        with st.spinner("Nano Banana 2 çalışıyor..."):
            try:
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"""
                Bu binadaki TÜM pencerelere ve balkon kapılarına {selected_code} kodlu 
                Sovetalya XPS dekoratif söve modelini uygula. 
                Mükemmel perspektif, gerçekçi ışık ve gölge, cam yansıması, seamless blending yap.
                Söveler orijinal ürün kalitesinde ve doğal dursun. 
                Binanın diğer hiçbir kısmını değiştirme. 
                Profesyonel mimari render kalitesi.
                """

                # Prediction oluştur
                create_response = requests.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {replicate_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "google/nano-banana-2",   # En güncel versiyonu Replicate'ten kontrol et
                        "input": {
                            "image": f"data:image/jpeg;base64,{building_b64}",
                            "prompt": prompt.strip(),
                            "num_outputs": 1,
                            "quality": "high"
                        }
                    }
                )

                if create_response.status_code != 201:
                    st.error("Prediction başlatılamadı")
                    st.json(create_response.json())
                    st.stop()

                prediction = create_response.json()
                prediction_id = prediction["id"]

                st.info(f"Prediction ID: {prediction_id} - İşleniyor...")

                # Polling
                for _ in range(60):  # Max 2 dakika bekle
                    time.sleep(3)
                    
                    get_response = requests.get(
                        f"https://api.replicate.com/v1/predictions/{prediction_id}",
                        headers={"Authorization": f"Token {replicate_api_key}"}
                    )
                    
                    result = get_response.json()
                    status = result.get("status")

                    if status == "succeeded":
                        output_url = result["output"][0] if isinstance(result.get("output"), list) else result.get("output")
                        if output_url:
                            img_data = requests.get(output_url).content
                            st.success("✅ Nano Banana 2 ile işlem tamamlandı!")
                            st.image(img_data, caption="Sonuç", use_container_width=True)
                            
                            st.download_button(
                                "📥 Sonucu İndir",
                                data=img_data,
                                file_name=f"sove_{selected_code}_nanob2.jpg",
                                mime="image/jpeg"
                            )
                        break
                    elif status in ["failed", "canceled"]:
                        st.error(f"İşlem başarısız: {result.get('error')}")
                        st.json(result)
                        break
                    else:
                        st.info(f"Durum: {status}... Bekleniyor.")

                else:
                    st.warning("İşlem çok uzun sürdü. Tekrar deneyin.")

            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.caption(f"**Versiyon:** {VERSION}")
