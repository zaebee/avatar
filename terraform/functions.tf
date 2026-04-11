data "yandex_function" "imap_poller" {
  name = "asi-one-imap-poller"
}

data "yandex_function" "asi_one_worker" {
  name = "asi-one-worker"
}

data "yandex_function_trigger" "scheduler" {
  name = "asi-one-scheduler"
}

data "yandex_function_trigger" "mq_trigger" {
  name = "asi-one-mq-trigger"
}