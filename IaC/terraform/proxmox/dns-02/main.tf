resource "proxmox_download_file" "debian13_lxc" {
  content_type        = "vztmpl"
  datastore_id        = var.template_datastore_id
  node_name           = var.proxmox_node_name
  url                 = var.debian_template_url
  file_name           = var.debian_template_file_name
  overwrite           = false
  overwrite_unmanaged = false
  upload_timeout      = 900
  verify              = true
}

resource "proxmox_virtual_environment_container" "dns02" {
  node_name    = var.proxmox_node_name
  vm_id        = var.vm_id
  description  = "Secondary DNS (Pi-hole + Unbound) managed from homelab-platform/IaC"
  unprivileged = true

  started       = true
  start_on_boot = true
  protection    = var.protect_after_build

  cpu {
    cores = var.cpu_cores
  }

  memory {
    dedicated = var.memory_mb
    swap      = var.swap_mb
  }

  disk {
    datastore_id = var.rootfs_datastore_id
    size         = var.disk_size_gb
  }

  initialization {
    hostname = var.hostname

    dns {
      domain  = var.search_domain
      servers = var.bootstrap_dns_servers
    }

    ip_config {
      ipv4 {
        address = var.ipv4_cidr
        gateway = var.ipv4_gateway
      }
    }

    user_account {
      keys = var.ssh_public_keys
    }
  }

  network_interface {
    name     = "veth0"
    bridge   = var.bridge
    firewall = var.enable_pve_firewall
  }

  operating_system {
    template_file_id = proxmox_download_file.debian13_lxc.id
    type             = "debian"
  }

  tags = [
    "dns",
    "iac",
    "pihole",
    "unbound",
  ]

  startup {
    order      = 10
    up_delay   = 5
    down_delay = 5
  }

  wait_for_ip {
    ipv4 = true
  }
}
