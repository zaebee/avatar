import os
import logging
import requests
import json
import time

S3_BUCKET = os.environ.get('S3_BUCKET', '')
S3_ENDPOINT = os.environ.get('S3_ENDPOINT', 'https://storage.yandexcloud.net')

logger = logging.getLogger(__name__)

SA_KEY_JSON = os.environ.get('SA_KEY_JSON', '')


def get_iam_token():
    """Get IAM token from metadata or SA key."""
    # First try metadata service
    try:
        response = requests.get(
            'http://169.254.169.254/metadata/v1/iam_token',
            headers={'Metadata-Flavor': 'Google'},
            timeout=3
        )
        if response.status_code == 200:
            try:
                data = response.json()
                return data.get('access_token', '')
            except:
                pass
    except Exception as e:
        logger.debug(f"Metadata: {e}")
    
    # Try using SA key from environment
    if SA_KEY_JSON:
        try:
            sa_key = json.loads(SA_KEY_JSON)
            private_key = sa_key.get('private_key', '')
            
            if private_key:
                import base64
                import jwt
                
                now = int(time.time())
                token_payload = {
                    "iss": sa_key.get('service_account_id'),
                    "sub": sa_key.get('service_account_id'),
                    "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
                    "iat": now,
                    "exp": now + 3600
                }
                
                # Sign JWT with private key
                jwt_token = jwt.encode(token_payload, private_key, algorithm="RS256")
                
                # Exchange for IAM token
                resp = requests.post(
                    "https://iam.api.cloud.yandex.net/iam/v1/tokens",
                    json={"jwt": jwt_token},
                    timeout=10
                )
                
                if resp.status_code == 200:
                    return resp.json().get('iamToken', '')
                    
        except Exception as e:
            logger.debug(f"SA key: {e}")
    
    return ''


def upload_image(image_data: bytes, filename: str) -> str:
    """Upload photo to Object Storage with IAM token."""
    iam_token = get_iam_token()
    if not iam_token:
        raise Exception("No IAM token")

    url = f"{S3_ENDPOINT}/{S3_BUCKET}/photos/{filename}"
    
    response = requests.put(
        url,
        data=image_data,
        headers={
            'Content-Type': 'image/jpeg',
            'Authorization': f'Bearer {iam_token}'
        },
        timeout=30
    )
    
    if response.status_code not in [200, 201, 204]:
        raise Exception(f"Upload failed: {response.status_code}")
    
    return f"{S3_ENDPOINT}/{S3_BUCKET}/photos/{filename}"


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    raise NotImplementedError()