# Cloud Function: IMAP-poller

resource "yandex_function" "imap_poller" {
  name        = "asi-one-imap-poller"
  description = "IMAP poller for asi:one InstagramPoster"
  runtime     = "python312"
  memory      = 256
  timeout     = 300
  execution_timeout = 300
  
  entrypoint  = "main.handler"
  content     = filebase64("./cloud-function.zip")
  
  service_account_id = yandex_iam_service_account.functions_sa.id
  
  environment = {
    IMAP_HOST    = "imap.yandex.ru"
    S3_BUCKET    = yandex_storage_bucket.photos.bucket
    S3_ENDPOINT  = "https://storage.yandexcloud.net"
    MQ_QUEUE     = yandex_message_queue.instagram_posts.name
  }
  
  secrets = [
    {
      id      = yandex_lockbox_secret.imap_credentials.id
      key     = "imap_password"
      version = "latest"
    },
    {
      id      = yandex_lockbox_secret.imap_credentials.id
      key     = "shared_secret"
      version = "latest"
    }
  ]
  
  depends_on = [
    yandex_message_queue.instagram_posts,
    yandex_storage_bucket.photos
  ]
}

# Trigger: Cloud Scheduler каждые 5 минут
resource "yandex_function_trigger" "scheduler" {
  name        = "asi-one-scheduler"
  description = "Trigger every 5 minutes for IMAP poller"
  
  schedule_cron = "*/5 * * * *"
  
  function {
    id = yandex_function.imap_poller.id
  }
}

# Cloud Function: asi:one worker (MQ Trigger)
resource "yandex_function" "asi_one_worker" {
  name        = "asi-one-worker"
  description = "asi:one worker for Instagram posting"
  runtime     = "python312"
  memory      = 512
  timeout     = 300
  execution_timeout = 300
  
  entrypoint  = "main.handler"
  content     = filebase64("./asi-one-worker.zip")
  
  service_account_id = yandex_iam_service_account.functions_sa.id
  
  environment = {
    MQ_QUEUE           = yandex_message_queue.instagram_posts.name
    INSTAGRAM_ACCOUNT = "@zaebuntu"
  }
  
  secrets = [
    {
      id      = yandex_lockbox_secret.asi_one.id
      key     = "key"
      version = "latest"
    }
  ]
  
  depends_on = [
    yandex_message_queue.instagram_posts
  ]
}

# MQ Trigger для asi:one worker
resource "yandex_function_trigger" "mq_trigger" {
  name        = "asi-one-mq-trigger"
  description = "Trigger on new queue messages"
  
  message_queue {
    queue_id     = yandex_message_queue.instagram_posts.id
    service_account_id = yandex_iam_service_account.functions_sa.id
  }
  
  function {
    id = yandex_function.asi_one_worker.id
  }
}