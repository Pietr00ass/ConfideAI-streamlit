import streamlit as st
import os
from functions import encrypt_file, decrypt_file, register_user, login_user

def login_page():
    st.title("Login & Register")
    login_choice = st.selectbox("Select option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if login_choice == "Login":
        if st.button("Login"):
            if login_user(username, password):
                st.session_state["authenticated"] = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials.")

    elif login_choice == "Register":
        if st.button("Register"):
            if register_user(username, password):
                st.success("Registered successfully! Please log in.")
            else:
                st.error("User already exists.")

def main_app():
    st.title("File Encryption & Decryption")

    action = st.selectbox("Action", ["Encrypt", "Decrypt"])
    uploaded_file = st.file_uploader("Upload file")
    delete_original = st.checkbox("Delete original after operation")

    if uploaded_file:
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if action == "Encrypt":
            if st.button("Encrypt"):
                encrypted_path, key_path = encrypt_file(file_path, delete_original=delete_original)
                st.download_button("Download encrypted file", open(encrypted_path, "rb"), os.path.basename(encrypted_path))
                st.download_button("Download key", open(key_path, "rb"), os.path.basename(key_path))

        else:
            key_file = st.file_uploader("Upload key", type="key")
            if key_file and st.button("Decrypt"):
                key_path = os.path.join("uploads", key_file.name)
                with open(key_path, "wb") as f:
                    f.write(key_file.getbuffer())

                decrypted_path = decrypt_file(file_path, key_path, delete_encrypted=delete_original)
                st.download_button("Download decrypted file", open(decrypted_path, "rb"), os.path.basename(decrypted_path))

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if st.session_state['authenticated']:
    main_app()
else:
    login_page()
