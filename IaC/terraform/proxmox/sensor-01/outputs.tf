output "sensor_vm_id" {
  value = proxmox_virtual_environment_vm.sensor.vm_id
}

output "sensor_name" {
  value = proxmox_virtual_environment_vm.sensor.name
}

output "sensor_ipv4" {
  value = split("/", var.ipv4_cidr)[0]
}

output "sensor_node" {
  value = var.proxmox_node_name
}

output "debian_cloud_image_id" {
  value = proxmox_download_file.debian_cloud_image.id
}
