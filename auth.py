import json
import logging
import os
import pickle

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES

logger = logging.getLogger(__name__)


def get_service():
    """Return an authenticated Search Console API service object.

    Priority:
      1. GOOGLE_SERVICE_ACCOUNT_JSON env var — used in GitHub Actions / Streamlit Cloud.
      2. OAuth2 token file — used for local development after first browser consent.
    """
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        logger.info("Authenticating via service account (GOOGLE_SERVICE_ACCOUNT_JSON)")
        info = json.loads(sa_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        return build("searchconsole", "v1", credentials=creds)

    # OAuth2 fallback for local dev
    logger.info("Service account env var not set — falling back to OAuth2 token")
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as fh:
            creds = pickle.load(fh)
        logger.debug("Loaded OAuth2 token from %s", TOKEN_FILE)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("OAuth2 token expired — refreshing")
            creds.refresh(Request())
            logger.info("OAuth2 token refreshed successfully")
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "No credentials found. Either:\n"
                    "  • Set GOOGLE_SERVICE_ACCOUNT_JSON env var (CI / Streamlit Cloud), or\n"
                    f"  • Place OAuth client secrets at '{CREDENTIALS_FILE}' (local dev)"
                )
            logger.info("No valid token found — starting browser OAuth2 flow")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info("OAuth2 flow complete")

        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "wb") as fh:
            pickle.dump(creds, fh)
        logger.debug("Saved OAuth2 token to %s", TOKEN_FILE)

    return build("searchconsole", "v1", credentials=creds)
