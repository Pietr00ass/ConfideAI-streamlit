import os
import hashlib
import secrets
import logging
import json
import spacy
import pytesseract
import cv2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac

# Configure logging
logging.basicConfig(filename='operations.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# OCR image load
def load_image(file_path):
    image = cv2.imread(file_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang='pol')
    return text.strip(), image

# Anonymize image data
def anonymize_image(image_path):
    text, image = load_image(image_path)
    nlp = spacy.load("ner_model")
    doc = nlp(text)
    for ent in doc.ents:
        boxes = pytesseract.image_to_boxes(image, lang='pol').splitlines()
        for box in boxes:
            box_data = box.split()
            if len(box_data) == 6:
                char, x, y, w, h = box_data[0], int(box_data[1]), int(box_data[2]), int(box_data[3]), int(box_data[4])
                if ent.text.find(char) != -1:
                    cv2.rectangle(image, (x, image.shape[0] - y), (w, image.shape[0] - h), (0, 0, 0), -1)
    anonymized_path = image_path.replace('.', '_anonimized.')
    cv2.imwrite(anonymized_path, image)
    return anonymized_path

# Generate file ID (hash)
def generate_file_id(file_path):
    hash_func = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_func.update(chunk)
    file_id = hash_func.digest()
    logging.info(f"Generated file ID: {file_id.hex()}")
    return file_id

# Delete file
def delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
        logging.info(f"Deleted file: {file_path}")

# Encrypt file
def encrypt_file(file_path, compress=False, password=None, use_rsa=False, delete_original=False):
    logging.info(f"Starting encryption: {file_path}")
    key = secrets.token_bytes(32)
    iv = secrets.token_bytes(16)
    with open(file_path, "rb") as f:
        plaintext = f.read()
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    encrypted_path = file_path + ".enc"
    with open(encrypted_path, "wb") as f:
        f.write(iv + ciphertext)
    hmac_key = secrets.token_bytes(32)
    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
    h.update(ciphertext)
    hmac_digest = h.finalize()
    with open(encrypted_path + ".hmac", "wb") as f:
        f.write(hmac_digest)
    file_id = generate_file_id(file_path)
    key_path = file_path + ".key"
    with open(key_path, "wb") as f:
        f.write(file_id + key + hmac_key)
    if delete_original:
        delete_file(file_path)
    return encrypted_path, key_path

# Decrypt file
def decrypt_file(file_path, key_path, password=None, use_rsa=False, delete_keys=False, delete_encrypted=False):
    logging.info(f"Starting decryption: {file_path}")
    if not os.path.isfile(file_path) or not os.path.isfile(key_path):
        return None
    with open(key_path, "rb") as f:
        file_id = f.read(32)
        key = f.read(32)
        hmac_key = f.read(32)
    data = open(file_path, "rb").read()
    iv = data[:16]
    encrypted_data = data[16:]
    hmac_digest = open(file_path + ".hmac", "rb").read()
    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
    h.update(encrypted_data)
    h.verify(hmac_digest)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
    decrypted_path = file_path.replace(".enc", "")
    with open(decrypted_path, "wb") as f:
        f.write(decrypted)
    if delete_keys:
        delete_file(key_path)
        delete_file(file_path + ".hmac")
    if delete_encrypted:
        delete_file(file_path)
    return decrypted_path

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register user
def register_user(username, password):
    users_file = "users.json"
    data = {"users": []}
    if os.path.exists(users_file):
        data = json.load(open(users_file, "r"))
    for u in data["users"]:
        if u["username"] == username:
            return False
    data["users"].append({"username": username, "password_hash": hash_password(password)})
    json.dump(data, open(users_file, "w"), indent=4)
    return True

# Login user
def login_user(username, password):
    users_file = "users.json"
    if not os.path.exists(users_file):
        return False
    data = json.load(open(users_file, "r"))
    for u in data["users"]:
        if u["username"] == username and u["password_hash"] == hash_password(password):
            return True
    return False
