output "bucket_name" {
  description = "Object Storage bucket name"
  value       = yandex_storage_bucket.photos.bucket
}

output "queue_name" {
  description = "Message Queue name"
  value       = yandex_message_queue.instagram_posts.name
}

output "imap_poller_function_id" {
  description = "IMAP poller function ID"
  value       = yandex_function.imap_poller.id
}

output "asi_one_worker_function_id" {
  description = "asi:one worker function ID"
  value       = yandex_function.asi_one_worker.id
}

output "service_account_id" {
  description = "Service account ID"
  value       = yandex_iam_service_account.functions_sa.id
}