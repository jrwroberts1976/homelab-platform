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
  description = "Target standalone/cluster Proxmox node name."
  type        = string
}

variable "vm_id" {
  description = "LXC container ID."
  type        = number

  validation {
    condition     = var.vm_id >= 100 && var.vm_id <= 999999999
    error_message = "vm_id must be a valid Proxmox guest ID."
  }
}

variable "hostname" {
  description = "Resolver hostname."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{0,62}$", var.hostname))
    error_message = "hostname must contain only lower-case letters, digits and hyphens."
  }
}

variable "ipv4_cidr" {
  description = "Static resolver IPv4 address in CIDR notation."
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
  description = "Existing DNS servers used before Pi-hole/Unbound is configured."
  type        = list(string)
  default     = ["192.168.2.48", "192.168.2.50"]
}

variable "ssh_public_keys" {
  description = "SSH public keys installed for the root account."
  type        = list(string)

  validation {
    condition     = length(var.ssh_public_keys) > 0
    error_message = "At least one SSH public key is required."
  }
}

variable "bridge" {
  description = "Proxmox bridge used by the resolver."
  type        = string
  default     = "vmbr0"
}

variable "rootfs_datastore_id" {
  description = "Datastore for the LXC root filesystem."
  type        = string
}

variable "template_file_id" {
  description = "Existing Debian 13 Proxmox LXC template volume ID."
  type        = string
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
  description = "Protect the container after the complete build and validation succeeds."
  type        = bool
  default     = false
}
