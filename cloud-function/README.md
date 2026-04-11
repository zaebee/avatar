# Cloud Function: IMAP Poller

## Структура

```
cloud-function/
├── main.py          # Handler
├── config.py        # Environment variables
├── imap_client.py   # IMAP connection
├── decryptor.py     # Decrypt payload
├── storage.py       # Upload to S3
├── queue.py         # Publish to MQ
└── requirements.txt
```

## Деплой

1. Создать zip архив:
   ```bash
   cd cloud-function
   zip -r function.zip *.py
   ```

2. Загрузить в Yandex Cloud Function:
   - Runtime: Python 3.12
   - Entry point: main.handler

## Environment Variables

| Variable | Description |
|----------|-------------|
| IMAP_HOST | IMAP сервер (default: imap.yandex.ru) |
| IMAP_USER | Email для подключения |
| IMAP_PASSWORD | Пароль |
| SHARED_SECRET | Ключ для дешифрования |
| S3_BUCKET | Имя bucket |
| S3_ENDPOINT | S3 endpoint |
| MQ_QUEUE | Имя очереди |

## Payload Format

```json
{
  "text": "Post caption",
  "images": ["base64 encoded images"],
  "timestamp": "2024-01-01T00:00:00Z",
  "from": "user@example.com"
}
```