import json
import logging
import base64
import os

from imap_client import get_unread_emails
from decryptor import decrypt
from storage import upload_image
from ymq_queue import publish_to_queue
from config import SECRET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Override SECRET to avoid error when not set
if not SECRET:
    logger.warning("SHARED_SECRET not set - using debug mode")
    SECRET = "debug-secret"


def handler(event, context):
    """
    Cloud Function handler для IMAP-poller.
    Триггер: Cloud Scheduler каждые 5 минут.
    """
    logger.info("Starting IMAP poller")
    
    if not SECRET:
        logger.error("SHARED_SECRET not configured")
        return {'statusCode': 500, 'body': 'Shared secret not configured'}

    emails = get_unread_emails()
    logger.info(f"Found {len(emails)} emails to process")
    
    processed = 0
    failed = 0
    
    for email_data in emails:
        try:
            if not email_data.get('body'):
                logger.warning(f"Email {email_data.get('id')} has no body, skipping")
                continue
            
            payload = decrypt(email_data['body'], SECRET)
            
            image_urls = []
            for idx, img_data in enumerate(payload.get('images', [])):
                try:
                    img_bytes = base64.b64decode(img_data)
                    filename = f"{email_data.get('id', 'unknown')}_{idx}.jpg"
                    url = upload_image(img_bytes, filename)
                    image_urls.append(url)
                except Exception as e:
                    logger.error(f"Failed to upload image {idx}: {e}")
            
            queue_payload = {
                'text': payload.get('text', ''),
                'images': image_urls,
                'timestamp': payload.get('timestamp', ''),
                'from': email_data.get('from', '')
            }
            
            if publish_to_queue(queue_payload):
                logger.info(f"Queued post: {queue_payload['text'][:50]}...")
                processed += 1
            else:
                logger.error("Failed to publish to queue")
                failed += 1
                
        except Exception as e:
            logger.error(f"Failed to process email {email_data.get('id')}: {e}")
            failed += 1
    
    logger.info(f"Processed: {processed}, Failed: {failed}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': processed,
            'failed': failed
        })
    }