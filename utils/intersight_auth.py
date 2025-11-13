from dotenv import load_dotenv
load_dotenv()
import os
import intersight
import re
# from intersight.api.iam_api import IamApi
import traceback
import logging
logger = logging.getLogger(__name__)

from intersight.api import iam_api


logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SECRET_PATH = os.path.join(BASE_DIR, "NSDev01-SecretKey.txt")


INTERSIGHT_API_KEY = os.getenv("INTERSIGHT_API_KEY")
INTERSIGHT_SECRET_FILE_PATH = os.getenv("INTERSIGHT_SECRET_FILE_PATH", DEFAULT_SECRET_PATH)
INTERSIGHT_ENDPOINT = os.getenv("INTERSIGHT_ENDPOINT", "https://intersight.com/api/v1")



def get_intersight_api_client(api_key_id, api_secret_path, endpoint):
    logger.info("Entering in get_intersight_api_client.")
    with open(api_secret_path, 'r') as f:
        api_secret_key = f.read()

    # API Key v2 format
    if re.search('BEGIN RSA PRIVATE KEY', api_secret_key):
        signing_algorithm = intersight.signing.ALGORITHM_RSASSA_PKCS1v15
        signing_scheme = intersight.signing.SCHEME_RSA_SHA256
        hash_algorithm = intersight.signing.HASH_SHA256

    # API Key v3 format
    elif re.search('BEGIN EC PRIVATE KEY', api_secret_key):
        signing_algorithm = intersight.signing.ALGORITHM_ECDSA_MODE_DETERMINISTIC_RFC6979
        signing_scheme = intersight.signing.SCHEME_HS2019
        hash_algorithm = intersight.signing.HASH_SHA256
    try:
        configuration = intersight.Configuration(
            host=endpoint,
            signing_info=intersight.signing.HttpSigningConfiguration(
                key_id=api_key_id,
                private_key_path=api_secret_path,
                signing_scheme=signing_scheme,
                signing_algorithm=signing_algorithm,
                hash_algorithm=hash_algorithm,
                signed_headers=[
                    intersight.signing.HEADER_REQUEST_TARGET,
                    intersight.signing.HEADER_HOST,
                    intersight.signing.HEADER_DATE,
                    intersight.signing.HEADER_DIGEST,
                ]
            )
        )
    except Exception as err:
        logger.exception(
            "Intersight API connection is not successful. Reason: Unauthorized", stack_info=True)
    return intersight.ApiClient(configuration)

def intersight_client_connection():  
    logger.info("Extracting Intersight_client_connection.")
    api_intersight_client = get_intersight_api_client(INTERSIGHT_API_KEY, INTERSIGHT_SECRET_FILE_PATH, endpoint="https://www.intersight.com")

    # Perform a lightweight test to validate credentials
    try:
        account_api = iam_api.IamApi(api_intersight_client)
        account_info = account_api.get_iam_account_list(top=1)
        logger.info("✅ Intersight client authentication successful.")
    except intersight.exceptions.ApiException as e:
        if e.status == 401:
            logger.error("❌ Authentication failed: Unauthorized (401). Check API key and secret.")
        elif e.status == 403:
            logger.error("❌ Access forbidden (403). API key may lack necessary permissions.")
        elif e.status == 400:
            logger.error("❌ Bad request (400). Possibly malformed auth headers or key.")
        else:
            logger.error(f"❌ API exception during client validation: {e}")
    except Exception as ex:
        logger.error(f"❌ Unexpected error during client validation: {traceback.format_exc()}")

    return api_intersight_client