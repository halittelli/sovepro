import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v27.0", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Ayarları")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: Profesyonel Söve Uygulaması")
st.caption("Auto-Version Flux Engine | Bina Dokusunu Koruma Garantili")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe Fotoğrafı Yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("📚 Söve Modeli")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Söve Seçin", tc_codes)
    
    # GitHub URL - halittelli (çift t)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Uygulanacak: {selected_code}", width=250)

st.divider()

if st.button("🚀 SÖVEYİ OTOMATİK UYGULA", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("AI motoru doğrulanıyor ve söve giydiriliyor..."):
            try:
                # 422 HATASINI BİTİREN YÖNTEM: Versiyon ID kullanmadan doğrudan model ismiyle çağırıyoruz
                # Bu yöntem her zaman Replicate üzerindeki en güncel/izinli sürümü çeker.
                
                output = replicate.run(
                    "black-forest-labs/flux-dev", # En stabil ana motor
                    input={
                        "image": building_file,
                        "prompt": f"Add white {selected_code} style architectural window moldings to the windows of this building. "
                                  f"The moldings must look exactly like the reference model: {preview_url}. "
                                  f"EXTREMELY IMPORTANT: Keep the original building exactly the same. Do not change the red bricks, "
                                  f"do not change the construction scaffolding, do not change the environment. "
                                  f"Only add the white moldings around windows. Professional architectural render.",
                        "guidance_scale": 3.5,
                        "num_inference_steps": 28,
                        "prompt_strength": 0.40  # Bina dokusunu kilitlemek için en kritik ayar (Grok gibi davranır)
                    }
                )

                if output:
                    st.success("✅ İşlem Başarılı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Sonuç", use_container_width=True)
                    
                    st.download_button("📥 Tasarımı Kaydet", requests.get(res_url).content, file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")
                st.info("Eğer hala izin hatası alıyorsanız, Replicate hesabınızda ödeme yönteminin tanımlı veya bakiyenizin (en az 1$) olduğundan emin olun.")

st.caption("Sovetalya v27.0 | Antalya | Halit Telli")
