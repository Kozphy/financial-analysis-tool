# Deployment Automation

This repository now includes two deployment-oriented GitHub Actions workflows:

- [container-release.yml](C:/Users/Zixsa/Kozphy/financial-analysis-tool/.github/workflows/container-release.yml) for automated CLI container publishing to GitHub Container Registry
- [deploy-dashboard.yml](C:/Users/Zixsa/Kozphy/financial-analysis-tool/.github/workflows/deploy-dashboard.yml) for automated Streamlit dashboard deployment to a Docker-capable Linux host over SSH

## What Is Automated

### Automated Container Release

- pushes to `main` run a quality gate and publish a container image
- version tags such as `v0.1.0` publish tag-aligned images
- `workflow_dispatch` allows a manual rerun from GitHub Actions

### Automated Dashboard Deployment

- pushes to `main` test, build, publish, and deploy the dashboard container
- `workflow_dispatch` can redeploy an existing image tag for rollback or recovery
- deployment targets a single remote host using Docker Compose and a health-checked Streamlit container

## Workflow Behavior

### CLI Container Release

1. install development dependencies
2. run the unit test suite
3. verify packaging with `python -m build`
4. run a Docker build smoke test
5. publish a multi-architecture image to GitHub Container Registry

### Dashboard Deployment

1. install development and runtime dependencies
2. run the unit test suite
3. verify packaging with `python -m build`
4. build and push the dashboard image defined by [Dockerfile.dashboard](C:/Users/Zixsa/Kozphy/financial-analysis-tool/Dockerfile.dashboard)
5. copy the remote compose file from [dashboard.compose.yaml](C:/Users/Zixsa/Kozphy/financial-analysis-tool/deploy/dashboard.compose.yaml)
6. log in to GitHub Container Registry on the remote host
7. pull the target image and restart the dashboard with `docker compose up -d --wait`

## Published Image Tags

The workflows publish images to:

```text
ghcr.io/<owner>/<repository>
ghcr.io/<owner>/<repository>-dashboard
```

Expected tags include:

- `latest` for the newest successful build on `main`
- `vX.Y.Z` for CLI release tags
- `sha-<commit>` for dashboard deployments and manual rollback targeting

## Deployment Target

The first-pass runtime target is a Docker-capable Linux VPS or VM with:

- Docker Engine
- Docker Compose v2
- network access to GitHub Container Registry

The remote deployment directory defaults to `/opt/financial-analysis-tool` and stores:

- `dashboard.compose.yaml`
- `.env`
- `output/`

## Required Repository Configuration

### GitHub Actions Permissions

- `packages: write` is required so workflows can push images

### Repository Variables

- `DEPLOY_PATH`
  Default remote deploy path. Example: `/opt/financial-analysis-tool`
- `DASHBOARD_PORT`
  External port exposed on the remote host. Example: `8501`
- `DEPLOY_SSH_PORT`
  SSH port for the remote host. Example: `22`

### Repository Secrets

- `DEPLOY_HOST`
  Remote server hostname or IP address
- `DEPLOY_USER`
  SSH user with Docker Compose access
- `DEPLOY_SSH_KEY`
  Private key used by GitHub Actions to connect to the host
- `DEPLOY_GHCR_USERNAME`
  Registry username used on the remote host to pull images
- `DEPLOY_GHCR_TOKEN`
  Registry token with `read:packages`

## Manual Rollback

Use the `Deploy Dashboard` workflow with `workflow_dispatch` and set `image_tag` to a previously published tag such as:

- `latest`
- `sha-<previous commit>`

This skips the build step and redeploys the selected image.

## Local And Remote Assets

- runtime image: [Dockerfile.dashboard](C:/Users/Zixsa/Kozphy/financial-analysis-tool/Dockerfile.dashboard)
- remote compose file: [dashboard.compose.yaml](C:/Users/Zixsa/Kozphy/financial-analysis-tool/deploy/dashboard.compose.yaml)
- example runtime environment: [dashboard.env.example](C:/Users/Zixsa/Kozphy/financial-analysis-tool/deploy/dashboard.env.example)

## Current Scope Boundary

This repository now supports automated container publishing and first-pass automated dashboard deployment, but it still does not include:

- infrastructure provisioning with Terraform, CloudFormation, Pulumi, or Ansible
- multi-environment promotion across dev, staging, and production
- blue-green or canary deployment strategies
- external monitoring or alerting integration
