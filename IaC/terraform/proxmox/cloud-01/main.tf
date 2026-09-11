resource "proxmox_virtual_environment_vm" "cloud" {
  name        = var.hostname
  description = "Homelab private cloud managed by homelab-platform/IaC"
  node_name   = var.proxmox_node_name
  vm_id       = var.vm_id

  tags = [
    "cloud",
    "core",
    "homelab",
    "iac",
    "nextcloud",
  ]

  started         = true
  on_boot         = true
  protection      = var.protect_after_build
  stop_on_destroy = true
  boot_order      = ["scsi0"]

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [clone]
  }

  clone {
    vm_id        = var.template_vm_id
    node_name    = var.proxmox_node_name
    datastore_id = var.vm_datastore_id
    full         = true
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

  disk {
    datastore_id = var.vm_datastore_id
    interface    = "scsi0"
    iothread     = true
    discard      = "on"
    ssd          = true
    size         = var.disk_size_gb
  }

  disk {
    datastore_id = var.vm_datastore_id
    interface    = "scsi1"
    iothread     = true
    discard      = "on"
    ssd          = true
    size         = var.data_disk_size_gb
  }

  initialization {
    datastore_id = var.vm_datastore_id
    interface    = "ide2"
    upgrade      = true

    dns {
      domain  = var.domain
      servers = var.dns_servers
    }

    ip_config {
      ipv4 {
        address = var.ipv4_cidr
        gateway = var.ipv4_gateway
      }
    }

    user_account {
      username = "james"
      keys     = [trimspace(var.ssh_public_key)]
    }
  }

  network_device {
    bridge       = var.bridge
    model        = "virtio"
    mac_address  = "BC:24:11:E9:49:60"
    disconnected = false
  }

  operating_system {
    type = "l26"
  }

  serial_device {}
}
