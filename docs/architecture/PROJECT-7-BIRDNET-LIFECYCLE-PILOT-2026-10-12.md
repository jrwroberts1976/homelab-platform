# Project 7 — BirdNET-Go Docker Image Lifecycle Pilot

**Date:** 12 October 2026  
**Status:** COMPLETE  
**Project:** Komodo hardening and Docker image lifecycle

## Scope

BirdNET-Go on `docker-01` was used as the low-risk controlled Docker
image-lifecycle canary for Project 7.

## Before

- Image: `ghcr.io/tphakala/birdnet-go:20260823`
- Digest: `sha256:233b94f1d3b27b261ec8d997364db0cb953f3e3b3362a89e9e22ad4a589143d6`
- Persistent paths:
  - `/opt/birdnet-go/config:/config`
  - `/opt/birdnet-go/data:/data`
- Container health: healthy
- Komodo update polling: enabled
- Komodo automatic update: disabled

## Change

BirdNET-Go was upgraded to:

- Image: `ghcr.io/tphakala/birdnet-go:20261010`
- Digest: `sha256:d412e7cc07cd77e7a1ef9d91fbffad1428106277a745c5accd90904a7cfb8b73`

The update was validated before changing the Git-backed Komodo desired state.

Git commit `d21e0518` updated
`IaC/komodo/resources/docker-01.toml` from `20260823` to `20261010`.

Komodo ResourceSync detected exactly one Deployment update with zero
pending deploys. `RunSync` was scoped specifically to the `birdnet-go`
Deployment.

## Final validation

- Git desired state: `20261010`
- Komodo desired state: `20261010`
- `/opt/birdnet-go/compose.yml`: `20261010`
- Running container: `20261010`
- Container health: healthy
- Health failing streak: 0
- ResourceSync pending updates: 0
- ResourceSync pending deploys: 0
- ResourceSync error: none

## Rollback

The previous `20260823` image remains present on `docker-01` and must not
be pruned until the defined rollback-retention period has expired.

Rollback consists of restoring the previous image tag in the authoritative
Git declaration and Compose configuration, redeploying BirdNET-Go, and
revalidating application and container health.

## Outcome

The Project 7 controlled image-lifecycle canary is complete.

This proves the workflow:

1. discover and assess the update;
2. record current image/digest and rollback state;
3. apply one controlled workload update;
4. validate service health;
5. update Git desired state;
6. inspect the Komodo ResourceSync diff;
7. apply ResourceSync only to the intended resource;
8. prove Git, Komodo, Compose and runtime convergence;
9. retain the previous image for rollback.

Project 7 remains open for the remaining estate-wide image audit and
phased container updates.
