resource "proxmox_virtual_environment_container" "resolver" {
  node_name    = var.proxmox_node_name
  vm_id        = var.vm_id
  description  = "DNS resolver managed from homelab-platform/IaC"
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
    name     = "eth0"
    bridge   = var.bridge
    firewall = false
  }

  operating_system {
    template_file_id = var.template_file_id
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

  # Debian 13/systemd needs LXC nesting. The scoped API identity cannot safely
  # manage the provider's full features structure, so the deployment wrapper
  # applies nesting=1 through its separately preflighted bootstrap path.
  lifecycle {
    ignore_changes = [features]
  }
}
