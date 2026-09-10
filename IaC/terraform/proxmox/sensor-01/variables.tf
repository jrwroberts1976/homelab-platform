variable "proxmox_endpoint" {
  description = "Proxmox VE API endpoint."
  type        = string
  default     = "https://192.168.2.70:8006/"
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
  description = "Standalone Proxmox node that hosts sensor-01."
  type        = string
  default     = "PROXMOX"
}

variable "vm_id" {
  description = "Proxmox VM ID proposed for sensor-01; deployment preflight must prove it is unused."
  type        = number
  default     = 201
}

variable "hostname" {
  description = "Sensor VM hostname."
  type        = string
  default     = "sensor-01"
}

variable "domain" {
  description = "Local search domain."
  type        = string
  default     = "jameshouse"
}

variable "ipv4_cidr" {
  description = "Proposed static sensor-01 management IPv4; deployment preflight must prove it is unused."
  type        = string
  default     = "192.168.2.55/24"
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
  description = "Proxmox bridge used only by the sensor management NIC."
  type        = string
  default     = "vmbr0"
}

variable "image_datastore_id" {
  description = "Datastore used to hold the imported Debian cloud image and cloud-init snippet."
  type        = string
  default     = "local"
}

variable "vm_datastore_id" {
  description = "Datastore used for sensor-01 system/log disk and cloud-init disk."
  type        = string
  default     = "vm-ssd"
}

variable "cpu_cores" {
  description = "Initial vCPU allocation."
  type        = number
  default     = 4
}

variable "memory_mb" {
  description = "Phase-1 RAM in MiB. Reassess capacity before enabling Suricata and Zeek together."
  type        = number
  default     = 3072
}

variable "disk_size_gb" {
  description = "Initial system/log disk size in GiB. Full packet capture is not retained."
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
