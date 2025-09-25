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

3. Run repository-wide tasks through `pnpm` or `make` (placeholders for now):

   ```bash
   pnpm turbo run build
   make -f ops/makefile setup
   ```

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

## Contributing

- Use pnpm for JavaScript/TypeScript dependencies.
- Use Poetry for Python dependencies.
- Keep shared code within the `libs` directory.
- Follow the conventions documented in this README when adding new packages or services.
