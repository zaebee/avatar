data "yandex_function" "imap_poller" {
  name = "asi-one-imap-poller"
}

data "yandex_function" "asi_one_worker" {
  name = "asi-one-worker"
}

resource "yandex_function" "imap_poller_update" {
  name        = "asi-one-imap-poller"
  description = "IMAP poller for asi:one InstagramPoster"
  runtime     = "python312"
  memory      = 256
  user_hash   = "v2"
  
  entrypoint  = "main.handler"
  
  content {
    zip_filename = "imap-worker.zip"
  }
  
  service_account_id = "ajeila5562o058l0q4eq"
  
  environment = {
    IMAP_HOST      = "imap.yandex.ru"
    IMAP_USER     = "asione@anokto.idp.yandexcloud.net"
    IMAP_PASSWORD = "ljfp-cfkv-hhfj-cjim"
    S3_BUCKET    = "asi-one-photos"
    S3_ENDPOINT   = "https://storage.yandexcloud.net"
    MQ_QUEUE     = "asi-one-instagram-posts"
  }
}

resource "yandex_function_trigger" "scheduler" {
  name        = "asi-one-scheduler"
  description = "Trigger every 5 minutes for IMAP poller"
  
  timer {
    cron_expression = "*/5 * * * ? *"
  }
  
  function {
    id                = "d4erk3ahrierh0l63643"
    service_account_id = "ajeila5562o058l0q4eq"
  }
}

resource "yandex_function_trigger" "mq_trigger" {
  name        = "asi-one-mq-trigger"
  description = "Trigger on new queue messages"
  
  message_queue {
    queue_id             = "yrn:yc:ymq:ru-central1:b1gesh0suso3pvjrro56:asi-one-instagram-posts"
    service_account_id  = "ajeila5562o058l0q4eq"
    batch_cutoff         = 0
  }
  
  function {
    id                = "d4epo4b8v2dmbpt4jp96"
    service_account_id = "ajeila5562o058l0q4eq"
  }
}