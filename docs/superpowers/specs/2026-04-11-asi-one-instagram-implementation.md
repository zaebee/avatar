# asi:one InstagramPoster — Детальная спека реализации

**Дата:** 2026-04-11  
**Версия:** 1.0 (на ревью)  
**Статус:** Draft

---

## 1. Web-encryptor (client-side)

### 1.1 Структура файлов

```
web-encryptor/
├── index.html      # UI + логика
└── README.md       # инструкция
```

### 1.2 HTML (index.html)

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>asi:one Encryptor</title>
  <style>
    /* минимальный CSS: шрифт, отступы, кнопка */
  </style>
</head>
<body>
  <h1>Шифратор для asi:one</h1>
  <textarea id="text" placeholder="Текст поста..."></textarea>
  <input type="file" id="photos" accept="image/*" multiple>
  <button id="encrypt">Зашифровать</button>
  <pre id="output"></pre>
  <script src="encryptor.js"></script>
</body>
</html>
```

### 1.3 JavaScript (inline в index.html)

#### Сжатие фото

```python
# Псевдокод: compress_image(file, max_size_mb=1)
def compress_image(file, max_size_mb=1):
    # Читаем файл как Image
    img = await read_as_image(file)
    
    # canvas для ресайза
    canvas = document.createElement('canvas')
    ctx = canvas.getContext('2d')
    
    # Уменьшаем until < max_size_mb
    quality = 0.9
    while get_blob_size(img, quality) > max_size_mb * 1024 * 1024:
        scale *= 0.8
        draw_resized(img, canvas, scale)
        quality -= 0.1
    
    return canvas.to_blob('image/jpeg', quality)
```

#### PBKDF2 Key Derivation

```python
# Псевдокод: derive_key(password, salt)
def derive_key(password, salt=None):
    if not salt:
        salt = crypto.get_random_values(16 bytes)
    
    key = await crypto.subtle.import_key('raw', password)
    derived = await crypto.subtle.derive_key(
        algorithm='PBKDF2',
        base_key=key,
        salt=salt,
        iterations=100000,
        hash='SHA-256',
        length=256
    )
    return derived, salt
```

#### AES-256-GCM Encryption

```python
# Псевдокод: encrypt(plaintext, key)
def encrypt(plaintext, key):
    # IV = 12 bytes random
    iv = crypto.get_random_values(12 bytes)
    
    # Шифруем
    ciphertext = await crypto.subtle.encrypt(
        algorithm='AES-GCM',
        key=key,
        iv=iv,
        data=plaintext
    )
    
    # Формат вывода: base64(salt + iv + ciphertext)
    return base64_encode(salt + iv + ciphertext)
```

#### Главная функция

```python
# Псевдокод: encrypt_content(text, files, secret)
async def encrypt_content(text, files, secret):
    # 1. Сжимаем фото
    images = []
    for f in files:
        img = await compress_image(f, max_size_mb=1)
        images.append(base64_encode(img))
    
    # 2. Формируем payload
    payload = json.dumps({
        'text': text,
        'images': images,
        'timestamp': now_iso()
    })
    
    # 3. Шифруем
    result = await encrypt(payload, secret)
    
    # 4. Выводим пользователю
    return result
```

---

## 2. Cloud Function (IMAP-poller)

### 2.1 Структура проекта

```
cloud-function/
├── main.py              # точка входа
├── imap_client.py       # IMAP логика
├── decryptor.py         # дешифровка
├── storage.py           # Object Storage
├── queue.py             # Message Queue
├── config.py            # конфиг (из env)
├── requirements.txt     # зависимости
└── main.tf             # деплой
```

### 2.2 config.py

```python
import os

SECRET = os.environ['SHARED_SECRET']
IMAP_HOST = os.environ['IMAP_HOST']
IMAP_USER = os.environ['IMAP_USER']
IMAP_PASSWORD = os.environ['IMAP_PASSWORD']
S3_BUCKET = os.environ['S3_BUCKET']
MQ_QUEUE = os.environ['MQ_QUEUE']
ASI_ONE_URL = os.environ['ASI_ONE_URL']
ASI_ONE_KEY = os.environ['ASI_ONE_KEY']
```

### 2.3 imap_client.py

```python
import imaplib
import email
from config import IMAP_HOST, IMAP_USER, IMAP_PASSWORD

