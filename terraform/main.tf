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

data "yandex_iam_service_account" "functions_sa" {
  name = "asi-one-functions"
}

data "yandex_storage_bucket" "photos" {
  bucket = "asi-one-photos"
}

data "yandex_message_queue" "instagram_posts" {
  name = "asi-one-instagram-posts"
}

resource "yandex_iam_service_account_static_access_key" "functions_sa_key" {
  service_account_id = data.yandex_iam_service_account.functions_sa.id
  description        = "Static access key for asi:one functions"
}
