variable "cloudflare_account_id" {
  description = "Cloudflare account ID that owns the Pages project."
  type        = string
}

variable "enable_custom_domain" {
  description = "Register me.jrwroberts.co.uk with the Pages project only after the preview deployment is validated."
  type        = bool
  default     = false
}