def connect():
    m = imaplib.IMAP4_SSL(IMAP_HOST)
    m.login(IMAP_USER, IMAP_PASSWORD)
    return m

def get_unread_emails():
    m = connect()
    m.select('INBOX')
    
    # Ищем непрочитанные письма.
    # HASATTACHMENT — расширение Yandex/Gmail.
    # Добавляем фильтр по теме для исключения спама.
    typ, data = m.search(None, 'UNSEEN', 'SUBJECT', '"ASI-POST"', 'HASATTACHMENT')
    
    emails = []
    for num in data[0].split():
        typ, msg_data = m.fetch(num, '(RFC822)')
        if typ != 'OK':
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        email_data = parse_email(msg)
        email_data['id'] = num.decode()
        emails.append(email_data)

        # Помечаем как прочитанное СРАЗУ, чтобы не обрабатывать повторно при сбое
        m.store(num, '+FLAGS', '\\Seen')
    
    m.close()
    m.logout()
    return emails
```

### 2.4 decryptor.py

```python
import base64
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def decrypt(encrypted_data: str, secret: str) -> dict:
    # Декодируем base64
    data = base64.b64decode(encrypted_data)
    
    # Извлекаем: salt(16) + iv(12) + ciphertext
    salt = data[:16]
    iv = data[16:28]
    ciphertext = data[28:]
    
    # Derive key via PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    key = kdf.derive(secret.encode())
    
    # Decrypt
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    
    return json.loads(plaintext)
```

### 2.5 storage.py

```python
import boto3
from config import S3_BUCKET

s3 = boto3.client('s3')

def upload_image(image_data: bytes, filename: str) -> str:
    key = f"photos/{filename}"
    s3.upload_fileobj(
        BytesIO(image_data),
        S3_BUCKET,
        key,
        ExtraArgs={'ContentType': 'image/jpeg'}
    )

    # Генерируем Pre-signed URL для Instagram (действует 1 час)
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET, 'Key': key},
        ExpiresIn=3600
    )
    return url
```

### 2.6 queue.py

```python
import boto3
from config import MQ_QUEUE

sqs = boto3.client('sqs')

def publish_to_queue(payload: dict):
    sqs.send_message(
        QueueUrl=MQ_QUEUE,
        MessageBody=json.dumps(payload)
    )
```

### 2.7 main.py

```python
import json
from imap_client import get_unread_emails
from decryptor import decrypt
from storage import upload_image
from queue import publish_to_queue
from config import SECRET
import logging
import base64

def handler(event, context):
    # Триггер: Cloud Scheduler каждые 5 минут
    emails = get_unread_emails()
    
    for email_data in emails:
        # Пропускаем если нет вложений
        if not email_data.get('attachments'):
            continue
        
        try:
            # Дешифруем тело письма
            payload = decrypt(email_data['body'], SECRET)
            
            # Загружаем фото в S3
            image_urls = []
            for idx, img_data in enumerate(payload.get('images', [])):
                img_bytes = base64.b64decode(img_data)
                url = upload_image(img_bytes, f"{email_data['id']}_{idx}.jpg")
                image_urls.append(url)
            
            # Публикуем в очередь
            publish_to_queue({
                'text': payload['text'],
                'images': image_urls,
                'timestamp': payload.get('timestamp'),
                'from': email_data['from']
            })
            
        except Exception as e:
            logging.error(f"Failed to process email {email_data['id']}: {e}")
    
    return {'statusCode': 200}
```

### 2.8 requirements.txt

```
boto3>=1.34.0
cryptography>=41.0.0
pyyaml>=6.0
```

---

## 3. asi:one интеграция

### 3.1 Структура

```
asi-one-worker/
├── main.py              # polling + вызов API
├── config.py            # конфиг
├── requirements.txt
└── main.tf
```

### 3.2 main.py

```python
import json
import requests
from config import ASI_ONE_URL, ASI_ONE_KEY, INSTAGRAM_ACCOUNT
import logging

def call_asi_one(text: str, images: list) -> dict:
    prompt = f"""Опубликуй пост в Instagram аккаунт {INSTAGRAM_ACCOUNT}.

Текст поста: {text}
Фото: {images}

Используй инструмент instagram для публикации."""

    response = requests.post(
        ASI_ONE_URL,
        headers={
            'Authorization': f'Bearer {ASI_ONE_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'asi1',
            'messages': [{'role': 'user', 'content': prompt}]
        }
    )
    return response.json()

