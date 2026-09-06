resource "cloudflare_pages_project" "engineering_portfolio" {
  account_id        = var.cloudflare_account_id
  name              = "engineering-portfolio"
  production_branch = "main"
}

resource "cloudflare_pages_domain" "portfolio" {
  count = var.enable_custom_domain ? 1 : 0

  account_id   = var.cloudflare_account_id
  project_name = cloudflare_pages_project.engineering_portfolio.name
  name         = "me.jrwroberts.co.uk"
}
