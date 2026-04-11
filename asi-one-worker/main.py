import json
import logging
import os
import requests
from botocore.exceptions import ClientError
from botocore.config import Config

import boto3

from config import MQ_QUEUE, INSTAGRAM_ACCOUNT, ASI_ONE_URL, ASI_ONE_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sqs = boto3.client(
    'sqs',
    endpoint_url='https://message-queue.api.cloud.yandex.net',
    region_name='ru-central1',
    config=Config(signature_version='s3v4')
)


def get_queue_url():
    """Получение URL очереди."""
    try:
        response = sqs.get_queue_url(QueueName=MQ_QUEUE)
        return response['QueueUrl']
    except ClientError as e:
        logger.error(f"Failed to get queue URL: {e}")
        raise


def call_asi_one(text: str, images: list) -> dict:
    """Вызов asi:one API для постинга в Instagram."""
    prompt = f"""Опубликуй пост в Instagram аккаунт {INSTAGRAM_ACCOUNT}.

Текст поста: {text}
Фото: {images}

Используй инструмент instagram для публикации."""

    try:
        response = requests.post(
            ASI_ONE_URL,
            headers={
                'Authorization': f'Bearer {ASI_ONE_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'asi1',
                'messages': [{'role': 'user', 'content': prompt}],
                'tools': [
                    {
                        'type': 'function',
                        'function': {
                            'name': 'instagram_post',
                            'description': 'Опубликовать пост в Instagram'
                        }
                    }
                ]
            },
            timeout=60
        )
        
        result = response.json()
        logger.info(f"asi:one response: {result}")
        return result
        
    except Exception as e:
        logger.error(f"asi:one API call failed: {e}")
        raise


def delete_from_queue(receipt_handle: str):
    """Удаление сообщения из очереди после успешной обработки."""
    try:
        sqs.delete_message(
            QueueUrl=get_queue_url(),
            ReceiptHandle=receipt_handle
        )
        logger.info("Message deleted from queue")
    except ClientError as e:
        logger.error(f"Failed to delete message: {e}")


def handler(event, context):
    """
    Cloud Function handler для asi:one worker.
    Триггер: Yandex Message Queue Trigger.
    """
    logger.info("Starting asi:one worker")
    
    if not ASI_ONE_KEY:
        logger.error("ASI_ONE_KEY not configured")
        return {'statusCode': 500, 'body': 'asi:one key not configured'}

    messages = event.get('messages', [])
    
    if not messages:
        logger.info("No messages in event")
        return {'statusCode': 200, 'body': 'No messages'}
    
    processed = 0
    failed = 0
    
    for msg in messages:
        receipt_handle = msg.get('receiptHandle', '')
        
        try:
            body = json.loads(msg.get('body', '{}'))
            
            text = body.get('text', '')
            images = body.get('images', [])
            
            if not text:
                logger.warning("Empty text, skipping")
                continue
            
            logger.info(f"Processing post: {text[:50]}...")
            
            resp = call_asi_one(text, images)
            
            if resp.get('choices'):
                delete_from_queue(receipt_handle)
                logger.info(f"Posted: {text[:50]}...")
                processed += 1
            else:
                logger.error(f"asi:one returned no choices: {resp}")
                failed += 1
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            failed += 1
    
    logger.info(f"Processed: {processed}, Failed: {failed}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': processed,
            'failed': failed
        })
    }