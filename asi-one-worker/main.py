import json
import logging
import os
import requests
import base64
import hmac
import hashlib
from datetime import datetime

from config import MQ_QUEUE, INSTAGRAM_ACCOUNT, ASI_ONE_URL, ASI_ONE_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
                            'description': 'Опубликовать пост в Instagram',
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'text': {'type': 'string', 'description': 'Текст поста'},
                                    'images': {'type': 'array', 'description': 'URL изображений'}
                                },
                                'required': ['text']
                            }
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


def handler(event, context):
    """
    Cloud Function handler для asi:one worker.
    Триггер: Yandex Message Queue Trigger.
    """
    logger.info(f"Starting asi:one worker with event: {json.dumps(event)[:200]}")
    
    if not ASI_ONE_KEY:
        logger.error("ASI_ONE_KEY not configured")
        return {'statusCode': 500, 'body': 'asi:one key not configured'}

    # YMQ trigger sends messages in event['messages']
    messages = event.get('messages', [])
    
    if not messages:
        logger.info("No messages in event")
        return {'statusCode': 200, 'body': 'No messages'}
    
    logger.info(f"Received {len(messages)} messages")
    
    processed = 0
    failed = 0
    
    for msg in messages:
        try:
            # YMQ trigger formats message as:
            # {"messages": [{"body": "...", "receiptHandle": "..."}]}
            # Or simple body
            
            body = msg.get('body', '{}')
            
            # Try to parse body
            try:
                if isinstance(body, str):
                    payload = json.loads(body)
                else:
                    payload = body
            except:
                payload = {'text': str(body), 'images': []}
            
            text = payload.get('text', '')
            images = payload.get('images', [])
            
            if not text:
                logger.warning("Empty text, skipping")
                continue
            
            logger.info(f"Processing post: {text[:50]}...")
            
            resp = call_asi_one(text, images)
            
            if resp.get('choices'):
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