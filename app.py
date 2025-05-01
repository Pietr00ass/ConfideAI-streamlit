import streamlit as st
import os
from functions import encrypt_file, decrypt_file, register_user, login_user

# Flag controlling whether to show landing or main app
def show_landing():
    # Inject CSS from static_site/style.css
    css_path = os.path.join('static_site', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    # Inject body HTML from static_site/index.html
    html_path = os.path.join('static_site', 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        # Extract body content
        body = html.split('<body>')[1].split('</body>')[0]
        st.markdown(body, unsafe_allow_html=True)
    # Button to enter app
    if st.button("Rozpocznij teraz"):
        st.session_state.show_app = True
        st.experimental_rerun()

# Authentication pages
def login_page():
    st.title("Login & Register")
    choice = st.selectbox("Select option", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if choice == "Login" and st.button("Login"):
        if login_user(username, password):
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")
    if choice == "Register" and st.button("Register"):
        if register_user(username, password):
            st.success("Registered successfully! Please log in.")
        else:
            st.error("User already exists.")

# Main encryption/decryption UI
def main_app():
    st.title("File Encryption & Decryption")
    action = st.selectbox("Action", ["Encrypt", "Decrypt"])
    if action == "Encrypt":
        uploaded = st.file_uploader("Upload file to encrypt")
        delete_orig = st.checkbox("Delete original after encrypting")
        if uploaded and st.button("Encrypt"):
            path = os.path.join("uploads", uploaded.name)
            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())
            enc_path, key_path = encrypt_file(path, delete_original=delete_orig)
            if enc_path:
                st.download_button("Download encrypted file", open(enc_path, "rb"), os.path.basename(enc_path))
                st.download_button("Download key file", open(key_path, "rb"), os.path.basename(key_path))
    else:
        enc_file = st.file_uploader("Upload encrypted file (.enc)", type=["enc"])
        key_file = st.file_uploader("Upload key file (.key)" , type=["key"])
        delete_enc = st.checkbox("Delete .enc after decrypting")
        if enc_file and key_file and st.button("Decrypt"):
            enc_path = os.path.join("uploads", enc_file.name)
            key_path = os.path.join("uploads", key_file.name)
            with open(enc_path, "wb") as f:
                f.write(enc_file.getbuffer())
            with open(key_path, "wb") as f:
                f.write(key_file.getbuffer())
            # Validate HMAC
            if not os.path.exists(enc_path + ".hmac"):
                st.error("Missing HMAC file (.hmac). Ensure it was generated during encryption.")
            else:
                dec_path = decrypt_file(enc_path, key_path, delete_encrypted=delete_enc)
                if dec_path:
                    st.download_button("Download decrypted file", open(dec_path, "rb"), os.path.basename(dec_path))
                else:
                    st.error("Decryption failed.")

# Initialize session state
def initialize():
    if 'show_app' not in st.session_state:
        st.session_state.show_app = False
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

# Entry point
initialize()
if not st.session_state.show_app:
    show_landing()
elif st.session_state.authenticated:
    main_app()
else:
    login_page()
