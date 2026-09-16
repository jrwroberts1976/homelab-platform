resource "proxmox_virtual_environment_vm" "greenbone" {
  name        = var.hostname
  description = "Homelab Greenbone vulnerability management platform managed by homelab-platform/IaC"
  node_name   = var.proxmox_node_name
  vm_id       = var.vm_id

  tags = [
    "homelab",
    "iac",
    "security",
    "scanner",
    "greenbone",
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
    import_from  = var.debian_cloud_image_id
    interface    = "scsi0"
    iothread     = true
    discard      = "on"
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

    user_data_file_id = "local:snippets/greenbone-01-user-data.yaml"
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
