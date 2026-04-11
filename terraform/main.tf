terraform {
  required_version = ">= 1.5"
  
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  service_account_key_file = "/app/authorized_key.json"
  folder_id = "b1gesh0suso3pvjrro56"
}