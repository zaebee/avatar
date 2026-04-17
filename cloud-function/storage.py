import os
import logging

S3_BUCKET = os.environ.get('S3_BUCKET', '')
S3_ENDPOINT = os.environ.get('S3_ENDPOINT', 'https://storage.yandexcloud.net')

logger = logging.getLogger(__name__)


def upload_image(image_data: bytes, filename: str) -> str:
    """
    Загрузка фото в Object Storage через REST API.
    """
    try:
        import requests
        
        url = f"{S3_ENDPOINT}/{S3_BUCKET}/photos/{filename}"
        
        response = requests.put(
            url,
            data=image_data,
            headers={'Content-Type': 'image/jpeg'},
            timeout=30
        )
        
        if response.status_code not in [200, 201, 204]:
            logger.error(f"S3 upload failed: {response.status_code} {response.text[:200]}")
            raise Exception(f"Upload failed: {response.status_code}")
        
        result_url = f"{S3_ENDPOINT}/{S3_BUCKET}/photos/{filename}"
        logger.info(f"Uploaded: {result_url}")
        return result_url
        
    except Exception as e:
        logger.error(f"S3 upload error: {e}")
        raise


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Генерация pre-signed URL для временного доступа."""
    raise NotImplementedError("Presigned URLs require boto3")