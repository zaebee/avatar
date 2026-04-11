terraform {
  required_version = ">= 1.5"
  
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  token = var.token
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