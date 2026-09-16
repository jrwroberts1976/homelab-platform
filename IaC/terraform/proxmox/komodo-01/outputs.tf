output "komodo_vm_id" {
  value = proxmox_virtual_environment_vm.komodo.vm_id
}

output "komodo_name" {
  value = proxmox_virtual_environment_vm.komodo.name
}

output "komodo_ipv4" {
  value = split("/", var.ipv4_cidr)[0]
}

output "komodo_node" {
  value = var.proxmox_node_name
}

output "komodo_clone_source_vm_id" {
  value = var.clone_source_vm_id
}
