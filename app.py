import streamlit as st
import os
from functions import encrypt_file, decrypt_file
from auth import (
    send_verification_email, confirm_email_token,
    get_google_auth_url, fetch_google_user,
    generate_totp_secret, get_totp_qr_uri, verify_totp
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Landing page
def show_landing():
    css_path = os.path.join('static_site', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    html_path = os.path.join('static_site', 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        body = html.split('<body>')[1].split('</body>')[0]
        st.markdown(body, unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; margin-top:2rem;'>", unsafe_allow_html=True)
    if st.button('Rozpocznij teraz'):
        st.session_state.page = 'auth'
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Authentication / Registration with styled panel
def auth_page():
    # Inline CSS for auth panel
    st.markdown("""
    <style>
    .auth-card {max-width:400px;margin:4rem auto;background:#fff;padding:2rem;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.2);color:#000;}
    .auth-card input {width:100%;padding:0.5rem;margin-bottom:1rem;border:1px solid #ccc;border-radius:4px;}
    .auth-btn {width:100%;padding:0.75rem;border:none;border-radius:4px;font-size:1rem;cursor:pointer;margin-bottom:0.5rem;background:#007bff;color:#fff;}
    .google-btn {width:100%;padding:0.75rem;border:1px solid #ccc;border-radius:4px;font-size:1rem;cursor:pointer;background:#fff;color:#333;display:flex;align-items:center;justify-content:center;margin-bottom:0.5rem;}
    .google-btn img {height:20px;margin-right:8px;}
    .separator {text-align:center;margin:1rem 0;position:relative;color:#666;}
    .separator:before, .separator:after {content:"";position:absolute;top:50%;width:45%;height:1px;background:#ccc;}
    .separator:before {left:0;}
    .separator:after {right:0;}
    .separator span {background:#fff;padding:0 0.5rem;position:relative;}
    a {color:#007bff;text-decoration:none;}
    a:hover {text-decoration:underline;}
    </style>
    <div class='auth-card'>
      <h2 style='text-align:center;'>Witaj</h2>
      <p style='text-align:center;color:#666;'>Zaloguj się do ConfideAI, aby kontynuować</p>
    """, unsafe_allow_html=True)

    # Email & password inputs
    email = st.text_input('', placeholder='Adres e-mail')
    password = st.text_input('', placeholder='Hasło', type='password')
    if st.button('Kontynuuj', key='auth_continue'):
        # TODO: handle email/password login
        pass

    # Forgot password link
    st.markdown("<p style='text-align:right;'><a href='#'>Nie pamiętasz hasła?</a></p>", unsafe_allow_html=True)
    # Registration link
    st.markdown(
        "<p style='text-align:center;'>Nie masz konta? <a href='#' id='register-link'>Zarejestruj się</a></p>",
        unsafe_allow_html=True
    )
    # Separator
    st.markdown("<div class='separator'><span>LUB</span></div>", unsafe_allow_html=True)
    # Google login button
    google_btn_html = (
        "<div><button class='google-btn'>"
        "<img src='https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg'/> "
        "Kontynuuj z Google</button></div>"
    )
    st.markdown(google_btn_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Fallback login placeholder
def login_page():
    st.title('🔑 Logowanie e-mail')
    st.info('Najpierw potwierdź e-mail w rejestracji.')

# Main app
def main_app():
    st.title('File Encryption & Decryption')
    action = st.selectbox('Action', ['Encrypt', 'Decrypt'])
    # existing logic...
    
# Routing logic
if st.session_state.page == 'landing':
    show_landing()
elif st.session_state.page == 'auth':
    auth_page()
elif st.session_state.authenticated:
    main_app()
else:
    show_landing()
