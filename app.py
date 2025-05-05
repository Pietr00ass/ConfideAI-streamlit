import streamlit as st
import os
from functions import encrypt_file, decrypt_file
from auth import get_authorization_url, fetch_user_info

# --- INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ''

# Handle OAuth2 callback
params = st.query_params
if 'code' in params and 'state' in params:
    code = params['code'][0]
    state = params['state'][0]
    user_info = fetch_user_info(code, state)
    st.session_state.authenticated = True
    st.session_state.user_email = user_info.get('email', '')
    # Clear query params to avoid re-trigger
    st.experimental_set_query_params()

# --- LANDING PAGE ---
def show_landing():
    # Inject external CSS
    css_path = os.path.join('static_site', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # Render body from static HTML
    html_path = os.path.join('static_site', 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # Extract <body> content
        try:
            body = html_content.split('<body>')[1].split('</body>')[0]
            st.markdown(body, unsafe_allow_html=True)
        except IndexError:
            st.error("Error loading landing page HTML body.")

    # Fallback button
    if st.button("Rozpocznij teraz", key="landing_btn"):
        st.session_state.page = 'auth'

# --- AUTH PAGE ---
def auth_page():
    st.title("🔐 Zaloguj się przez Google")
    auth_url, state = get_authorization_url()
    st.session_state.state = state
    # Styled link button
    st.markdown(
        f"<a href='{auth_url}' style='text-decoration:none;'>"
        f"<button style='padding:0.75rem 1.5rem; font-size:1rem; background:#4285F4; color:#fff; border:none; border-radius:4px;'>"
        f"Kontynuuj z Google</button></a>",
        unsafe_allow_html=True
    )

# --- MAIN APP ---
def main_app():
    st.header(f"Witaj, {st.session_state.user_email}")
    st.title("File Encryption & Decryption")
    action = st.selectbox('Action', ['Encrypt', 'Decrypt'])
    if action == 'Encrypt':
        uploaded = st.file_uploader('Upload file to encrypt')
        delete_orig = st.checkbox('Delete original after encrypting')
        if uploaded and st.button('Encrypt', key='encrypt_btn'):
            path = os.path.join('uploads', uploaded.name)
            with open(path, 'wb') as f:
                f.write(uploaded.getbuffer())
            enc_path, key_path = encrypt_file(path, delete_original=delete_orig)
            if enc_path:
                st.download_button('Pobierz zaszyfrowany plik', open(enc_path, 'rb'), os.path.basename(enc_path))
                st.download_button('Pobierz klucz', open(key_path, 'rb'), os.path.basename(key_path))
    else:
        enc_file = st.file_uploader('Upload encrypted file (.enc)', type=['enc'])
        key_file = st.file_uploader('Upload key file (.key)', type=['key'])
        delete_enc = st.checkbox('Delete .enc after decrypting')
        if enc_file and key_file and st.button('Decrypt', key='decrypt_btn'):
            enc_path = os.path.join('uploads', enc_file.name)
            key_path = os.path.join('uploads', key_file.name)
            with open(enc_path, 'wb') as f:
                f.write(enc_file.getbuffer())
            with open(key_path, 'wb') as f:
                f.write(key_file.getbuffer())
            if not os.path.exists(enc_path + '.hmac'):
                st.error('Missing HMAC file (.hmac).')
            else:
                dec_path = decrypt_file(enc_path, key_path, delete_encrypted=delete_enc)
                if dec_path:
                    st.download_button('Pobierz odszyfrowany plik', open(dec_path, 'rb'), os.path.basename(dec_path))
                else:
                    st.error('Decryption failed.')

# --- ROUTING ---
if st.session_state.authenticated:
    main_app()
elif st.session_state.page == 'auth':
    auth_page()
else:
    show_landing()
