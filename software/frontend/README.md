# Frontend

React and Material UI application shell. The former Keycloak integration has
been removed. The current screen states that authentication is inactive and
shows a disabled email-code form so development does not imply a working or
secure login before the backend contract exists.

Run checks from this directory with:

```powershell
npm test
npm run build
```

Tickets 45-46 add secure cookie sessions and the real email-to-OTP UI flow.
Tickets 17-21 then add current balance, timestamp, history, graph, warning
threshold and device/reading freshness.

Distinguish stale or uncertain readings from a current balance. Do not display
anomaly flags as proof of theft. The current shell proves only that the Material
UI foundation builds; it does not imply that authentication or meter data exists.
