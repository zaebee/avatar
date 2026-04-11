terraform {
  required_version = ">= 1.5"
  
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
      version = "~> 1.0"
    }
  }
}

provider "yandex" {
  token   = var.token
  folder_id = var.folder_id
  cloud_id  = var.cloud_id
}

# Object Storage bucket for photos
resource "yandex_storage_bucket" "photos" {
  bucket = "asi-one-photos"
  acl    = "public-read"
  
  versioning {
    enabled = false
  }
}

# Yandex Message Queue
resource "yandex_message_queue" "instagram_posts" {
  name       = "asi-one-instagram-posts"
  region     = "ru-central1"
  
  settings {
    visibility_timeout   = 300
    receive_wait_time     = 0
    retry_delays          = [10, 20, 40]
  }
  
  redrive_policy {
    max_delivery_attempts = 3
  }
}

# Dead Letter Queue
resource "yandex_message_queue" "instagram_posts_dlq" {
  name       = "asi-one-instagram-posts-dlq"
  region     = "ru-central1"
}