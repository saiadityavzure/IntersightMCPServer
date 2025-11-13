# utils/intersight_rest.py

import os
import re
import logging
from dotenv import load_dotenv
from requests import Session

# Load environment variables
load_dotenv()

from intersight_auth import IntersightAuth  

logger = logging.getLogger(__name__)

# Build BASE_DIR similar to SDK file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SECRET_PATH = os.path.join(BASE_DIR, "NSDev01-SecretKey.txt")

# Load .env values
INTERSIGHT_API_KEY = os.getenv("INTERSIGHT_API_KEY")
INTERSIGHT_SECRET_FILE_PATH = os.getenv("INTERSIGHT_SECRET_FILE_PATH", DEFAULT_SECRET_PATH)
INTERSIGHT_ENDPOINT = os.getenv("INTERSIGHT_ENDPOINT", "https://intersight.com/api/v1")


def get_intersight_rest_session(api_key_id=None, api_secret_path=None, endpoint=None, proxy=None):
    """
    Creates a signed REST Session using IntersightAuth.

    Returns:
        requests.Session ready to make authenticated REST calls.
    """

    api_key_id = api_key_id or INTERSIGHT_API_KEY
    api_secret_path = api_secret_path or INTERSIGHT_SECRET_FILE_PATH
    endpoint = endpoint or INTERSIGHT_ENDPOINT.replace("/api/v1", "")

    logger.info(f"Creating REST session @ {endpoint}")

    if not api_key_id or not api_secret_path:
        raise ValueError("Missing Intersight credentials for REST Session")

    # Create a signed REST session
    session = Session()

    session.auth = IntersightAuth(
        secret_key_filename=api_secret_path,
        api_key_id=api_key_id
    )

    # Configure proxy if needed
    if proxy:
        session.proxies = {
            "http": proxy,
            "https": proxy
        }

    # Add default headers
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json"
    })

    return session, endpoint


def test_rest_connection():
    """
    Lightweight call to verify the REST session works.
    Equivalent to GET /iam/Accounts
    """

    session, endpoint = get_intersight_rest_session()
    url = f"{endpoint}/api/v1/iam/Accounts"

    try:
        response = session.get(url)
        response.raise_for_status()

        logger.info("✅ REST authentication successful")
        return response.json()
    except Exception as ex:
        logger.error(f"❌ REST auth failed: {ex}")
        return {"error": str(ex)}
