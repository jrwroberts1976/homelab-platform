variable "proxmox_endpoint" {
  description = "Proxmox VE API endpoint."
  type        = string
  default     = "https://192.168.2.70:8006/"
}

variable "proxmox_api_token" {
  description = "Proxmox API token in user@realm!token=secret form. Supply with TF_VAR_proxmox_api_token; never commit it."
  type        = string
  sensitive   = true
}

variable "proxmox_insecure" {
  description = "Allow the current self-signed Proxmox API certificate."
  type        = bool
  default     = true
}

variable "proxmox_node_name" {
  description = "Target Proxmox node name."
  type        = string
  default     = "PROXMOX"
}

variable "vm_id" {
  description = "LXC container ID. Confirm it is unused before apply."
  type        = number
}

variable "hostname" {
  description = "DNS service hostname."
  type        = string
  default     = "dns-02"
}

variable "ipv4_cidr" {
  description = "Static IPv4 address in CIDR notation. The address must be verified free and reserved before apply."
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
  description = "DNS servers used by the container before Pi-hole/Unbound takes over."
  type        = list(string)
  default     = ["192.168.2.48"]
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
  description = "Proxmox bridge used by dns-02."
  type        = string
  default     = "vmbr0"
}

variable "enable_pve_firewall" {
  description = "Enable the Proxmox firewall flag on the LXC network interface."
  type        = bool
  default     = false
}

variable "rootfs_datastore_id" {
  description = "Datastore for the LXC root filesystem."
  type        = string
  default     = "vm-ssd"
}

variable "template_file_id" {
  description = "Existing Proxmox LXC template volume ID."
  type        = string
  default     = "local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst"
}

variable "cpu_cores" {
  description = "vCPU allocation."
  type        = number
  default     = 1
}

variable "memory_mb" {
  description = "Dedicated RAM in MiB."
  type        = number
  default     = 512
}

variable "swap_mb" {
  description = "Swap allocation in MiB."
  type        = number
  default     = 256
}

variable "disk_size_gb" {
  description = "Root disk size in GiB."
  type        = number
  default     = 8
}

variable "protect_after_build" {
  description = "Set Proxmox protection flag. Leave false during initial build/rollback testing; change to true after validation."
  type        = bool
  default     = false
}