def handler(event, context):
    # Триггер: Yandex Message Queue
    for message in event['messages']:
        try:
            body = json.loads(message['details']['message']['body'])

            # Вызов asi:one
            resp = call_asi_one(body['text'], body['images'])
            
            # Проверяем успех
            if resp.get('choices'):
                logging.info(f"Posted successfully: {body['text'][:50]}...")
            else:
                logging.error(f"asi:one failed: {resp}")
                raise Exception("Publication failed")
                
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            # Пробрасываем исключение, чтобы триггер не удалял сообщение и сработал retry
            raise e
    
    return {'statusCode': 200}
```

### 3.3 requirements.txt

```
boto3>=1.34.0
requests>=2.31.0
```

---

## 4. Terraform конфигурация

### 4.1 main.tf (общий)

```hcl
terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  token   = var.token
  folder_id = var.folder_id
  cloud_id  = var.cloud_id
}

# Object Storage bucket
resource "yandex_storage_bucket" "photos" {
  bucket = "asi-one-photos"
  acl    = "private"
}

# Service Account for Functions
resource "yandex_iam_service_account" "sa" {
  name = "asi-one-sa"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_roles" {
  for_each = toset([
    "storage.editor",
    "lockbox.payloadViewer",
    "ymq.reader",
    "ymq.writer",
  ])
  folder_id = var.folder_id
  member    = "serviceAccount:${yandex_iam_service_account.sa.id}"
  role      = each.key
}

# Message Queue (YMQ)
resource "yandex_message_queue" "queue" {
  name = "asi-one-queue"
}

# Static Access Key for boto3 (S3 & YMQ)
resource "yandex_iam_service_account_static_access_key" "sa_key" {
  service_account_id = yandex_iam_service_account.sa.id
}
```

### 4.2 secrets.tf

```hcl
resource "yandex_lockbox_secret" "imap_credentials" {
  name = "asi-one-imap"
  
  payload = {
    "imap_host"     = "imap.yandex.ru"
    "imap_user"     = "asione@chronicles.website.yandexcloud.net"
    "imap_password" = "xxx"  # из переменной
    "shared_secret" = "moydереня2026"
  }
}

resource "yandex_lockbox_secret" "asi_one" {
  name = "asi-one-api"
  
  payload = {
    "url" = "https://api.asi1.ai/v1/chat/completions"
    "key" = "xxx"  # из переменной
  }
}
```

### 4.3 functions.tf

```hcl
# Cloud Function: IMAP-poller
resource "yandex_function" "imap_poller" {
  name               = "asi-one-imap-poller"
  runtime            = "python312"
  memory             = 256
  timeout            = 300
  service_account_id = yandex_iam_service_account.sa.id
  
  entrypoint  = "main.handler"
  content     = filebase64("./cloud-function.zip")
  
  environment = {
    IMAP_HOST       = "imap.yandex.ru"
    S3_BUCKET       = yandex_storage_bucket.photos.id
    MQ_QUEUE        = yandex_message_queue.queue.id
    AWS_ACCESS_KEY_ID     = yandex_iam_service_account_static_access_key.sa_key.access_key
    AWS_SECRET_ACCESS_KEY = yandex_iam_service_account_static_access_key.sa_key.secret_key
  }
  
  secret {
    id      = yandex_lockbox_secret.imap_credentials.id
    key     = "imap_password"
    version = 1
  }
}

# Trigger: каждые 5 минут
resource "yandex_function_trigger" "scheduler" {
  name        = "asi-one-scheduler"
  description = "Trigger every 5 minutes"
  
  schedule_cron = "*/5 * * * *"
  
  function {
    id = yandex_function.imap_poller.id
    service_account_id = yandex_iam_service_account.sa.id
  }
}

# Trigger: MQ -> asi:one worker
resource "yandex_function_trigger" "mq_trigger" {
  name        = "asi-one-mq-trigger"

  message_queue {
    queue_id           = yandex_message_queue.queue.arn
    service_account_id = yandex_iam_service_account.sa.id
    batch_size         = 1
    batch_cutoff       = 10
  }

  function {
    id = yandex_function.asi_one_worker.id
    service_account_id = yandex_iam_service_account.sa.id
  }
}

