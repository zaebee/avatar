resource "yandex_iam_service_account" "functions_sa" {
  name        = "asi-one-functions"
  description = "Service account for asi:one InstagramPoster functions"
}

resource "yandex_iam_service_account_static_access_key" "functions_sa_key" {
  service_account_id = yandex_iam_service_account.functions_sa.id
  
  description = "Static access key for asi:one functions"
}

resource "yandex_resourcemanager_folder_iam_member" "functions_sa_editor" {
  folder_id = var.folder_id
  role     = "editor"
  member   = "serviceAccount:${yandex_iam_service_account.functions_sa.id}"
}

resource "yandex_storage_bucket_acl" "photos_acl" {
  bucket = yandex_storage_bucket.photos.bucket
  
  grant {
    type   = "typeCanonicalUser"
    permission = "FULL_CONTROL"
    entity = "serviceAccount:${yandex_iam_service_account.functions_sa.id}"
  }
}