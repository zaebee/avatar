import json
import boto3
from botocore.exceptions import ClientError
from config import MQ_QUEUE
import logging

logger = logging.getLogger(__name__)

sqs = boto3.client(
    'sqs',
    endpoint_url='https://message-queue.api.cloud.yandex.net',
    region_name='ru-central1'
)


def publish_to_queue(payload: dict) -> bool:
    """
    Публикация сообщения в очередь Yandex MQ.
    """
    try:
        response = sqs.send_message(
            QueueUrl=get_queue_url(),
            MessageBody=json.dumps(payload),
            MessageGroupId='asi-one-instagram'
        )
        logger.info(f"Published to queue: {response['MessageId']}")
        return True
    except ClientError as e:
        logger.error(f"Failed to publish to queue: {e}")
        return False


def get_queue_url() -> str:
    """Получение URL очереди по имени."""
    try:
        response = sqs.get_queue_url(QueueName=MQ_QUEUE)
        return response['QueueUrl']
    except ClientError as e:
        logger.error(f"Failed to get queue URL: {e}")
        raise