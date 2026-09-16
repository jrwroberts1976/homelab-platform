output "container_id" {
  description = "Proxmox LXC ID."
  value       = proxmox_virtual_environment_container.komodo.vm_id
}

output "container_name" {
  description = "Container hostname."
  value       = var.hostname
}

output "target_node" {
  description = "Proxmox node hosting komodo-01."
  value       = var.proxmox_node_name
}

output "ipv4_cidr" {
  description = "Configured komodo-01 IPv4 address."
  value       = var.ipv4_cidr
}

output "mac_address" {
  description = "Stable komodo-01 management MAC address."
  value       = var.mac_address
}

output "ansible_target" {
  description = "IPv4 address used by the subsequent Ansible configuration phase."
  value       = split("/", var.ipv4_cidr)[0]
}
