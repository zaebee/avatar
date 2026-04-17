resource "yandex_message_queue" "instagram_posts" {
  name       = "asi-one-instagram-posts"
  folder_id  = var.folder_id
  deduplication_window = 300
  retention_window = 604800
  visibility_timeout = 120
  wait_time_seconds = 0
}

output "queue_url" {
  value = yandex_message_queue.instagram_posts.url
}