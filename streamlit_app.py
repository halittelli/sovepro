import streamlit as st
import requests
import os

# ... (Sidebar ve başlık kısımları aynı kalacak) ...

with col2:
    st.subheader("🛠️ Model Kütüphanesi")
    
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Uygulanacak Söve Modelini Seçin", tc_codes, index=0)
    
    st.markdown(f"**Seçilen Model Ön İzlemesi:** `{selected_code}`")
    
    # GÜNCEL GITHUB URL (Daha güvenli erişim için raw.githubusercontent kullanıyoruz)
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    
    # Tarayıcı gibi davranması için headers ekliyoruz
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        # Önce .png (küçük harf) dene
        response = requests.get(preview_url, headers=headers)
        
        # Eğer bulunamadıysa (404), bir de .PNG (büyük harf) dene
        if response.status_code != 200:
            preview_url_upper = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.PNG"
            response = requests.get(preview_url_upper, headers=headers)
            if response.status_code == 200:
                preview_url = preview_url_upper

        if response.status_code == 200:
            st.image(preview_url, caption=f"Model: {selected_code}", width=300)
        else:
            # Hata detayını gösterelim ki sorunu anlayalım
            st.error(f"Görsel bulunamadı. (Hata Kodu: {response.status_code})")
            st.info(f"GitHub'da bu dosyanın tam adının '{selected_code}.png' olduğundan emin ol.")
            # Hatalı URL'yi göster (Test etmek için)
            st.write(f"Aranan adres: {preview_url}")
            
    except Exception as e:
        st.warning(f"Bağlantı hatası: {e}")

# ... (Geri kalan Replicate kodları aynı) ...
