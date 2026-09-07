# Cloudflare Pages Production Deployment Pipeline

## Implementation status — 7 September 2026

The production site at `https://me.jrwroberts.co.uk` is now hosted on Cloudflare Pages and has been manually validated in production.

A production GitHub Actions workflow has also been implemented in `jrwroberts1976/engineering-portfolio` on branch `ci/cloudflare-pages-production` and opened as PR #16 (`Automate Cloudflare Pages production deployment`). PR #16 is still open, so manual upload remains the fallback until the workflow is merged and a normal `main` deployment is proven.

The implemented workflow intentionally reuses the repository-level `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` secrets already proven by the preview workflow. A dedicated GitHub `production` Environment remains a future hardening option rather than a current dependency.


## Purpose

This document records the production deployment process for the public engineering portfolio and defines the pipeline that should replace manual Cloudflare Pages uploads.

Production site:

- Source repository: `jrwroberts1976/engineering-portfolio`
- Cloudflare Pages project: `engineering-portfolio`
- Production URL: `https://me.jrwroberts.co.uk`
- Framework: Astro
- Node.js requirement: 22.x
- Build command: `npm run build`
- Build output: `dist/`

A manual production deployment was validated successfully on 7 September 2026 by building the Astro site locally and uploading the contents of `dist/` to the Cloudflare Pages Production deployment.

The objective of the pipeline is to make the same process repeatable, auditable and automatic.

## Existing deployment work

The portfolio repository already contains a Cloudflare Pages preview workflow on branch `migration/cloudflare-pages`:

`.github/workflows/cloudflare-pages-preview.yml`

That workflow already proves the required pattern:

1. Check out the portfolio source.
2. Use Node.js 22.
3. Install dependencies with `npm ci`.
4. Run `npm audit --audit-level=high`.
5. Build the static Astro site with `npm run build`.
6. Deploy `dist/` with Cloudflare Wrangler.

The production workflow should be based on that validated preview workflow rather than introducing a different deployment mechanism.

## Cloudflare credentials

Create a scoped Cloudflare API token for the Pages deployment.

Required Cloudflare access:

- Account scope: the account containing the `engineering-portfolio` Pages project.
- Cloudflare Pages permission: Edit / Pages Write.

Store the following values as GitHub Actions secrets for the portfolio repository, preferably in a GitHub Environment named `production`:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Do not place the API token or account credentials in Git, workflow YAML, documentation, shell history or build artifacts.

`GITHUB_TOKEN` is supplied automatically by GitHub Actions and does not need to be created manually.

## Recommended production workflow

Implemented file:

`.github/workflows/cloudflare-pages-production.yml`