# Cloud Function: asi:one worker
resource "yandex_function" "asi_one_worker" {
  name               = "asi-one-worker"
  runtime            = "python312"
  memory             = 512
  timeout            = 300
  service_account_id = yandex_iam_service_account.sa.id
  
  entrypoint  = "main.handler"
  content     = filebase64("./asi-one-worker.zip")
  
  environment = {
    MQ_QUEUE    = yandex_message_queue.queue.id
    INSTAGRAM_ACCOUNT = "@zaebuntu"
  }
  
  secret {
    id      = yandex_lockbox_secret.asi_one.id
    key     = "key"
    version = 1
  }
}
```

---

## 5. Тестирование

### 5.1 Подход

| Уровень | Инструменты | Что тестируем |
|---------|-------------|---------------|
| Unit | pytest | encrypt/decrypt, PBKDF2, |
| Integration | pytest + moto | IMAP mock, S3 mock, SQS mock |
| E2E | ручной | полный цикл |

### 5.2 Unit-тесты (пример)

```python
# test_encryptor.py
import pytest
from encryptor import encrypt, decrypt
import json

def test_encrypt_decrypt_roundtrip():
    secret = "test-secret"
    payload = {"text": "hello", "images": []}
    
    encrypted = encrypt(json.dumps(payload), secret)
    decrypted = decrypt(encrypted, secret)
    
    assert json.loads(decrypted) == payload

def test_different_iv_per_encryption():
    secret = "test-secret"
    payload = {"text": "hello"}
    
    enc1 = encrypt(payload, secret)
    enc2 = encrypt(payload, secret)
    
    # IV разный -> результат разный
    assert enc1 != enc2
    
    # Но оба дешифруются
    assert decrypt(enc1, secret) == decrypt(enc2, secret)
```

### 5.3 Integration-тесты (пример)

```python
# test_imap_client.py
import pytest
from unittest.mock import MagicMock
from imap_client import parse_email

def test_parse_email_with_attachment():
    mock_msg = MagicMock()
    mock_msg.get_payload.return_value = "encrypted_data"
    mock_msg.get.return_value = "sender@yandex.ru"
    mock_msg.walk.return_value = []
    
    result = parse_email(mock_msg)
    
    assert result['from'] == "sender@yandex.ru"
    assert result['body'] == "encrypted_data"
```

---

## 6. Стильгайд (AGENTS.md)

### Конвенции кода

1. **Именование:** snake_case для функций/переменных, PascalCase для классов
2. **Типизация:** использовать type hints
3. **Документация:** docstrings для всех функций
4. **Ошибки:** логировать через logging, не print

### Workflow

```bash
# Тесты
pytest -v

# Деплой cloud function
cd cloud-function && zip -r function.zip . && \
  yc function upload python312 \
    --name=asi-one-imap-poller \
    --description="IMAP poller for InstagramPoster"
```

### Структура проекта

```
asi-one-instagram/
├── web-encryptor/       # клиент (HTML + JS)
├── cloud-function/      # Cloud Function (Python)
├── asi-one-worker/      # asi:one worker (Python)
├── terraform/          # IaC
├── tests/              # тесты
└── AGENTS.md          # этот файл
```

---

## 7. Риски и митигации

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| IMAP пароль истекает | Средняя | Логировать в Secrets, легко ротировать |
| asi:one API недоступен | Низкая | Retry 3 раза, логировать |
| Фото > 1MB после сжатия | Средняя | Рекурсивное уменьшение quality |
| Cloud Function таймаут | Средняя | Увеличить timeout до 300s |
| Очередь переполняется | Низкая | Dead letter queue + мониторинг |

---

## 8. Следующие шаги

1. ✅ Спека написана
2. ⏳ Ревью от коллеги
3. ⏳ Утверждение спеки
4. ⏳ Реализация: Web-encryptor
5. ⏳ Реализация: Cloud Function (IMAP-poller)
6. ⏳ Реализация: Terraform
7. ⏳ Реализация: asi:one worker
8. ⏳ Тестирование
9. ⏳ Деплой

---

## Зависимости

- Yandex Cloud (Functions, Storage, MQ, Secrets, Trigger)
- Python 3.12
- Terraform >= 1.5
- pytest