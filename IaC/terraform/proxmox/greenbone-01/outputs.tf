output "greenbone_vm_id" {
  value = proxmox_virtual_environment_vm.greenbone.vm_id
}

output "greenbone_name" {
  value = proxmox_virtual_environment_vm.greenbone.name
}

output "greenbone_ipv4" {
  value = split("/", var.ipv4_cidr)[0]
}

output "greenbone_node" {
  value = var.proxmox_node_name
}

output "debian_cloud_image_id" {
  value = proxmox_download_file.debian_cloud_image.id
}
