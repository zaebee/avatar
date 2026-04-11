variable "imap_host" {
  description = "IMAP host"
  type        = string
  default     = "imap.yandex.ru"
  sensitive   = false
}

variable "imap_user" {
  description = "IMAP user email"
  type        = string
  default     = "asione@chronicles.website.yandexcloud.net"
}

variable "imap_password" {
  description = "IMAP password"
  type        = string
  sensitive   = true
}

variable "shared_secret" {
  description = "Shared secret for encryption"
  type        = string
  sensitive   = true
}

variable "asi_one_url" {
  description = "asi:one API URL"
  type        = string
  default     = "https://api.asi1.ai/v1/chat/completions"
}

variable "asi_one_key" {
  description = "asi:one API key"
  type        = string
  sensitive   = true
}