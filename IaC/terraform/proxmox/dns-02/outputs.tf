output "container_id" {
  description = "Proxmox LXC ID."
  value       = proxmox_virtual_environment_container.dns02.vm_id
}

output "container_name" {
  description = "Container hostname."
  value       = var.hostname
}

output "target_node" {
  description = "Proxmox node hosting dns-02."
  value       = var.proxmox_node_name
}

output "ipv4_cidr" {
  description = "Configured dns-02 IPv4 address."
  value       = var.ipv4_cidr
}

output "ansible_target" {
  description = "IPv4 address for the subsequent Ansible configuration phase."
  value       = split("/", var.ipv4_cidr)[0]
}
