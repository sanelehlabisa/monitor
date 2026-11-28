# Task 111: Nginx security update

## Outcome
Update the existing production Nginx image to the fixed stable release.

## Questions and answers
The owner approved updating all three app repositories, local verification,
committing and pushing master, and providing VPS rollout commands. No unresolved questions.

## Scope and reuse
Pin the existing frontend Dockerfile to official Nginx 1.30.8 Alpine by digest.
Reuse the current proxy configuration, Compose services and deployment guide.

## Verification
Build the production image, run existing frontend checks, and test the production
proxy with isolated local backends/data and the shared edge. Record actual limits.

## Exclusions
No UI, backend behavior, TLS certificates, live VPS deployment, research work,
credentials, database migrations or user-data changes.
