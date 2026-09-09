output "cloud_vm_id" {
  value = proxmox_virtual_environment_vm.cloud.vm_id
}

output "cloud_name" {
  value = proxmox_virtual_environment_vm.cloud.name
}

output "cloud_ipv4" {
  value = split("/", var.ipv4_cidr)[0]
}

output "cloud_node" {
  value = var.proxmox_node_name
}

output "source_template_vm_id" {
  value = var.template_vm_id
}
