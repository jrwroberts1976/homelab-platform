resource "proxmox_download_file" "debian_cloud_image" {
  content_type       = "import"
  datastore_id       = var.image_datastore_id
  node_name          = var.proxmox_node_name
  url                = var.debian_cloud_image_url
  file_name          = "debian-13-genericcloud-amd64-20260712-2537.qcow2"
  checksum           = var.debian_cloud_image_sha512
  checksum_algorithm = "sha512"
  overwrite          = false
}

resource "proxmox_virtual_environment_vm" "monitor" {
  name        = var.hostname
  description = "Homelab monitoring platform managed by homelab-platform/IaC"
  node_name   = var.proxmox_node_name
  vm_id       = var.vm_id

  tags = [
    "homelab",
    "iac",
    "core",
    "monitoring",
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
    import_from  = proxmox_download_file.debian_cloud_image.id
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

    user_data_file_id = "local:snippets/monitor-01-user-data.yaml"
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
