import streamlit as st
from PIL import Image

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")
st.title("🏠 Söve Oturucu Pro - Ücretsiz Demo")
st.markdown("**Bina fotoğrafı yükle + söve seç → otomatik oturt (demo)**")

# Sol taraf: Yükleme ve galerisi
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    uploaded_file = st.file_uploader("JPG, PNG veya WEBP", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Yüklenen Bina", use_column_width=True)
        st.session_state.building = uploaded_file

with col2:
    st.subheader("📚 Söve Kütüphanesi")
    # Demo söve örnekleri (kendi PNG'lerini buraya ekleyebilirsin)
    sove_options = {
        "Modern Beyaz Söve": "https://picsum.photos/id/1015/400/300",
        "Klasik Ahşap Söve": "https://picsum.photos/id/133/400/300",
        "Lüks Siyah Çerçeve": "https://picsum.photos/id/201/400/300",
        "Minimal Gri": "https://picsum.photos/id/251/400/300",
        "Taş Görünümlü": "https://picsum.photos/id/870/400/300"
    }
    
    selected_sove_name = st.selectbox("Söve seç", list(sove_options.keys()))
    st.image(sove_options[selected_sove_name], caption=selected_sove_name, use_column_width=True)
    st.session_state.selected_sove = selected_sove_name

# İşlem butonu
if st.button("🔥 SÖVEYİ OTURT (Otomatik)", type="primary", use_container_width=True):
    if "building" not in st.session_state:
        st.error("Lütfen önce bina fotoğrafı yükle!")
    else:
        with st.spinner("Grok Imagine kalitesinde perspektif, ışık ve gölge uyumu yapılıyor... (demo)"):
            st.success("✅ Söve başarıyla oturtuldu!")
            st.image(uploaded_file, caption="✅ Sonuç: Söve perspektifli ve gerçekçi şekilde oturtuldu", use_column_width=True)
            st.markdown("**Not:** Bu demo modudur. Sonraki adımda fal.ai ile gerçek Grok Imagine entegrasyonu eklenecek.")

# İndirme butonu (demo)
st.download_button(
    label="📥 Sonucu İndir (Demo)",
    data=uploaded_file.getvalue() if "building" in st.session_state else b"",
    file_name="sove-oturtulmus-demo.jpg",
    mime="image/jpeg",
    disabled="building" not in st.session_state
)

st.caption("Bu demo tamamen ücretsiz ve anında çalışır. Beğenirsen bir sonraki adımda Render.com veya Railway’e canlı deploy edeceğiz.")
