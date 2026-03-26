import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Arşiv Okuyucu AI", layout="wide")

# --- SOL MENÜ (API AYARLARI) ---
st.sidebar.title("🔑 Bağlantı Ayarları")
st.sidebar.write("Google AI Studio'dan aldığınız API anahtarını buraya yapıştırın.")
api_key = st.sidebar.text_input("Gemini API Anahtarı:", type="password")

# Modelleri tutacağımız liste
available_models = []
selected_model = None

# API anahtarı girildiyse modelleri otomatik çek
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Sadece metin ve görsel üretebilen modelleri bul
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if available_models:
            st.sidebar.success("✅ API Bağlantısı Başarılı!")
            # Bulunan modelleri kullanıcıya açılır menü ile sun
            selected_model = st.sidebar.selectbox("Kullanılacak Yapay Zeka Modeli:", available_models)
    except Exception as e:
        st.sidebar.error("API Anahtarı geçersiz veya bağlantı kurulamadı.")

# --- ANA EKRAN ---
st.title("🚀 Yapay Zeka Destekli Arşiv Okuyucu")
st.write("El yazısı, eski belge veya soluk metin... Yapay zekaya gönderin ve arkanıza yaslanın.")

uploaded_file = st.file_uploader("Belge Yükle (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    image = Image.open(uploaded_file)
    
    with col1:
        st.subheader("Yüklenen Belge")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("Çıkarılan Metin")
        
        # Kullanıcıyı yönlendir
        if not api_key:
            st.warning("👈 Lütfen işlemi başlatmadan önce sol menüye API Anahtarınızı girin.")
        elif not selected_model:
            st.warning("⏳ Modeller yükleniyor veya yetkiniz yok...")
        else:
            if st.button("Yapay Zeka ile Oku", use_container_width=True):
                with st.spinner(f"Yapay zeka ({selected_model}) belgeyi inceliyor ve el yazılarını çözüyor..."):
                    try:
                        # Baştaki 'models/' takısını temizleyip modeli ayarlıyoruz
                        model_name = selected_model.replace("models/", "")
                        model = genai.GenerativeModel(model_name)
                        
                        # Yapay zekaya vereceğimiz özel komut
                        prompt = """
                        Sen uzman bir arşivci ve dilbilimcisin. Lütfen bu görseldeki metni, 
                        el yazıları ve eski daktilo fontları dahil olmak üzere en yüksek doğrulukla metne dök. 
                        Okuyamadığın veya emin olamadığın yerler olursa köşeli parantez içinde [okunamadı] şeklinde belirt. 
                        Sadece belgedeki metni yaz, kendi yorumlarını veya fazladan açıklamaları katma.
                        """
                        
                        response = model.generate_content([prompt, image])
                        
                        st.success("Okuma Başarılı!")
                        edited_text = st.text_area("Düzenleyebilirsiniz:", response.text, height=350)
                        st.download_button("Metni İndir (.txt)", data=edited_text, file_name="yapay_zeka_metni.txt", mime="text/plain")
                        
                    except Exception as e:
                        st.error("Okuma sırasında bir hata oluştu.")
                        st.code(str(e))