data "yandex_function" "imap_poller" {
  name = "asi-one-imap-poller"
}

data "yandex_function" "asi_one_worker" {
  name = "asi-one-worker"
}

resource "yandex_function_trigger" "scheduler" {
  name        = "asi-one-scheduler"
  description = "Trigger every 5 minutes for IMAP poller"
  
  timer {
    cron_expression = "*/5 * * * ? *"
  }
  
  function {
    id                = data.yandex_function.imap_poller.id
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
    id                = data.yandex_function.asi_one_worker.id
    service_account_id = "ajeila5562o058l0q4eq"
  }
}