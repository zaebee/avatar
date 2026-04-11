resource "yandex_function" "imap_poller" {
  name        = "asi-one-imap-poller"
  description = "IMAP poller for asi:one InstagramPoster"
  runtime     = "python312"
  memory      = 256
  user_hash   = "v1"
  
  entrypoint  = "main.handler"
  
  content {
    zip_filename = "imap-worker.zip"
  }
  
  service_account_id = yandex_iam_service_account.functions_sa.id
  
  environment = {
    IMAP_HOST      = "imap.yandex.ru"
    IMAP_USER     = var.imap_user
    IMAP_PASSWORD = var.imap_password
    SHARED_SECRET = var.shared_secret
    S3_BUCKET    = yandex_storage_bucket.photos.bucket
    S3_ENDPOINT   = "https://storage.yandexcloud.net"
    MQ_QUEUE     = yandex_message_queue.instagram_posts.name
  }
  
  depends_on = [
    yandex_message_queue.instagram_posts,
    yandex_storage_bucket.photos
  ]
}

resource "yandex_function_trigger" "scheduler" {
  name        = "asi-one-scheduler"
  description = "Trigger every 5 minutes for IMAP poller"
  
  timer {
    cron_expression = "*/5 * * * ? *"
  }
  
  function {
    id = yandex_function.imap_poller.id
  }
}

resource "yandex_function" "asi_one_worker" {
  name        = "asi-one-worker"
  description = "asi:one worker for Instagram posting"
  runtime     = "python312"
  memory      = 512
  user_hash   = "v1"
  
  entrypoint  = "main.handler"
  
  content {
    zip_filename = "worker.zip"
  }
  
  service_account_id = yandex_iam_service_account.functions_sa.id
  
  environment = {
    MQ_QUEUE            = yandex_message_queue.instagram_posts.name
    INSTAGRAM_ACCOUNT  = "@zaebuntu"
    ASI_ONE_URL       = var.asi_one_url
    ASI_ONE_KEY      = var.asi_one_key
  }
  
  depends_on = [
    yandex_message_queue.instagram_posts
  ]
}

resource "yandex_function_trigger" "mq_trigger" {
  name        = "asi-one-mq-trigger"
  description = "Trigger on new queue messages"
  
  message_queue {
    queue_id             = yandex_message_queue.instagram_posts.id
    service_account_id  = yandex_iam_service_account.functions_sa.id
    batch_cutoff         = 0
  }
  
  function {
    id = yandex_function.asi_one_worker.id
  }
}