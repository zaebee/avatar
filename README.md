# asi:one InstagramPoster

Система для автоматической публикации постов в Instagram через зашифрованную email-рассылку для пользователей в rural areas с ограниченным интернетом.

## Архитектура

```
User (email + photo)
    ↓
Yandex Mail (IMAP)
    ↓
Cloud Function: imap-poller (every 5 min)
    ↓
Object Storage (upload photos)
    ↓
Message Queue
    ↓
Cloud Function: asi-one-worker
    ↓
asi:one AI Agent
    ↓
Instagram API
```

## Компоненты

| Компонент | Описание |
|-----------|----------|
| `terraform/` | IaC для Yandex Cloud |
| `cloud-function/` | Код IMAP poller функции |
| `asi-one-worker/` | Код worker функции |
| `web-encryptor/` | Web UI для шифрования писем |

## Требования

- Yandex Cloud аккаунт
- Service Account с правами editor + functions.invoker
- IMAP ящик для приёма писем
- asi:one API ключ

## Развёртывание

1. **CI/CD**: Sourcecraft автоматически деплоит через `.sourcecraft/ci.yaml`
2. **Secrets**: Настроить в Sourcecraft:
   - `IMAP_PASSWORD`
   - `SHARED_SECRET`
   - `ASI_ONE_KEY`

3. **Ручная настройка в консоли**:
   - Создать Service Account `asi-one-functions`
   - Дать роль `editor` на папку
   - Дать роль `functions.invoker` на функции

## Переменные

| Переменная | Описание | Default |
|------------|----------|---------|
| `imap_user` | IMAP email | `asione@anokto.idp.yandexcloud.net` |
| `asi_one_url` | asi:one API URL | `https://api.asi1.ai/v1/chat/completions` |
| `folder_id` | Yandex folder | `b1gesh0suso3pvjrro56` |

## Использование

1. Зашифровать данные через `web-encryptor/`
2. Отправить email с зашифрованным JSON на IMAP ящик
3. Система автоматически обработает и опубликует в Instagram