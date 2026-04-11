terraform {
  required_version = ">= 1.5"
  
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  token    = var.token
  folder_id = "b1gesh0suso3pvjrro56"
  cloud_id  = "b1gbmfuuno217asel61v"
}

resource "yandex_storage_bucket" "photos" {
  bucket = "asi-one-photos"
  
  versioning {
    enabled = false
  }
}

resource "yandex_message_queue" "instagram_posts" {
  name = "asi-one-instagram-posts"
  region_id = "ru-central1"
  
  visibility_timeout_seconds = 300
  receive_wait_time_seconds = 0
  message_retention_seconds = 345600
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = yandex_message_queue.instagram_posts_dlq.arn
    maxReceiveCount = 3
  })
}

resource "yandex_message_queue" "instagram_posts_dlq" {
  name = "asi-one-instagram-posts-dlq"
  region_id = "ru-central1"
}