import os
from authlib.integrations.requests_client import OAuth2Session

# Load Google OAuth2 credentials from env
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("APP_URL")  # e.g. https://confideai-streamlit-production.up.railway.app

# OAuth2 endpoints
AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_authorization_url():
    """
    Create Google OAuth2 authorization URL and state.
    Returns (authorization_url, state)
    """
    oauth = OAuth2Session(
        CLIENT_ID,
        CLIENT_SECRET,
        scope="openid email profile",
        redirect_uri=REDIRECT_URI
    )
    url, state = oauth.create_authorization_url(
        AUTHORIZATION_ENDPOINT,
        access_type="offline",
        prompt="consent"
    )
    return url, state


def fetch_user_info(code: str, state: str) -> dict:
    """
    Exchange authorization code for tokens and fetch user info.
    """
    oauth = OAuth2Session(
        CLIENT_ID,
        CLIENT_SECRET,
        scope="openid email profile",
        redirect_uri=REDIRECT_URI,
        state=state
    )
    # Exchange code for token
    token = oauth.fetch_token(
        TOKEN_ENDPOINT,
        code=code
    )
    # Get user info
    resp = oauth.get(USERINFO_ENDPOINT)
    return resp.json()
