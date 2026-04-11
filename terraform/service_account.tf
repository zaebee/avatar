resource "yandex_iam_service_account" "functions_sa" {
  name        = "asi-one-functions"
  description = "Service account for asi:one InstagramPoster functions"
}

resource "yandex_resourcemanager_folder_iam_member" "functions_sa_editor" {
  folder_id = var.folder_id
  role     = "editor"
  member   = "serviceAccount:${yandex_iam_service_account.functions_sa.id}"
}