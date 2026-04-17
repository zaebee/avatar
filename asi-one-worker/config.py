import os
import logging

MQ_QUEUE = os.environ.get('MQ_QUEUE', '')
INSTAGRAM_ACCOUNT = os.environ.get('INSTAGRAM_ACCOUNT', '@zaebuntu')
ASI_ONE_URL = os.environ.get('ASI_ONE_URL', 'https://api.asi1.ai/v1/chat/completions')
ASI_ONE_KEY = os.environ.get('ASI_ONE_KEY', '')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)