resource "proxmox_virtual_environment_vm" "home" {
  name        = var.hostname
  description = "Home Assistant OS ${var.haos_version} managed by homelab-platform/IaC"
  node_name   = var.proxmox_node_name
  vm_id       = var.vm_id

  tags = [
    "homelab",
    "iac",
    "core",
    "home-automation",
    "home-assistant",
  ]

  started         = true
  on_boot         = true
  protection      = var.protect_after_build
  stop_on_destroy = true

  bios    = "ovmf"
  machine = "q35"

  efi_disk {
    datastore_id      = var.vm_datastore_id
    type              = "4m"
    pre_enrolled_keys = false
  }

  agent {
    enabled = true
    trim    = true
  }

  cpu {
    cores = var.cpu_cores
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = var.memory_mb
    floating  = var.memory_mb
  }

  scsi_hardware = "virtio-scsi-single"
  boot_order    = ["scsi0"]

  disk {
    datastore_id = var.vm_datastore_id
    import_from  = var.haos_image_id
    interface    = "scsi0"
    iothread     = true
    discard      = "on"
    ssd          = true
    size         = var.disk_size_gb
  }

  network_device {
    bridge      = var.bridge
    model       = "virtio"
    mac_address = var.mac_address
  }

  operating_system {
    type = "l26"
  }

  serial_device {}
}
