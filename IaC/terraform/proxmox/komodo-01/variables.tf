variable "proxmox_endpoint" {
  description = "Proxmox VE API endpoint."
  type        = string
  default     = "https://192.168.2.70:8006/"
}

variable "proxmox_api_token" {
  description = "Proxmox API token. Supply through TF_VAR_proxmox_api_token."
  type        = string
  sensitive   = true
}

variable "proxmox_insecure" {
  description = "Allow the current self-signed Proxmox API certificate."
  type        = bool
  default     = true
}

variable "proxmox_node_name" {
  description = "Proxmox node hosting komodo-01."
  type        = string
  default     = "PROXMOX"
}

variable "ct_id" {
  description = "Proxmox LXC container ID reserved for komodo-01."
  type        = number
  default     = 104
}

variable "hostname" {
  description = "Komodo management container hostname."
  type        = string
  default     = "komodo-01"
}

variable "ipv4_cidr" {
  description = "Static management address for komodo-01."
  type        = string
  default     = "192.168.2.58/24"
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
  description = "DNS resolvers available during bootstrap."
  type        = list(string)
  default     = ["192.168.2.51", "192.168.2.50"]
}

variable "ssh_public_keys" {
  description = "SSH public keys installed for the root account so Ansible can configure the container."
  type        = list(string)

  validation {
    condition     = length(var.ssh_public_keys) > 0
    error_message = "At least one SSH public key is required."
  }
}

variable "bridge" {
  description = "Proxmox management bridge."
  type        = string
  default     = "vmbr0"
}

variable "mac_address" {
  description = "Stable locally administered MAC address for komodo-01."
  type        = string
  default     = "02:00:00:00:01:04"
}

variable "enable_pve_firewall" {
  description = "Enable the Proxmox firewall flag on the container network interface."
  type        = bool
  default     = false
}

variable "rootfs_datastore_id" {
  description = "Datastore for the LXC root filesystem."
  type        = string
  default     = "vm-ssd"
}

variable "template_file_id" {
  description = "Existing Debian 13 Proxmox LXC template."
  type        = string
  default     = "local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst"
}

variable "cpu_cores" {
  description = "CPU allocation."
  type        = number
  default     = 2
}

variable "memory_mb" {
  description = "Dedicated RAM in MiB."
  type        = number
  default     = 2048
}

variable "swap_mb" {
  description = "Swap allocation in MiB."
  type        = number
  default     = 512
}

variable "disk_size_gb" {
  description = "Root filesystem size in GiB."
  type        = number
  default     = 32
}

variable "protect_after_build" {
  description = "Enable Proxmox protection after deployment, monitoring and backup validation."
  type        = bool
  default     = false
}
