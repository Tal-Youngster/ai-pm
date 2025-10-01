# syntax=docker/dockerfile:1.7
FROM node:20-alpine AS base

ENV PNPM_HOME=/root/.local/share/pnpm \
    PATH=/root/.local/share/pnpm:$PATH \
    NEXT_TELEMETRY_DISABLED=1

RUN corepack enable pnpm

WORKDIR /srv/app

# Copy root manifests to install dependencies with maximum cache reuse
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml turbo.json ./
COPY apps/web/package.json ./apps/web/package.json

RUN pnpm install --frozen-lockfile

# Copy application sources and shared packages
COPY apps ./apps
COPY libs ./libs

RUN pnpm --filter @ai-pm/web build

FROM node:20-alpine AS runner

ENV PNPM_HOME=/root/.local/share/pnpm \
    PATH=/root/.local/share/pnpm:$PATH \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

RUN corepack enable pnpm

WORKDIR /srv/app

COPY --from=base /srv/app/package.json ./
COPY --from=base /srv/app/pnpm-workspace.yaml ./
COPY --from=base /srv/app/pnpm-lock.yaml ./
COPY --from=base /srv/app/turbo.json ./
COPY --from=base /srv/app/node_modules ./node_modules
COPY --from=base /srv/app/apps/web ./apps/web
COPY --from=base /srv/app/libs ./libs

# Ensure production dependencies for the web app are present in the runtime image
RUN pnpm install --filter @ai-pm/web --prod --frozen-lockfile

EXPOSE 3000

CMD ["pnpm", "--filter", "@ai-pm/web", "start"]
