output "pages_project_name" {
  value = cloudflare_pages_project.engineering_portfolio.name
}

output "pages_subdomain" {
  value = cloudflare_pages_project.engineering_portfolio.subdomain
}

output "custom_domain_enabled" {
  value = var.enable_custom_domain
}
