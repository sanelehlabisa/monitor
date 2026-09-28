# Frontend

React and Material UI authenticated shell. It uses `keycloak-js` with the
secret-free `monitor-web` client, Authorization Code + S256 PKCE and in-memory
browser session handling. After login it refreshes the access token, calls the
backend `/auth/me` endpoint and displays only the validated username/email.

Configuration uses `VITE_` variables listed in `.env.example`. Run checks from
this directory with:

```powershell
npm test
npm run build
```

Tickets 17-21 add current balance, timestamp, history, graph, warning threshold
and device/reading freshness.

Distinguish stale or uncertain readings from a current balance. Do not display
anomaly flags as proof of theft. The current shell proves user login and API
identity integration only; it does not imply that meter data exists.
