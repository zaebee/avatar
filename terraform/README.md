# Terraform Infrastructure

## Файлы

- `main.tf` — Provider конфигурация
- `variables.tf` — Переменные для CI/CD
- `functions.tf` — Data sources для существующих ресурсов
- `outputs.tf` — Выводы

## Ресурсы

- Service Account: `asi-one-functions` (`ajeila5562o058l0q4eq`)
- Bucket: `asi-one-photos`
- Queue: `asi-one-instagram-posts`
- Function: `asi-one-imap-poller` (d4erk3ahrierh0l63643)
- Function: `asi-one-worker` (d4epo4b8v2dmbpt4jp96)
- Trigger: `asi-one-scheduler` (a1s7jhtreucu46ks7k34)
- Trigger: `asi-one-mq-trigger` (a1smplboodr376ouafle)

## known issues

- Provider версия v0.197 требует ручного добавления ролей в консоли
- Function iam bindings не работают — добавлять вручную