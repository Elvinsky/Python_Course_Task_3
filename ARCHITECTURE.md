# Architecture

Fill in every section below (AC 8). Replace each `TODO` with your decisions: the acceptance test
`tests/acceptance/test_ac8_architecture.py` fails while a `TODO` marker or an empty section remains.
Write the contracts BEFORE you implement the services, then keep this file in sync with the code.

## Service boundaries

TODO: What does the Auth service own, what does Core own? Which service calls which (hint: Core never
calls Auth)? Why is identity a separate service?

## JWT claims

TODO: List every claim in the access token (at least `sub`, `role`, `exp`; add `iss` / `aud` if you use
them), their types, the signing algorithm, the token lifetime, and how Core gets the verification key.

## Error format

TODO: The shape of an error response (for example `{"detail": "..."}`), and the status codes both
services use: 401 vs 403, 404, 409, 422.

## Data ownership

TODO: Which tables does Auth own (`users`, ...)? Which does Core own (`items`, `orders`, ...)? How does
Core refer to a user without a foreign key into Auth's database?

## URL prefixes

TODO: The public prefixes behind the Ingress (`/auth` for Auth, `/api` for Core), plus the health endpoints
(`/health`, `/ready`) that are only used by the kubelet.
