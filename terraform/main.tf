terraform {
  required_version = ">= 1.5"
  
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  service_account_key_file = "/app/authorized_key.json"
  folder_id = "b1gesh0suso3pvjrro56"
}

resource "yandex_function_iam_binding" "imap_poller_invoker" {
  function_id = "d4erk3ahrierh0l63643"
  role        = "functions.invoker"
  members     = ["serviceAccount:ajeila5562o058l0q4eq"]
}

resource "yandex_function_iam_binding" "asi_one_worker_invoker" {
  function_id = "d4epo4b8v2dmbpt4jp96"
  role        = "functions.invoker"
  members     = ["serviceAccount:ajeila5562o058l0q4eq"]
}