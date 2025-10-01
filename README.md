# ai-pm Monorepo

This repository contains the platform code for the **ai-pm** project. It is organised as a Turborepo powered PNPM workspace for JavaScript/TypeScript applications alongside Poetry managed Python services.

## Prerequisites

Ensure the following tools are installed before working in the repository:

- [Node.js](https://nodejs.org/) **LTS** (use the Active LTS release)
- [pnpm](https://pnpm.io/) (recommended version 8 or newer)
- [Python](https://www.python.org/) **3.11**
- [Poetry](https://python-poetry.org/) (matching Python 3.11)

## Getting Started

1. Install Node dependencies:

   ```bash
   pnpm install
   ```

2. Bootstrap Python environments for each service (example shown for the API service):

   ```bash
   cd services/api
   poetry install
   ```

3. Use the top-level PNPM scripts to drive the monorepo pipelines:

   ```bash
   pnpm build
   pnpm lint
   pnpm test
   pnpm dev
   ```

   - `pnpm build` runs `turbo run build` with caching for every app/service JavaScript package.
   - `pnpm lint` executes the lint pipeline across workspace packages.
   - `pnpm test` runs the JavaScript test suites with cached outputs (coverage, reports).
   - `pnpm dev` concurrently starts the Python API (`make -C services/api dev`), the Python worker (`make -C services/worker dev`), and the Next.js web app (`pnpm --filter @ai-pm/web dev`).

   Quick check: `pnpm dev` should boot the web experience and surface the API health endpoint once the services finish their startup routines.

## Repository Layout

```
ai-pm/
  apps/           # JavaScript/TypeScript applications
  services/       # Python microservices
  libs/           # Shared libraries (JS & Python)
  infra/          # Infrastructure-as-code
  ops/            # Operational tooling & automation
  tools/          # Developer scripts
```

## Turborepo Pipelines

The repository standardises the following tasks for every JavaScript workspace package in `apps/*` and `services/*`:

- `build` — produces distributable artifacts (`dist/`, `build/`, `.next/`) with cache reuse.
- `lint` — runs static analysis before dependent packages execute their own lint steps.
- `test` — runs package-level tests after builds finish, caching coverage and report directories.
- `dev` — long-lived development servers/watchers; dependency dev tasks start first to keep local linking in sync.

## Contributing

- Use pnpm for JavaScript/TypeScript dependencies and scripts documented above.
- Use Poetry for Python dependencies.
- Keep shared code within the `libs` directory.
- Follow the conventions documented in this README when adding new packages or services.
