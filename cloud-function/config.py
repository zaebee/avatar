import os

SECRET = os.environ.get('SHARED_SECRET', '')
IMAP_HOST = os.environ.get('IMAP_HOST', 'imap.yandex.ru')
IMAP_USER = os.environ.get('IMAP_USER', '')
IMAP_PASSWORD = os.environ.get('IMAP_PASSWORD', '')
S3_BUCKET = os.environ.get('S3_BUCKET', '')
S3_ENDPOINT = os.environ.get('S3_ENDPOINT', 'https://storage.yandexcloud.net')
MQ_QUEUE = os.environ.get('MQ_QUEUE', '')
ASI_ONE_URL = os.environ.get('ASI_ONE_URL', 'https://api.asi1.ai/v1/chat/completions')
ASI_ONE_KEY = os.environ.get('ASI_ONE_KEY', '')