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

resource "yandex_iam_service_account" "functions_sa" {
  name        = "asi-one-functions"
  description = "Service account for asi:one InstagramPoster functions"
  folder_id   = "b1gesh0suso3pvjrro56"
}

resource "yandex_iam_service_account_static_access_key" "functions_sa_key" {
  service_account_id = yandex_iam_service_account.functions_sa.id
  description        = "Static access key for asi:one functions"
}

resource "yandex_resourcemanager_folder_iam_member" "functions_sa_editor" {
  folder_id = "b1gesh0suso3pvjrro56"
  role     = "editor"
  member   = "serviceAccount:${yandex_iam_service_account.functions_sa.id}"
}

resource "yandex_storage_bucket" "photos" {
  bucket     = "asi-one-photos"
  access_key = yandex_iam_service_account_static_access_key.functions_sa_key.access_key
  secret_key = yandex_iam_service_account_static_access_key.functions_sa_key.secret_key
  
  versioning {
    enabled = false
  }
}

resource "yandex_message_queue" "instagram_posts" {
  name       = "asi-one-instagram-posts"
  region_id = "ru-central1"
  
  access_key = yandex_iam_service_account_static_access_key.functions_sa_key.access_key
  secret_key = yandex_iam_service_account_static_access_key.functions_sa_key.secret_key
  
  visibility_timeout_seconds = 300
  receive_wait_time_seconds = 0
  message_retention_seconds = 345600
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = yandex_message_queue.instagram_posts_dlq.arn
    maxReceiveCount = 3
  })
}

resource "yandex_message_queue" "instagram_posts_dlq" {
  name       = "asi-one-instagram-posts-dlq"
  region_id = "ru-central1"
  
  access_key = yandex_iam_service_account_static_access_key.functions_sa_key.access_key
  secret_key = yandex_iam_service_account_static_access_key.functions_sa_key.secret_key
}
