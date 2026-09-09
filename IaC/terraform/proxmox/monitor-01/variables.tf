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
  description = "Standalone Proxmox node that hosts monitor-01."
  type        = string
  default     = "Proxmox-2"
}

variable "vm_id" {
  description = "Proxmox VM ID reserved for monitor-01."
  type        = number
  default     = 200
}

variable "hostname" {
  description = "Monitoring VM hostname."
  type        = string
  default     = "monitor-01"
}

variable "domain" {
  description = "Local search domain."
  type        = string
  default     = "jameshouse"
}

variable "ipv4_cidr" {
  description = "Static monitor-01 IPv4 address."
  type        = string
  default     = "192.168.2.52/24"
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

variable "ssh_public_key" {
  description = "SSH public key installed for the james automation/admin account."
  type        = string
  sensitive   = true
}

variable "bridge" {
  description = "Proxmox bridge used by monitor-01."
  type        = string
  default     = "vmbr0"
}

variable "image_datastore_id" {
  description = "Datastore used to hold the imported Debian cloud image and cloud-init snippet."
  type        = string
  default     = "local"
}

variable "vm_datastore_id" {
  description = "Datastore used for the monitor-01 VM disk and cloud-init disk."
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
  default     = 6144
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

variable "debian_cloud_image_url" {
  description = "Pinned Debian 13 genericcloud QCOW2 image."
  type        = string
  default     = "https://cloud.debian.org/cdimage/cloud/trixie/20260712-2537/debian-13-genericcloud-amd64-20260712-2537.qcow2"
}

variable "debian_cloud_image_sha512" {
  description = "SHA-512 checksum for the pinned Debian 13 genericcloud QCOW2 image."
  type        = string
  default     = "7ae53e9dbee282bfc16f289dec483dde3a8598769c38a267948310f7a2a52c662620198603bc52c142627efba379863d16079698a10b34102d55bcedd40e8d32"
}
