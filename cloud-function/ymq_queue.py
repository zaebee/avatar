import json
import os
import logging
import requests
import hashlib
import hmac
import base64
from datetime import datetime

MQ_QUEUE = os.environ.get('MQ_QUEUE', 'asi-one-instagram-posts')
FOLDER_ID = "b1gesh0suso3pvjrro56"
REGION = "ru-central1"

logger = logging.getLogger(__name__)


def get_iam_token():
    """Get IAM token from metadata service"""
    try:
        response = requests.get(
            'http://169.254.169.254/metadata/v1/iam_token',
            headers={'Metadata-Flavor': 'Google'},
            timeout=5
        )
        data = response.json()
        return data.get('access_token', '')
    except Exception as e:
        logger.error(f"Failed to get IAM token: {e}")
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