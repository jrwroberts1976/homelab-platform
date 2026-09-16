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
  description = "Proxmox cluster node hosting komodo-01."
  type        = string
  default     = "PROXMOX"
}

variable "clone_source_vm_id" {
  description = "Validated Debian 13 QGA-enabled template used as the full-clone source."
  type        = number
  default     = 9001
}

variable "vm_id" {
  description = "Proxmox VM ID allocated to komodo-01."
  type        = number
  default     = 204
}

variable "hostname" {
  description = "Komodo management VM hostname."
  type        = string
  default     = "komodo-01"
}

variable "domain" {
  description = "Local search domain."
  type        = string
  default     = "jameshouse"
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

variable "dns_servers" {
  description = "IaC-managed DNS resolver pair."
  type        = list(string)
  default     = ["192.168.2.51", "192.168.2.50"]
}

variable "bridge" {
  description = "Proxmox management bridge."
  type        = string
  default     = "vmbr0"
}

variable "vm_datastore_id" {
  description = "Datastore used for the komodo-01 VM and cloud-init disk."
  type        = string
  default     = "vm-ssd"
}

variable "cpu_cores" {
  description = "Initial vCPU allocation."
  type        = number
  default     = 2
}

variable "memory_mb" {
  description = "Initial RAM allocation in MiB."
  type        = number
  default     = 2048
}

variable "disk_size_gb" {
  description = "Initial system disk size in GiB."
  type        = number
  default     = 32
}

variable "protect_after_build" {
  description = "Enable Proxmox protection only after deployment, monitoring and backup validation."
  type        = bool
  default     = false
}
