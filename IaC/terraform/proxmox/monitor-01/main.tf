resource "proxmox_virtual_environment_download_file" "debian_cloud_image" {
  content_type       = "import"
  datastore_id       = var.image_datastore_id
  node_name          = var.proxmox_node_name
  url                = var.debian_cloud_image_url
  file_name          = "debian-13-genericcloud-amd64-20260712-2537.qcow2"
  checksum           = var.debian_cloud_image_sha512
  checksum_algorithm = "sha512"
  overwrite          = false
}

resource "proxmox_virtual_environment_file" "cloud_init_user_data" {
  content_type = "snippets"
  datastore_id = var.image_datastore_id
  node_name    = var.proxmox_node_name

  source_raw {
    file_name = "${var.hostname}-user-data.yaml"

    data = <<-EOF
    #cloud-config
    hostname: ${var.hostname}
    fqdn: ${var.hostname}.${var.domain}
    manage_etc_hosts: true
    timezone: Europe/London
    ssh_pwauth: false

    users:
      - default
      - name: james
        groups:
          - sudo
        shell: /bin/bash
        ssh_authorized_keys:
          - ${trimspace(var.ssh_public_key)}
        sudo: ALL=(ALL) NOPASSWD:ALL

    package_update: true
    packages:
      - qemu-guest-agent
      - python3
      - sudo

    runcmd:
      - systemctl enable qemu-guest-agent
      - systemctl start qemu-guest-agent
      - touch /var/lib/cloud/monitor-01-bootstrap-complete
    EOF
  }
}

resource "proxmox_virtual_environment_vm" "monitor" {
  name        = var.hostname
  description = "Homelab monitoring platform managed by homelab-platform/IaC"
  node_name   = var.proxmox_node_name
  vm_id       = var.vm_id

  started         = true
  on_boot         = true
  protection      = var.protect_after_build
  stop_on_destroy = true

  tags = [
    "grafana",
    "iac",
    "monitoring",
    "prometheus",
  ]

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
    import_from  = proxmox_virtual_environment_download_file.debian_cloud_image.id
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

    user_data_file_id = proxmox_virtual_environment_file.cloud_init_user_data.id
  }

  network_device {
    bridge = var.bridge
    model  = "virtio"
  }

  operating_system {
    type = "l26"
  }

  serial_device {}

  startup {
    order      = 20
    up_delay   = 10
    down_delay = 10
  }
}