in `jrwroberts1976/engineering-portfolio` (currently in PR #16).

Current implementation:

```yaml
name: Cloudflare Pages Production

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  deployments: write

concurrency:
  group: engineering-portfolio-production
  cancel-in-progress: false

jobs:
  production:
    name: Build and deploy production
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment: production

    env:
      CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}

    steps:
      - name: Checkout
        uses: actions/checkout@v6

      - name: Setup Node
        uses: actions/setup-node@v6
        with:
          node-version: 22
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Dependency security audit
        run: npm audit --audit-level=high

      - name: Build static site
        run: npm run build

      - name: Verify build output
        shell: bash
        run: |
          test -f dist/index.html
          test -d dist/_astro
          echo "Static build gate: PASS"

      - name: Verify Cloudflare credentials
        shell: bash
        run: |
          if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
            echo "CLOUDFLARE_API_TOKEN is not configured."
            exit 2
          fi

          if [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
            echo "CLOUDFLARE_ACCOUNT_ID is not configured."
            exit 2
          fi

          echo "Cloudflare credential gate: PASS"

      - name: Deploy production to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy dist --project-name=engineering-portfolio --branch=main --commit-hash=${{ github.sha }}
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}

      - name: Validate production site
        shell: bash
        run: |
          curl --fail             --silent             --show-error             --location             --retry 5             --retry-delay 5             --retry-all-errors             https://me.jrwroberts.co.uk/             -o /tmp/production-index.html

          test -s /tmp/production-index.html
          echo "Production HTTP validation: PASS"
```

## Production branch requirement

The Cloudflare Pages project's production branch must be `main`.

The Wrangler command:

```bash
npx wrangler pages deploy dist --project-name=engineering-portfolio --branch=main
```

uploads the prebuilt `dist/` directory. A branch matching the Pages project's production branch is treated as a production deployment.

Preview deployments should continue to use a non-production branch name such as:

```text
migration-preview
```

## GitHub Environment

A dedicated GitHub Environment is **not required by the current implementation**. PR #16 reuses the existing repository-level `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` secrets already used successfully by the preview workflow.

A future hardening change may introduce an Environment called `production` with approval and branch restrictions. If that is done, migrate the Cloudflare secrets deliberately and update the workflow in the same reviewed change.

## Intended release flow

The normal release flow should be:

```text
feature branch
      |
      v
pull request
      |
      v
CI / Astro build
      |
      v
merge to main
      |
      v
Cloudflare Pages Production workflow
      |
      +--> npm ci
      +--> npm audit
      +--> npm run build
      +--> verify dist/
      +--> wrangler pages deploy dist
      +--> validate https://me.jrwroberts.co.uk
```

No production deployment should require a developer workstation once this workflow is active.

## Manual fallback

If GitHub Actions or the Cloudflare API is unavailable, the validated manual process is:

```bash
git clone https://github.com/jrwroberts1976/engineering-portfolio.git
cd engineering-portfolio
npm install
npm run build
```

Confirm:

```text
dist/index.html
dist/_astro/
```

Then in Cloudflare Pages:

1. Open the `engineering-portfolio` Pages project.
2. Create a deployment.
3. Select `Production`.
4. Upload the contents of `dist/`.
5. Deploy.
6. Validate `https://me.jrwroberts.co.uk`.

The repository root, `src/`, and `node_modules/` must not be uploaded. Cloudflare receives only the generated static site in `dist/`.

## Validation gates

A production deployment is complete only when all of the following are true:

- GitHub Actions build succeeds.
- `npm audit --audit-level=high` passes.
- `npm run build` succeeds.
- `dist/index.html` exists.
- Wrangler reports a successful Pages deployment.
- `https://me.jrwroberts.co.uk` responds successfully.
- The expected portfolio content is visible through the custom domain.

## Rollback

The previous homelab-hosted site should remain available until the automated Cloudflare production path has been proven through normal releases.

For a bad production deployment:

1. Identify the last known-good Git commit.
2. Revert the bad commit on `main`, or re-run the production workflow from the last known-good revision.
3. Validate `https://me.jrwroberts.co.uk`.
4. Record the failure and corrective action.

Do not solve a failed deployment by editing files directly in Cloudflare. Production content should remain reproducible from Git.

## Security notes

- Never commit Cloudflare API tokens.
- Use a scoped API token rather than the Global API Key.
- Give the token only the Cloudflare Pages permissions it needs.
- Do not expose deployment secrets to pull-request workflows from untrusted branches.
- Keep production deployment restricted to `main`.
- Continue dependency and build validation before deployment.
- Rotate the Cloudflare API token if it is ever printed in a log or terminal shared outside the trusted environment.

## Cloudflare reference

Cloudflare documents CI-based Direct Upload using Wrangler:

- https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/
- https://developers.cloudflare.com/workers/wrangler/commands/pages/
- https://developers.cloudflare.com/pages/configuration/api/

The supported deployment command is:

```bash
npx wrangler pages deploy <DIRECTORY> --project-name=<PROJECT_NAME>
```

For this site the directory is `dist` and the project is `engineering-portfolio`.

## Exit criteria

The manual deployment process can be considered replaced when:

- the production workflow is merged to `main`;
- required GitHub environment secrets are configured;
- a merge to `main` automatically creates a Cloudflare Pages production deployment;
- the post-deployment HTTP validation passes;
- a rollback has been demonstrated or rehearsed;
- manual upload is retained only as an emergency fallback.
