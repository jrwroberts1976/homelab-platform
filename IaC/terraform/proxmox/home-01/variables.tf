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
  description = "Proxmox cluster node that hosts home-01."
  type        = string
  default     = "PROXMOX"
}

variable "vm_id" {
  description = "Proxmox VM ID reserved for home-01."
  type        = number
  default     = 204
}

variable "hostname" {
  description = "Home Assistant VM hostname."
  type        = string
  default     = "home-01"
}

variable "expected_ipv4" {
  description = "Approved static IPv4 address to configure in Home Assistant OS after first boot."
  type        = string
  default     = "192.168.2.60"
}

variable "mac_address" {
  description = "Fixed MAC address for home-01."
  type        = string
  default     = "02:00:00:00:02:04"
}

variable "bridge" {
  description = "Proxmox bridge used by home-01."
  type        = string
  default     = "vmbr0"
}

variable "vm_datastore_id" {
  description = "Datastore used for the HAOS VM and EFI disk."
  type        = string
  default     = "vm-ssd"
}

variable "cpu_cores" {
  description = "vCPU allocation."
  type        = number
  default     = 2
}

variable "memory_mb" {
  description = "Dedicated RAM in MiB."
  type        = number
  default     = 4096
}

variable "disk_size_gb" {
  description = "HAOS system disk size in GiB."
  type        = number
  default     = 32
}

variable "haos_version" {
  description = "Pinned Home Assistant OS release."
  type        = string
  default     = "18.2"
}

variable "haos_image_id" {
  description = "Pre-staged uncompressed HAOS QCOW2 image on PROXMOX local import storage."
  type        = string
  default     = "local:import/haos_ova-18.2.qcow2"
}

variable "protect_after_build" {
  description = "Enable Proxmox VM protection after commissioning and backup validation; the deployment workflow explicitly overrides this to false during initial build."
  type        = bool
  default     = true
}
