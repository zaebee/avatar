resource "yandex_lockbox_secret" "imap_credentials" {
  name        = "asi-one-imap"
  description = "IMAP credentials for asi:one InstagramPoster"
  
  lifecycle {
    prevent_destroy = true
  }
}

resource "yandex_lockbox_secret_version" "imap_credentials" {
  secret_id = yandex_lockbox_secret.imap_credentials.id
  
  entries {
    key   = "imap_host"
    value = "imap.yandex.ru"
  }
  entries {
    key   = "imap_user"
    value = var.imap_user
  }
  entries {
    key   = "imap_password"
    value = var.imap_password
  }
  entries {
    key   = "shared_secret"
    value = var.shared_secret
  }
}

resource "yandex_lockbox_secret" "asi_one" {
  name        = "asi-one-api"
  description = "asi:one API credentials"
  
  lifecycle {
    prevent_destroy = true
  }
}

resource "yandex_lockbox_secret_version" "asi_one" {
  secret_id = yandex_lockbox_secret.asi_one.id
  
  entries {
    key   = "url"
    value = "https://api.asi1.ai/v1/chat/completions"
  }
  entries {
    key   = "key"
    value = var.asi_one_key
  }
}