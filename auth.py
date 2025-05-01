import os, json, smtplib, pyotp
from authlib.integrations.requests_client import OAuth2Session
from itsdangerous import URLSafeTimedSerializer
from email.message import EmailMessage

# ---- KONFIGURACJA ----
SECRET_KEY = os.getenv("SECRET_KEY", "zmień_to_na_bezpieczne")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")
BASE_URL = os.getenv("APP_URL", "https://confideai-streamlit-production.up.railway.app")

# do tokenów e-mail
serializer = URLSafeTimedSerializer(SECRET_KEY)

# ---- FUNKCJE EMAIL ----
def send_verification_email(recipient: str):
    token = serializer.dumps(recipient, salt="email-confirm")
    link = f"{BASE_URL}/?confirm_email={token}"
    msg = EmailMessage()
    msg["Subject"] = "Potwierdź swój adres e-mail w ConfideAI"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    msg.set_content(f"Kliknij ten link, aby aktywować konto:\n\n{link}")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASS)
        smtp.send_message(msg)

def confirm_email_token(token: str, expiration=3600):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=expiration)
        return email
    except Exception:
        return None

# ---- GOOGLE OAUTH2 ----
def get_google_oauth_session():
    # w credentials/client_secret.json masz client_id, client_secret
    conf = json.load(open("credentials/client_secret.json"))
    return OAuth2Session(
        client_id=conf["installed"]["client_id"],
        client_secret=conf["installed"]["client_secret"],
        scope="openid email profile",
        redirect_uri=f"{BASE_URL}/?google_auth=1"
    )

def get_google_auth_url():
    oauth = get_google_oauth_session()
    return oauth.create_authorization_url(conf["installed"]["auth_uri"])[0]

def fetch_google_user(token_response):
    oauth = get_google_oauth_session()
    oauth.fetch_token(
        token_endpoint=conf["installed"]["token_uri"],
        code=token_response["code"]
    )
    return oauth.get("https://www.googleapis.com/oauth2/v3/userinfo").json()

# ---- TOTP (Google Authenticator) ----
def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_qr_uri(secret, user_email):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=user_email, issuer_name="ConfideAI")

def verify_totp(token, secret):
    return pyotp.TOTP(secret).verify(token)
