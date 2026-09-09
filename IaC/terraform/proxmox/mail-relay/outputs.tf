output "container_id" {
  value = proxmox_virtual_environment_container.mail_relay.vm_id
}

output "container_name" {
  value = var.hostname
}

output "target_node" {
  value = var.proxmox_node_name
}

output "ipv4_cidr" {
  value = var.ipv4_cidr
}

output "ansible_target" {
  value = split("/", var.ipv4_cidr)[0]
}
