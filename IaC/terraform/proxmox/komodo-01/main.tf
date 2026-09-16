resource "proxmox_virtual_environment_vm" "komodo" {
  name        = var.hostname
  description = "Homelab Komodo container-management control plane managed by homelab-platform/IaC"
  node_name   = var.proxmox_node_name
  vm_id       = var.vm_id

  clone {
    vm_id        = var.clone_source_vm_id
    node_name    = var.proxmox_node_name
    datastore_id = var.vm_datastore_id
    full         = true
  }

  tags = [
    "homelab",
    "iac",
    "core",
    "management",
    "komodo",
  ]

  started         = true
  on_boot         = true
  protection      = var.protect_after_build
  stop_on_destroy = true

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
    aio          = "io_uring"
    backup       = true
    cache        = "none"
    discard      = "on"
    iothread     = true
    ssd          = true
    size         = var.disk_size_gb
  }

  initialization {
    datastore_id = var.vm_datastore_id

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

    user_data_file_id = "local:snippets/komodo-01-user-data.yaml"
  }

  network_device {
    bridge = var.bridge
    model  = "virtio"
  }

  operating_system {
    type = "l26"
  }

  serial_device {}
}
