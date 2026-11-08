#!/usr/bin/env bash
# Create the local k3d cluster (Traefik ingress included) and import the service images.
# Port 8080 on your machine maps to port 80 of the cluster's load balancer.
set -euo pipefail
cd "$(dirname "$0")/.."

CLUSTER=kickstart
VERSION=0.1.0

if ! k3d cluster list "$CLUSTER" >/dev/null 2>&1; then
  k3d cluster create "$CLUSTER" -p "8080:80@loadbalancer"
fi

docker build -t "kickstart/auth:$VERSION" services/auth
docker build -t "kickstart/core:$VERSION" services/core
k3d image import "kickstart/auth:$VERSION" "kickstart/core:$VERSION" -c "$CLUSTER"

echo "Cluster ready. Next: make k8s-secrets && make k8s-apply"
