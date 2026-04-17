import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from io import BytesIO
from config import S3_BUCKET, S3_ENDPOINT
import logging

logger = logging.getLogger(__name__)

s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    config=Config(signature_version='s3v4')
)


def upload_image(image_data: bytes, filename: str) -> str:
    """
    Загрузка фото в Object Storage.
    Возвращает публичный URL.
    """
    key = f"photos/{filename}"

    try:
        s3_client.upload_fileobj(
            BytesIO(image_data),
            S3_BUCKET,
            key,
            ExtraArgs={
                'ContentType': 'image/jpeg',
                'ACL': 'public-read'
            }
        )
        url = f"https://storage.yandexcloud.net/{S3_BUCKET}/{key}"
        logger.info(f"Uploaded: {url}")
        return url
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        raise


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Генерация pre-signed URL для временного доступа."""
    try:
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': key},
            ExpiresIn=expires_in
        )
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise