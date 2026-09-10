variable "proxmox_endpoint" {
  description = "Target Proxmox VE API endpoint."
  type        = string
}

variable "proxmox_api_token" {
  description = "Proxmox API token in user@realm!token=secret form."
  type        = string
  sensitive   = true
}

variable "proxmox_insecure" {
  description = "Allow the current self-signed Proxmox API certificate."
  type        = bool
  default     = true
}

variable "proxmox_node_name" {
  description = "Target standalone Proxmox node."
  type        = string
}

variable "vm_id" {
  description = "LXC container ID."
  type        = number
}

variable "hostname" {
  description = "Mail relay hostname."
  type        = string
  default     = "mail-relay-01"
}

variable "ipv4_cidr" {
  description = "Static IPv4 address in CIDR notation."
  type        = string
}

variable "ipv4_gateway" {
  description = "LAN default gateway."
  type        = string
  default     = "192.168.2.1"
}

variable "search_domain" {
  description = "Local DNS search domain."
  type        = string
  default     = "jameshouse"
}

variable "bootstrap_dns_servers" {
  description = "DNS servers used by the relay host."
  type        = list(string)
  default     = ["192.168.2.51", "192.168.2.50"]
}

variable "ssh_public_keys" {
  description = "SSH public keys installed for root."
  type        = list(string)

  validation {
    condition     = length(var.ssh_public_keys) > 0
    error_message = "At least one SSH public key is required."
  }
}

variable "bridge" {
  description = "Proxmox bridge."
  type        = string
  default     = "vmbr0"
}

variable "rootfs_datastore_id" {
  description = "Datastore for the LXC root filesystem."
  type        = string
  default     = "vm-ssd"
}

variable "template_file_id" {
  description = "Existing Debian 13 Proxmox LXC template volume ID."
  type        = string
  default     = "local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst"
}

variable "cpu_cores" {
  type    = number
  default = 1
}

variable "memory_mb" {
  type    = number
  default = 512
}

variable "swap_mb" {
  type    = number
  default = 256
}

variable "disk_size_gb" {
  type    = number
  default = 8
}

variable "protect_after_build" {
  description = "Protect the container after successful configuration and validation."
  type        = bool
  default     = false
}
