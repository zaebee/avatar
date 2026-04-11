# Service Account для Cloud Functions
resource "yandex_iam_service_account" "functions_sa" {
  name        = "asi-one-functions"
  description = "Service account for asi:one InstagramPoster functions"
}

# Статический ключ для Object Storage
resource "yandex_iam_service_account_static_access_key" "functions_sa_key" {
  service_account_id = yandex_iam_service_account.functions_sa.id
  
  description = "Static access key for asi:one functions"
}

# IAM роли для Service Account
resource "yandex_resourcemanager_folder_iam_member" "functions_sa_editor" {
  folder_id = var.folder_id
  role      = "editor"
  member    = "serviceAccount:${yandex_iam_service_account.functions_sa.id}"
}

# Роль для Object Storage
resource "yandex_storage_bucket_acl" "photos_acl" {
  bucket = yandex_storage_bucket.photos.bucket
  
  access {
    type  = "bucket"
    role  = "OWNER"
    entity = "serviceAccount:${yandex_iam_service_account.functions_sa.id}"
  }
  
  access {
    type  = "bucket"
    role  = "READER"
    entity = "serviceAccount:${yandex_iam_service_account.functions_sa.id}"
  }
}