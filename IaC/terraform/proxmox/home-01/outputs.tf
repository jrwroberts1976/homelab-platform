output "vm_id" {
  value = proxmox_virtual_environment_vm.home.vm_id
}

output "hostname" {
  value = proxmox_virtual_environment_vm.home.name
}

output "proxmox_node" {
  value = proxmox_virtual_environment_vm.home.node_name
}

output "expected_ipv4" {
  value = var.expected_ipv4
}

output "home_assistant_url" {
  value = "http://${var.expected_ipv4}:8123"
}
