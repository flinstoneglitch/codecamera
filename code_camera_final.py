import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pytesseract
import qrcode
from datetime import datetime
import easyocr

st.set_page_config(page_title="Code Camera", layout="centered", initial_sidebar_state="collapsed")

# PWA Enhancements
st.markdown("""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0a001f">
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#00ffff; text-align:center; font-size:2.5em;'>CODE CAMERA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#ff00ff; text-align:center;'>80s NEON FUTURE</h2>", unsafe_allow_html=True)

reader = easyocr.Reader(['en'])

st.subheader("📸 Live Camera")
camera_photo = st.camera_input("Take a picture of code")

st.subheader("📁 Upload Photos (Batch OK)")
uploaded_files = st.file_uploader("Drop multiple photos", type=["jpg","png","jpeg"], accept_multiple_files=True)

files_to_process = [camera_photo] if camera_photo else []
if uploaded_files:
    files_to_process.extend(uploaded_files)

for uploaded_file in files_to_process:
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
        
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.convertScaleAbs(gray, alpha=1.8, beta=30)
        denoised = cv2.fastNlMeansDenoising(enhanced)
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        code_text = pytesseract.image_to_string(thresh, config='--psm 6')
        if len(code_text.strip()) < 30:
            result = reader.readtext(thresh, detail=0)
            code_text = '\n'.join(result)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        py_path = f"code_capture_{timestamp}.py"
        with open(py_path, "w") as f: f.write(code_text)

        qr_path = f"code_qr_{timestamp}.png"
        qr = qrcode.QRCode(version=25, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(code_text[:4000])
        qr.make(fit=True)
        qr.make_image(fill_color="#00ffff", back_color="#1a0033").save(qr_path)

        st.subheader("📋 Extracted Code")
        st.code(code_text, language="python")
        st.image(qr_path, caption="Neon QR Code")
        st.success(f"✅ Saved {py_path} + QR")
        if st.button("📋 Copy for Grok", key=timestamp):
            st.code(code_text)

st.info("👆 Tap Share → 'Add to Home Screen' on your phone for full app experience!")
