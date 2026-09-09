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
  description = "Standalone Proxmox node that hosts cloud-01."
  type        = string
  default     = "PROXMOX"
}

variable "template_vm_id" {
  description = "Validated Debian 13 genericcloud QGA template VM ID."
  type        = number
  default     = 9001
}

variable "vm_id" {
  description = "Proxmox VM ID reserved for cloud-01."
  type        = number
  default     = 200
}

variable "hostname" {
  description = "Cloud VM hostname."
  type        = string
  default     = "cloud-01"
}

variable "domain" {
  description = "Local search domain."
  type        = string
  default     = "jameshouse"
}

variable "ipv4_cidr" {
  description = "Static cloud-01 IPv4 address."
  type        = string
  default     = "192.168.2.53/24"
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
  description = "Proxmox bridge used by cloud-01."
  type        = string
  default     = "vmbr0"
}

variable "vm_datastore_id" {
  description = "Datastore used for the cloud-01 system disk and cloud-init disk."
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
  description = "System disk size in GiB."
  type        = number
  default     = 32
}

variable "ssh_public_key" {
  description = "SSH public key for the james cloud-init account."
  type        = string
}

variable "protect_after_build" {
  description = "Enable Proxmox VM protection only after deployment and service validation pass."
  type        = bool
  default     = false
}
