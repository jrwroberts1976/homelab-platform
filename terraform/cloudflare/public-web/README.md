# Public website - Cloudflare Pages

This Terraform stack creates the Cloudflare Pages project used to move
`me.jrwroberts.co.uk` off the homelab.

## Safety model

The first apply creates only the Pages project.

`enable_custom_domain` defaults to `false`, so the existing public DNS path is not changed during bootstrap.

The custom domain is registered only after the Pages preview has been validated. Existing DNS must be captured/imported before any record cutover so the current home-hosted site remains a rollback path.

## Authentication

Do not put a Cloudflare API token in Git.

Export it to the Terraform process as:

```bash
export CLOUDFLARE_API_TOKEN='...'
```

Set the non-secret account ID in a local tfvars file copied from
`terraform.tfvars.example`.

## Bootstrap

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

The expected first apply creates:

- Pages project: `engineering-portfolio`
- production branch metadata: `main`

It does **not** enable the custom domain.

## Deployment

The application repository `jrwroberts1976/engineering-portfolio` contains a manual Cloudflare Pages preview workflow. It builds the Astro static site and deploys `dist/` to the Pages project.

Required GitHub repository secrets:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

No secret value is committed or printed.

## Cutover gate

Do not enable `me.jrwroberts.co.uk` until all of these pass:

- Pages preview returns HTTP 200
- main navigation works
- project pages render
- CV/PDF downloads work
- static assets and favicons load
- canonical URLs remain `https://me.jrwroberts.co.uk`
- current Cloudflare DNS record for `me` is recorded
- rollback to the current homelab origin is understood

After validation, set:

```hcl
enable_custom_domain = true
```

and review a Terraform plan before apply. DNS cutover is a separate controlled step.
