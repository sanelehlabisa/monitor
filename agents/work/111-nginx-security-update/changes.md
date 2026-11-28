# Task 111: Nginx security update

Pinned the existing production frontend to official nginx:1.30.8-alpine at digest
sha256:8eb04fe3b385090e9aa02961f77398ad09b6bf33ab07f6669a5bb7acce22c0d3.
Reused Docker build, runtime template and shared routing without UI, backend,
Compose, TLS, environment or research-data changes.

Production TypeScript/Vite build passes with the existing bundle-size warning.
All 44 frontend and 228 backend checks pass. Backend checks use disposable
PostgreSQL and existing synthetic seed fixtures, not user data. Shared HTTPS
edge checks pass: 1280/390px rendering, redirects, metadata, foreign-origin
rejection, captured OTP, secure cookie, meter create/delete and logout.
No JavaScript errors or overflow. Nginx syntax/version pass. No real mail,
live VPS or certificate renewal was tested.

Owner approved committing/pushing master. Existing task 110 research work,
including staged files and agents/context.md, is excluded. Frontend-only rollout
is in software/nginx/README.md; Roventics contains the all-three-app rollout guide.
