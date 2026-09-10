output "monitor_vm_id" {
  value = proxmox_virtual_environment_vm.monitor.vm_id
}

output "monitor_name" {
  value = proxmox_virtual_environment_vm.monitor.name
}

output "monitor_ipv4" {
  value = split("/", var.ipv4_cidr)[0]
}

output "monitor_node" {
  value = var.proxmox_node_name
}

output "debian_cloud_image_id" {
  value = proxmox_download_file.debian_cloud_image.id
}
