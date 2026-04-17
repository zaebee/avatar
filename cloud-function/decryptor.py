import base64
import json
import os
import logging

logger = logging.getLogger(__name__)


def decrypt(encrypted_data: str, secret: str) -> dict:
    """
    Parse JSON from email body - for testing without encryption.
    """
    if not encrypted_data:
        raise ValueError("Empty data")
    
    encrypted_data = encrypted_data.strip()
    
    try:
        return json.loads(encrypted_data)
    except:
        pass
    
    try:
        decoded = base64.b64decode(encrypted_data)
        return json.loads(decoded.decode('utf-8'))
    except Exception as e:
        pass
    
    try:
        return {'text': encrypted_data[:1000], 'images': []}
    except:
        pass
    
    raise ValueError(f"Invalid data format")