# Task 031: Admin meter views

## Result

Administrators can switch between their own meter profiles and every meter in
the system, making self-testing quicker without reducing existing access.

## Change and reuse

- Added compact Material UI `My meters` and `All meters` controls for admins.
- Defaulted each admin session to `My meters` and reset that view on logout.
- Filtered the already-loaded list by normalized owner email; no backend query,
  schema or ownership policy changed.
- Kept admin-created meters owned by the signed-in admin. The system-wide view
  continues to identify each owner and all selected-meter management actions
  remain available.
- Added distinct admin empty-state text and left regular-user behavior unchanged.

## Verification

- Frontend tests: `20 passed`, including admin-owned/system-wide rendering.
- Frontend production build: passed.
- `git diff --check`: passed (line-ending conversion warnings only).
