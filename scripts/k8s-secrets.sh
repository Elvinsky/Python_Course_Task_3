#!/usr/bin/env bash
# Create the Secrets the Deployments read (auth-secrets, core-secrets) without committing any value.
#
# The databases and Redis run in docker compose on your machine; from inside a k3d pod they are reachable
# at host.k3d.internal (compose publishes auth-db on 5433, core-db on 5434 and redis on 6379).
# Override any value by exporting the variable first.
set -euo pipefail

NAMESPACE=kickstart
JWT_SECRET="${JWT_SECRET:-$(openssl rand -hex 32)}"
AUTH_DATABASE_URL="${AUTH_DATABASE_URL:-postgresql+asyncpg://auth:auth@host.k3d.internal:5433/auth}"
CORE_DATABASE_URL="${CORE_DATABASE_URL:-postgresql+asyncpg://core:core@host.k3d.internal:5434/core}"
REDIS_URL="${REDIS_URL:-redis://host.k3d.internal:6379/0}"

kubectl apply -f deploy/k8s/base/namespace.yaml

kubectl -n "$NAMESPACE" create secret generic auth-secrets \
  --from-literal=DATABASE_URL="$AUTH_DATABASE_URL" \
  --from-literal=REDIS_URL="$REDIS_URL" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl -n "$NAMESPACE" create secret generic core-secrets \
  --from-literal=DATABASE_URL="$CORE_DATABASE_URL" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secrets auth-secrets and core-secrets are in namespace $NAMESPACE."
