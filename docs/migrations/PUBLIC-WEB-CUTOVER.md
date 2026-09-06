# Public Website Cutover Runbook

Status: preview deployment validated; production custom-domain association initiated and currently initializing.

Target site: `https://me.jrwroberts.co.uk`  
Cloudflare Pages project: `engineering-portfolio`

## Completed

- Astro static build confirmed.
- Cloudflare Pages project created.
- Migration preview deployed successfully.
- Preview rendering and site navigation manually validated.
- Existing home-hosted site remains live as rollback.

## Pre-cutover gate

Current production DNS captured on 2026-09-06:

```text
Name: me.jrwroberts.co.uk
Type: CNAME
Target: jrwroberts.co.uk
Proxy: Proxied
TTL: Auto
```

This record is the rollback reference for the current home-hosted site.

Before associating the custom domain:

1. record the current Cloudflare DNS record for `me.jrwroberts.co.uk`
2. record its current type, target/content, proxy state and TTL
3. confirm the current home-hosted origin remains healthy
4. confirm the Pages preview remains healthy
5. confirm the rollback action: restore the previous DNS record and remove/disable the Pages custom-domain association if required

Do not delete the current home-hosted deployment during cutover.

## Cutover

The custom domain must be associated with the Pages project before relying on a CNAME to the Pages endpoint. Cloudflare documents that manually pointing DNS at Pages without first associating the custom domain can fail.

For a subdomain already in a Cloudflare-managed zone, the intended target is:

```text
me.jrwroberts.co.uk
  -> Cloudflare Pages custom domain
  -> engineering-portfolio.pages.dev
```

The existing Pages token is scoped to Pages Read/Edit and is sufficient for the Pages-domain association.

## Cutover state

Cloudflare custom-domain association for `me.jrwroberts.co.uk` has been initiated. Cloudflare currently reports the domain as **Initializing**.

No home-hosted service should be retired while this state is pending. Wait for Cloudflare to report the custom domain as active before final production validation.

## Validation

After cutover prove:

- `https://me.jrwroberts.co.uk/` returns the Pages version
- HTTPS certificate is valid
- homepage renders correctly
- deep links refresh without 404
- project pages load
- CV/PDF downloads work
- favicons/static assets load
- canonical URLs remain `https://me.jrwroberts.co.uk`
- site is reachable while the homelab web container/origin is stopped temporarily for a controlled proof

## Rollback

If validation fails:

1. restore the recorded previous DNS record
2. verify the old home-hosted site responds
3. leave Pages preview available for diagnosis
4. do not retire the homelab web route/container

## Retirement gate

Only after the production custom domain has remained healthy and a controlled home-origin stop proves independence may the following be retired:

- home-hosted portfolio container
- reverse-proxy route for the public portfolio
- any tunnel/DDNS dependency used only by the public portfolio

Retirement is a separate reviewed change.
