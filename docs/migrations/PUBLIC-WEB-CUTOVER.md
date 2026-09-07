# Public Website Cutover Runbook

Status: **PRODUCTION CUTOVER COMPLETE — Cloudflare Pages is serving `me.jrwroberts.co.uk`; deployment automation hardening remains in progress.**

Target site: `https://me.jrwroberts.co.uk`  
Cloudflare Pages project: `engineering-portfolio`

## Completed

- Astro static build confirmed.
- Cloudflare Pages project created.
- Migration preview deployed successfully.
- Preview rendering and site navigation manually validated.
- Production build created from `jrwroberts1976/engineering-portfolio` and manually deployed to Cloudflare Pages on 7 September 2026.
- `https://me.jrwroberts.co.uk` validated against the Cloudflare Pages production deployment.
- Public-site hosting has moved away from the homelab origin.
- Previous home-hosted state is retained only as a rollback reference until the automated production path is proven.

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

The production cutover is complete. `me.jrwroberts.co.uk` is now served from the Cloudflare Pages project `engineering-portfolio` and the production site has been manually validated.

The public portfolio is therefore no longer dependent on the homelab web origin for normal service.

The remaining release-engineering task is to replace manual production upload with the GitHub Actions production workflow. Implementation exists in `jrwroberts1976/engineering-portfolio` PR #16 (`Automate Cloudflare Pages production deployment`) and is pending merge/production proof.

## Validation

Production hosting has been validated manually. Before retiring the old route completely, retain/prove the following:

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

The hosting cutover itself is complete. Retirement of the legacy homelab route remains a separate reviewed change. Before final removal, prove the automated Cloudflare production workflow and, if the legacy origin is still present, perform a controlled stop to demonstrate independence.

The following may then be retired:

- home-hosted portfolio container
- reverse-proxy route for the public portfolio
- any tunnel/DDNS dependency used only by the public portfolio

Retirement is a separate reviewed change.

## Automation status — 7 September 2026

A production GitHub Actions workflow has been implemented in `jrwroberts1976/engineering-portfolio` on branch `ci/cloudflare-pages-production` and opened as PR #16.

The workflow:

- runs on pushes to `main` and by manual dispatch
- uses Node.js 22
- runs `npm ci`
- runs `npm audit --audit-level=high`
- builds Astro with `npm run build`
- verifies `dist/index.html` and `dist/_astro`
- deploys `dist/` to the Cloudflare Pages `engineering-portfolio` project
- validates `https://me.jrwroberts.co.uk/` after deployment

Until PR #16 is merged and a normal `main` deployment has passed, the manual upload process remains the emergency fallback.
