variable "token" {
  description = "Yandex Cloud OAuth token"
  type        = string
  sensitive   = true
  default     = ""
}

variable "folder_id" {
  description = "Yandex Cloud folder ID"
  type        = string
  default     = "b1gesh0suso3pvjrro56"
}

variable "cloud_id" {
  description = "Yandex Cloud cloud ID"
  type        = string
  default     = "b1gbmfuuno217asel61v"
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