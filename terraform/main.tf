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

resource "yandex_resourcemanager_folder_iam_member" "functions_sa_invoker" {
  folder_id = "b1gesh0suso3pvjrro56"
  role     = "functions.invoker"
  member   = "serviceAccount:ajeila5562o058l0q4eq"
}