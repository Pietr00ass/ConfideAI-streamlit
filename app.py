import streamlit as st
import os
from functions import encrypt_file, decrypt_file
from auth import (
    send_verification_email, confirm_email_token,
    get_google_auth_url, fetch_google_user,
    generate_totp_secret, get_totp_qr_uri, verify_totp
)

# Initialize session
if 'next' not in st.session_state:
    st.session_state.next = 'landing'
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Landing page
def show_landing():
    # Inject CSS
    css_path = os.path.join('static_site', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    # Inject HTML body
    html_path = os.path.join('static_site', 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        body = html.split('<body>')[1].split('</body>')[0]
        st.markdown(body, unsafe_allow_html=True)
    # Button to proceed
    if st.button('Rozpocznij teraz'):
        st.session_state.next = 'auth'
        st.experimental_rerun()

# Authentication / Registration page
def auth_page():
    st.title('🔐 Autoryzacja i Rejestracja')
    mode = st.selectbox('Wybierz metodę:', [
        'Zaloguj przez Google',
        '2FA Google Authenticator',
        'Rejestracja e-mail'
    ])

    # Google OAuth2 login
    if mode == 'Zaloguj przez Google':
        auth_url = get_google_auth_url()
        st.markdown(f"[Zaloguj się przez Google]({auth_url})")
        params = st.experimental_get_query_params()
        if 'code' in params:
            user_info = fetch_google_user(params)
            st.success(f"Witaj, {user_info['email']}!")
            st.session_state.authenticated = True
            st.session_state.next = 'app'
            st.experimental_rerun()

    # Google Authenticator 2FA
    elif mode == '2FA Google Authenticator':
        email = st.text_input('Adres e-mail (dla TOTP)')
        if st.button('Wygeneruj QR kod'):
            secret = generate_totp_secret()
            uri = get_totp_qr_uri(secret, email)
            st.image(f"https://api.qrserver.com/v1/create-qr-code/?data={uri}&size=200x200")
            st.session_state.totp_secret = secret
        token = st.text_input('Kod z aplikacji Authenticator', max_chars=6)
        if st.button('Zweryfikuj 2FA'):
            if verify_totp(token, st.session_state.get('totp_secret', '')):
                st.success('2FA zweryfikowane!')
                st.session_state.authenticated = True
                st.session_state.next = 'app'
                st.experimental_rerun()
            else:
                st.error('Niepoprawny kod.')

    # Email registration with verification
    else:
        email = st.text_input('Adres e-mail')
        if st.button('Zarejestruj e-mail'):
            send_verification_email(email)
            st.info('Sprawdź swoją skrzynkę i kliknij link weryfikacyjny.')
        params = st.experimental_get_query_params()
        if 'confirm_email' in params:
            user = confirm_email_token(params['confirm_email'][0])
            if user:
                st.success('E-mail potwierdzony! Możesz się teraz zalogować.')
                st.session_state.next = 'landing'
                st.experimental_rerun()
            else:
                st.error('Link wygasł lub jest niepoprawny.')

# Login/Registration fallback (after email verification)
def login_page():
    st.title('🔑 Logowanie')
    username = st.text_input('Login')
    password = st.text_input('Hasło', type='password')
    if st.button('Zaloguj'):
        # placeholder: implement username/password check
        st.error('Ta opcja jeszcze niezaimplementowana.')

# Main application
def main_app():
    st.title('File Encryption & Decryption')
    action = st.selectbox('Action', ['Encrypt', 'Decrypt'])
    if action == 'Encrypt':
        uploaded = st.file_uploader('Upload file to encrypt')
        delete_orig = st.checkbox('Delete original after encrypting')
        if uploaded and st.button('Encrypt'):
            path = os.path.join('uploads', uploaded.name)
            with open(path, 'wb') as f:
                f.write(uploaded.getbuffer())
            enc_path, key_path = encrypt_file(path, delete_original=delete_orig)
            if enc_path:
                st.download_button('Download encrypted file', open(enc_path, 'rb'), os.path.basename(enc_path))
                st.download_button('Download key file', open(key_path, 'rb'), os.path.basename(key_path))
    else:
        enc_file = st.file_uploader('Upload encrypted file (.enc)', type=['enc'])
        key_file = st.file_uploader('Upload key file (.key)', type=['key'])
        delete_enc = st.checkbox('Delete .enc after decrypting')
        if enc_file and key_file and st.button('Decrypt'):
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
                    st.download_button('Download decrypted file', open(dec_path, 'rb'), os.path.basename(dec_path))
                else:
                    st.error('Decryption failed.')

# Routing logic
if st.session_state.next == 'landing':
    show_landing()
elif st.session_state.next == 'auth':
    auth_page()
elif st.session_state.authenticated:
    main_app()
else:
    login_page()
