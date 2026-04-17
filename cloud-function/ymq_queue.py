import json
import os
import logging
import requests
import time

MQ_QUEUE = os.environ.get('MQ_QUEUE', 'asi-one-instagram-posts')
FOLDER_ID = "b1gesh0suso3pvjrro56"

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
            import jwt
            import base64
            
            sa_key = json.loads(SA_KEY_JSON)
            private_key = sa_key.get('private_key', '')
            
            if private_key:
                now = int(time.time())
                token_payload = {
                    "iss": sa_key.get('service_account_id'),
                    "sub": sa_key.get('service_account_id'),
                    "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
                    "iat": now,
                    "exp": now + 3600
                }
                
                jwt_token = jwt.encode(token_payload, private_key, algorithm="RS256")
                
                resp = requests.post(
                    "https://iam.api.cloud.yandex.net/iam/v1/tokens",
                    json={"jwt": jwt_token},
                    timeout=10
                )
                
                if resp.status_code == 200:
                    return resp.json().get('iamToken', '')
                    
        except Exception as e:
            logger.error(f"SA key failed: {e}")
    
    return ''


def publish_to_queue(payload: dict) -> bool:
    """
    Publish to YMQ using HTTP API with IAM token.
    YMQ uses SQS-compatible API format.
    """
    try:
        iam_token = get_iam_token()
        if not iam_token:
            logger.error("No IAM token available - cannot publish to queue")
            return False

        # SQS-compatible endpoint format
        queue_url = f"https://message-queue.api.cloud.yandex.net/{FOLDER_ID}/{MQ_QUEUE}"
        
        # Build SQS-compatible request - use URL query params instead
        message_body = json.dumps(payload)
        
        # SendMessage action as query parameter
        url = f"{queue_url}/?Action=SendMessage&Version=2012-11-05"
        
        response = requests.post(
            url,
            data=message_body,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {iam_token}'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("Published to queue via IAM")
            return True
        
        logger.warning(f"Queue publish failed: {response.status_code} - {response.text[:200]}")
        return False
        
    except Exception as e:
        logger.error(f"Failed to publish: {e}")
        return False