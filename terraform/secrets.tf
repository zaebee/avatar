# Lockbox secrets for credentials

resource "yandex_lockbox_secret" "imap_credentials" {
  name = "asi-one-imap"
  description = "IMAP credentials for asi:one InstagramPoster"
  
  lifecycle {
    prevent_destroy = true
  }
}

resource "yandex_lockbox_secret_version" "imap_credentials" {
  secret_id = yandex_lockbox_secret.imap_credentials.id
  
  payload = {
    "imap_host"     = "imap.yandex.ru"
    "imap_user"     = var.imap_user
    "imap_password" = var.imap_password
    "shared_secret" = var.shared_secret
  }
}

resource "yandex_lockbox_secret" "asi_one" {
  name = "asi-one-api"
  description = "asi:one API credentials"
  
  lifecycle {
    prevent_destroy = true
  }
}

resource "yandex_lockbox_secret_version" "asi_one" {
  secret_id = yandex_lockbox_secret.asi_one.id
  
  payload = {
    "url" = "https://api.asi1.ai/v1/chat/completions"
    "key" = var.asi_one_key
  }
}