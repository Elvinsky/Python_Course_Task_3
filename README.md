<!--
  Generated from the Python Kick-Start course: the description and acceptance criteria match the
  task window of the course app. Do not edit by hand; changes are made in the course repository.
-->

# Practical Task 3: Multi-Tenant E-Commerce Auth & Order Microservices on Kubernetes

> Part of **Python Kick-Start**: Section 3: “Get Yourself Familiar” — Auth, Guards & Caching (3 Weeks). This repository is a **forkable template**:
> fork it, clone your fork, and implement everything marked `TODO` until all acceptance tests pass.

## 1. Set up your virtual environment first

> **Do this before you touch any code.** Every task in the course runs inside an isolated virtual
> environment, so dependencies never leak into your system Python (there is no `node_modules`-style
> implicit lookup in Python). Nothing in this repository is guaranteed to work outside it.

You need [git](https://git-scm.com/) and [uv](https://docs.astral.sh/uv/getting-started/installation/)
(a fast package and environment manager that also installs Python for you).

```bash
# install uv once: https://docs.astral.sh/uv/getting-started/installation/
uv python install 3.14
make setup   # creates a virtual environment in the repo root, services/auth and services/core

# then run every acceptance check (they fail until you finish the task)
make check
```

What these commands do:

- `uv python install 3.14` downloads Python 3.14 (the version pinned in `.python-version`). Python 3.12 is the
  minimum the acceptance criteria allow; use 3.13 only if a dependency has no wheels for 3.14 yet.
- `uv sync` creates the `.venv` folder and installs the locked dependencies into it.
- `uv run <command>` always runs inside that environment, so you do not have to activate it. If you prefer to
  activate it: `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows).
- `uv run python --version` must print `Python 3.14.x` (or at least 3.12). If it prints another version, stop and fix
  the environment before continuing.

Common problems:

- `uv: command not found`: install uv and open a new terminal.
- Wrong Python version: run `uv python list` and `uv python install 3.14`, then delete `.venv` and run `uv sync` again.
- `make: command not found` (Windows): run the commands from the `Makefile` by hand, or use WSL / Git Bash.

This repository has **three independent uv projects**, so `make setup` creates three virtual environments:
the repository root (static checks for Dockerfiles, Compose and Kubernetes manifests), `services/auth` and
`services/core`. Run a service's own commands from inside its folder (`cd services/auth && uv run pytest`) or use
the `make` targets from the root.

## 2. Fork, clone and work on your fork

1. **Fork** [Python_Course_Task_3](https://github.com/Elvinsky/Python_Course_Task_3) to your own GitHub account (the *Fork* button, top right).
2. **Clone your fork** (not this repository):

   ```bash
   git clone https://github.com/<your-username>/Python_Course_Task_3.git
   cd Python_Course_Task_3
   ```

3. Set up the virtual environment (section 1), then create a branch: `git switch -c solution`.
4. Search for `TODO` to find everything you have to implement: `grep -rn "TODO" . --exclude-dir=.venv --exclude-dir=.git --exclude=README.md`.
5. Commit small steps. The GitHub Actions workflow in `.github/workflows/ci.yml` runs the same checks as `make check`
   on every push to your fork, so you can see your progress there too.
6. Keep the acceptance tests in `tests/acceptance/` unchanged: they are the definition of "done" for each
   acceptance criterion. Write your own tests next to them.

## 3. Task description

Split an e-commerce backend into two services: an Auth Microservice that owns identities, passwords and one-time codes, and a Core Service that owns products and orders. The Core Service never sees a password; it only trusts signed JWTs and enforces role-based access with reusable dependency guards. Guards and OTP flows are covered by tests, auth events are logged without leaking secrets, and the whole system runs first under Docker Compose and then on a local Kubernetes cluster behind a single Ingress. You work in a fork of the template repository: both services come with configuration, models, Alembic setup, test fixtures and acceptance tests, and the security code, endpoints, Dockerfiles, Compose services, Kubernetes manifests and `ARCHITECTURE.md` are marked `TODO`. Each service has its own virtual environment, so set all of them up first (`make setup`).

## 4. Acceptance criteria

- [ ] **AC 1**: Build Auth Microservice handling registration, password hashing, and Redis OTP verification.
- [ ] **AC 2**: Issue signed JWT bearer tokens upon authentication.
- [ ] **AC 3**: Implement custom security dependency guard in Core Service to decode and validate JWTs.
- [ ] **AC 4**: Enforce RBAC: `user` (order placement), `moderator`/`admin` (price override & stock edits).
- [ ] **AC 5**: Cover the guard matrix with `pytest` (401 missing/invalid/expired token, 403 wrong role, 200 allowed role) and OTP flows with `fakeredis` (success, wrong code, expiry, single use).
- [ ] **AC 6**: Emit structured logs for register, login success/failure and OTP issue/verify, with no passwords, tokens or codes in the output.
- [ ] **AC 7**: Containerize Auth and Core with multi-stage, non-root Dockerfiles; `docker compose up --build` starts both services, their PostgreSQL databases and Redis locally.
- [ ] **AC 8**: Core validates JWTs locally and never calls Auth per request; document service boundaries (owned tables, JWT claims, error format) in `ARCHITECTURE.md`.
- [ ] **AC 9**: Deploy to a local Kubernetes cluster (`k3d`): one Deployment (2 replicas) and ClusterIP Service per service, ConfigMap + Secret for configuration, readiness (`/ready`) and liveness (`/health`) probes, and a single Ingress routing `/auth` to Auth and `/api` to Core.
- [ ] **AC 10**: Run schema migrations as a Kubernetes Job, then demonstrate resilience: delete a Core pod and show traffic keeps flowing, and scale Core to 3 replicas.

## 5. What the template gives you, and what is yours

| Path | State | Purpose |
|---|---|---|
| `Makefile`, `.python-version`, `.github/workflows/ci.yml`, `pyproject.toml` | provided | tooling for the three projects and CI |
| `services/auth/app/{config,models,schemas,deps,database,logging_config,health,main}.py` | provided | settings, `users` table, schemas, dependencies, structlog setup, `/health` and `/ready` |
| `services/auth/app/security.py` | **TODO (AC 1, AC 2)** | `hash_password`, `verify_password` (Argon2id), `create_access_token` (JWT) |
| `services/auth/app/otp.py` | **TODO (AC 1)** | `issue_otp`, `verify_otp` on Redis |
| `services/auth/app/routers/auth.py` | **TODO (AC 1, AC 2, AC 6)** | `/auth/register`, `/auth/verify-otp`, `/auth/login` and the log events |
| `services/auth/tests/test_otp.py` | **TODO (AC 5)** | your OTP tests with fakeredis |
| `services/core/app/{config,models,schemas,deps,database,logging_config,health,main}.py` | provided | settings, `items` and `orders` tables, schemas, dependencies |
| `services/core/app/security.py` | **TODO (AC 3, AC 4)** | `get_current_user` (local JWT validation) and `require_roles` |
| `services/core/app/routers/{items,orders}.py` | **TODO (AC 4)** | price override, stock edit, order placement (the listing endpoint is a worked example) |
| `services/core/tests/test_guards.py` | **TODO (AC 5)** | your guard-matrix tests |
| `services/*/alembic/` | provided, **TODO (AC 10)** | async Alembic environment; you generate the first migration |
| `services/*/Dockerfile` | **TODO (AC 7)** | multi-stage, non-root image |
| `compose.yaml` | **TODO (AC 7)** | databases and Redis are provided; add `auth` and `core` |
| `ARCHITECTURE.md` | **TODO (AC 8)** | boundaries, JWT claims, error format, data ownership, URL prefixes |
| `deploy/k8s/base/{namespace,core}.yaml`, `deploy/k8s/overlays/local/` | provided | the Namespace and a worked example (Deployment + Service for Core) |
| `deploy/k8s/base/{auth,ingress,configmap,secret.example,migrate-job}.yaml` | **TODO (AC 9, AC 10)** | the rest of the manifests, already listed in `kustomization.yaml` |
| `scripts/` | provided | `k3d-up.sh` (cluster and images) and `k8s-secrets.sh` (Secrets, never committed) |
| `**/tests/acceptance/` | provided, do not edit | one file per acceptance criterion |

### Service contracts

**Auth** (mounted under `/auth`):

| Endpoint | Success | Errors |
|---|---|---|
| `POST /auth/register` `{email, password}` | `201` user without password or hash; role `user`, not verified; an OTP is stored in Redis | `409` email exists, `422` invalid body |
| `POST /auth/verify-otp` `{email, code}` | `200` user, now verified; the code is deleted (single use) | `400` or `401` wrong or expired code |
| `POST /auth/login` (OAuth2 password form, `username` = email) | `200` `{access_token, token_type: "bearer"}`; JWT claims `sub` (string), `role`, `exp` | `401` bad credentials, `403` not verified |

OTP: Redis key `otp:{email}`, a 6-digit string, TTL `OTP_TTL_SECONDS`, never returned by the API.
Log events (JSON, structlog): `user_registered`, `otp_issued`, `otp_verified`, `otp_failed`, `login_succeeded`, `login_failed`.
Never log a password, a hash, a code or a token.

**Core** (mounted under `/api`, `/health` and `/ready` at the root):

| Endpoint | Allowed roles | Result |
|---|---|---|
| `GET /api/items` | any authenticated user | `200` list |
| `PATCH /api/items/{item_id}/price` `{price}` | `moderator`, `admin` | `200` item, `404` unknown, `422` invalid |
| `PATCH /api/items/{item_id}/stock` `{stock}` | `moderator`, `admin` | `200` item, `404` unknown, `422` invalid |
| `POST /api/orders` `{item_id, quantity}` | `user` only | `201` order and stock decremented, `404` unknown item, `409` not enough stock |

Missing, malformed, tampered or expired token, or a token without `sub`, `role` or `exp`: `401` with `WWW-Authenticate: Bearer`.
Valid token with the wrong role: `403`. Core validates tokens with the shared key and never calls Auth.

### How the acceptance tests map to the criteria

| Criterion | Checked by |
|---|---|
| AC 1 | `services/auth/tests/acceptance/test_ac1_register_hash_otp.py` |
| AC 2 | `services/auth/tests/acceptance/test_ac2_jwt.py` |
| AC 3 | `services/core/tests/acceptance/test_ac3_jwt_guard.py` |
| AC 4 | `services/core/tests/acceptance/test_ac4_rbac.py` |
| AC 5 | `services/auth/tests/acceptance/test_ac5_learner_tests.py` and `services/core/tests/acceptance/test_ac5_learner_tests.py` check your own tests: 4+ OTP tests (success, wrong code, expiry, single use) and 4+ guard tests mentioning 401, 403 and 200 |
| AC 6 | `services/auth/tests/acceptance/test_ac6_logging.py` |
| AC 7 | `tests/acceptance/test_ac7_containers.py` (Dockerfiles and `compose.yaml`, static checks) |
| AC 8 | `services/core/tests/acceptance/test_ac8_local_validation.py` (no HTTP client in Core) and `tests/acceptance/test_ac8_architecture.py` |
| AC 9 | `tests/acceptance/test_ac9_kubernetes.py` (manifests, parsed with PyYAML) |
| AC 10 | `tests/acceptance/test_ac10_migration_jobs.py` and `services/*/tests/acceptance/test_ac10_migrations.py` |

The acceptance tests do not need Docker, a cluster or PostgreSQL: they use in-memory SQLite and fakeredis, and parse the
YAML files. Things only you can verify by hand (the cluster really running, the resilience demo) are described in the steps.

### Makefile cheat sheet

| Command | What it does |
|---|---|
| `make setup` | `uv sync` in the root, `services/auth` and `services/core` |
| `make lint` / `make typecheck` / `make test` | Ruff, strict Mypy and pytest in all three projects |
| `make check` | all of the above: the definition of "green" |
| `make fmt` | auto-fix Ruff findings and format |
| `make compose-up` / `make compose-down` | the local stack (AC 7) |
| `make k3d-up` / `make k3d-down` | create or delete the local cluster and import the images (AC 9) |
| `make k8s-secrets` / `make k8s-apply` | create the Secrets (never committed) and apply the manifests |

## 6. Step-by-step setup

1. Fork the template and set up every virtual environment with `make setup`. The monorepo layout is ready: `services/auth`, `services/core`, `deploy/k8s/base`, `deploy/k8s/overlays/local`.
2. Write the contracts first in `ARCHITECTURE.md`: JWT claims (`sub`, `role`, `exp`, `iss`, `aud`), the error response shape, which service owns which tables, and the public URL prefixes (`/auth`, `/api`).
3. Build and test Auth in isolation: register (Argon2 hash), login and OTP via Redis, JWT issue, `/health` and `/ready`.
4. Build and test Core in isolation: items and orders, the `require_roles` guard, and the guard-matrix tests. Core only needs the JWT verification key.
5. Write a multi-stage, non-root Dockerfile for each service and a `compose.yaml` with `auth`, `core`, two databases and Redis. Run `docker compose up --build` and click through both Swagger UIs.
6. Create the cluster: `k3d cluster create kickstart -p "8080:80@loadbalancer"`. Build versioned images and import them: `k3d image import kickstart/auth:0.1.0 kickstart/core:0.1.0 -c kickstart`.
7. Write manifests: Namespace, ConfigMap (plain settings), Secret (JWT key, DB URLs; generate them locally, do not commit them), Deployment with probes and resources, Service, and one Ingress.
8. Run migrations as a `Job` (`alembic upgrade head`) before the Deployments roll out. Apply everything with `kubectl apply -k deploy/k8s/overlays/local`.
9. Verify: `kubectl get pods -n kickstart`, `kubectl rollout status`, then call `http://localhost:8080/auth/...` and `http://localhost:8080/api/...`. Delete a Core pod, scale Core to 3, and watch traffic keep working.
10. Run the guard-matrix tests (or a smoke script) against the cluster URL to prove 401, 403 and 200 behave identically to local tests.

### The cluster commands

```bash
# k3d bundles the Traefik ingress controller; port 8080 on your machine -> cluster port 80
k3d cluster create kickstart -p "8080:80@loadbalancer"

docker build -t kickstart/auth:0.1.0 services/auth
docker build -t kickstart/core:0.1.0 services/core
k3d image import kickstart/auth:0.1.0 kickstart/core:0.1.0 -c kickstart

make k8s-secrets          # creates auth-secrets and core-secrets (values are never committed)
make k8s-apply            # kubectl apply -k deploy/k8s/overlays/local
kubectl get pods -n kickstart -w

# resilience demo
kubectl delete pod -n kickstart -l app=core --wait=false
kubectl scale deployment/core -n kickstart --replicas=3

# clean up
k3d cluster delete kickstart
```

`make k3d-up` runs the cluster and image steps for you. PostgreSQL and Redis run in `docker compose`
(`docker compose up -d auth-db core-db redis`); pods reach them at `host.k3d.internal` (ports 5433, 5434 and 6379),
which is what `scripts/k8s-secrets.sh` uses. Run the migration Jobs after the Secrets exist and before the Deployments
become ready. Helm charts or an operator are the alternative if you want the databases inside the cluster.
Do not use Ingress NGINX: the Kubernetes project retired it in March 2026 (this template uses Traefik).

## 7. Tech stack requirements

- FastAPI
- PyJWT
- Argon2 / bcrypt
- Redis (redis-py asyncio)
- PostgreSQL
- SQLAlchemy 2.0
- pytest + fakeredis
- Docker Compose
- Kubernetes (k3d)
- kubectl + Kustomize

## 8. Recommended stack

**Python version:** Python 3.14 (current stable). Fall back to 3.13 if a dependency lacks wheels; 3.12 is the minimum the ACs allow. Pin it per service with `requires-python` and `.python-version`.

**Services**

- FastAPI + Pydantic v2 (one project per service): same stack as Task 2; each service has its own `pyproject.toml` and `uv.lock`
- PyJWT: sign in Auth, verify in Core. Prefer asymmetric keys (RS256 or EdDSA) so Core only holds the public key; HS256 with a shared secret is acceptable for a first iteration
- argon2-cffi (or pwdlib with Argon2): password hashing with Argon2id; bcrypt is the fallback
- redis-py (asyncio) 5+: OTP codes with TTL and rate limiting
- httpx + tenacity: only if services call each other: timeouts always, retries for idempotent requests only
- SQLAlchemy 2.0 async + asyncpg + Alembic: one database and one migration history per service
- structlog: JSON logs with a request/correlation id

**Testing**

- pytest + pytest-asyncio + httpx: API and guard-matrix tests
- fakeredis, freezegun or time-machine: OTP expiry and token expiry without sleeping

**Containers & cluster**

- Docker (BuildKit) + Compose v2: local multi-service environment
- k3d (K3s in Docker) + kubectl: fast local cluster with Traefik ingress included
- Kustomize (base + overlays/local): built into kubectl, enough for this task; Helm optional
- PostgreSQL 16+ and Redis 7+: official images locally; use managed services in real environments
- k9s, Tilt or Skaffold (optional): quality-of-life tools for inspecting the cluster and the inner dev loop

**Avoid**

- Ingress NGINX: retired by the Kubernetes project in March 2026 (use Traefik, or look at Gateway API)
- One shared database or shared tables between Auth and Core
- Calling Auth on every request to validate a token
- `passlib` (unmaintained) and hand-rolled hashing or JWT code
- The `latest` image tag, secrets in images or ConfigMaps, running containers as root

## 9. Architecture guidelines

- Two deployable services, each with its own database/schema; communicate only through JWTs (and HTTP if required).
- Hash passwords with Argon2id (or bcrypt); never log or return hashes.
- Store OTP codes in Redis with a TTL (e.g. 5 min), compare in constant time, delete on first successful use.
- JWT claims: `sub` (user id), `role`, `exp`. Short-lived access tokens; keep the signing secret in an environment variable.
- Guards are FastAPI dependencies (`Depends`) returning the current user, so route handlers stay free of auth code.
- Return 401 for missing/invalid tokens and 403 for authenticated users without the required role.
- Raise domain exceptions in services and translate them to HTTP in exception handlers, not inside business logic.
- Each service has its own database; if both share one PostgreSQL server in dev, use two databases with two users.
- Every pod gets configuration from the environment; images are tagged with a version (never `latest`) and contain no secrets.

## 10. Study first

Topics from the Python Kick-Start roadmap for this section:

- **Authentication & JWT Security**: [FastAPI tutorial: Security](https://fastapi.tiangolo.com/tutorial/security/) · [JWT introduction (jwt.io)](https://jwt.io/introduction)
- **Guards, RBAC & Redis Caching**: [Hands-on Microservices with Django (GitHub)](https://github.com/PacktPublishing/Hands-on-Microservices-with-Django) · [Redis documentation](https://redis.io/docs/)
- **Logging & Structured Error Handling**: [Logging HOWTO](https://docs.python.org/3/howto/logging.html) · [FastAPI: handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) · [structlog](https://www.structlog.org/)
- **Testing Auth, Guards & Redis**: [fakeredis documentation](https://fakeredis.readthedocs.io/) · [FastAPI: testing dependencies with overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/) · [HTTPX documentation](https://www.python-httpx.org/)
- **Microservices: What to Use & How to Set Them Up**: [Microservice architecture pattern (microservices.io)](https://microservices.io/patterns/microservices.html) · [FastAPI in containers](https://fastapi.tiangolo.com/deployment/docker/) · [HTTPX: timeouts](https://www.python-httpx.org/advanced/timeouts/) · [Docker Compose documentation](https://docs.docker.com/compose/)
- **Containers & Kubernetes Essentials**: [Kubernetes basics tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/) · [Kubernetes: liveness, readiness and startup probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) · [Kubernetes: Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) · [k3d (K3s in Docker)](https://k3d.io/) · [Traefik Kubernetes Ingress provider](https://doc.traefik.io/traefik/providers/kubernetes-ingress/) · [Ingress NGINX retirement statement](https://www.kubernetes.io/blog/2026/01/29/ingress-nginx-statement/) · [Gateway API](https://gateway-api.sigs.k8s.io/)

## Definition of done

- [ ] `make check` is green locally and in the CI of your fork
- [ ] `docker compose up --build` starts both services, their databases and Redis
- [ ] The cluster runs two replicas of each service behind one Ingress, and you demonstrated the resilience steps
- [ ] Each service has its committed Alembic migration and `uv.lock`; no secrets, `.env` files or `.venv` are committed
- [ ] `ARCHITECTURE.md` is complete and matches the code
