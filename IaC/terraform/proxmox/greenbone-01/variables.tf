variable "proxmox_endpoint" {
  description = "Proxmox VE API endpoint."
  type        = string
  default     = "https://192.168.2.71:8006/"
}

variable "proxmox_api_token" {
  description = "Proxmox API token in user@realm!token=secret form. Supply through TF_VAR_proxmox_api_token."
  type        = string
  sensitive   = true
}

variable "proxmox_insecure" {
  description = "Allow the current self-signed Proxmox API certificate."
  type        = bool
  default     = true
}

variable "proxmox_node_name" {
  description = "Proxmox cluster node that hosts greenbone-01."
  type        = string
  default     = "Proxmox-2"
}

variable "vm_id" {
  description = "Proxmox VM ID reserved for greenbone-01."
  type        = number
  default     = 203
}

variable "hostname" {
  description = "Greenbone VM hostname."
  type        = string
  default     = "greenbone-01"
}

variable "domain" {
  description = "Local search domain."
  type        = string
  default     = "jameshouse"
}

variable "ipv4_cidr" {
  description = "Static greenbone-01 IPv4 address."
  type        = string
  default     = "192.168.2.57/24"
}

variable "ipv4_gateway" {
  description = "LAN default gateway."
  type        = string
  default     = "192.168.2.1"
}

variable "dns_servers" {
  description = "IaC-managed DNS resolver pair."
  type        = list(string)
  default     = ["192.168.2.51", "192.168.2.50"]
}

variable "bridge" {
  description = "Proxmox bridge used by greenbone-01."
  type        = string
  default     = "vmbr0"
}

variable "image_datastore_id" {
  description = "Datastore used to hold the imported Debian cloud image and cloud-init snippet."
  type        = string
  default     = "local"
}

variable "vm_datastore_id" {
  description = "Datastore used for the greenbone-01 VM disk and cloud-init disk."
  type        = string
  default     = "local-lvm"
}

variable "cpu_cores" {
  description = "vCPU allocation."
  type        = number
  default     = 4
}

variable "memory_mb" {
  description = "Dedicated RAM in MiB."
  type        = number
  default     = 8192
}

variable "disk_size_gb" {
  description = "System/data disk size in GiB."
  type        = number
  default     = 80
}

variable "protect_after_build" {
  description = "Enable Proxmox VM protection only after deployment and validation pass."
  type        = bool
  default     = false
}

variable "debian_cloud_image_id" {
  description = "Existing Debian 13 cloud image on Proxmox-2 local import storage."
  type        = string
  default     = "local:import/debian-13-genericcloud-amd64-20260712-2537.qcow2"
}
