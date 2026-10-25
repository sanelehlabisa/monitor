# Task 088: Readable login emails

## Aim

Make Monitor and Job Talk login codes easy to read in simple Roventics-style emails.

## Clarifications

- The user directly requests compact HTML/CSS, black/white/gray, a prominent code,
  personal-use/non-sharing guidance and Roventics company/team/logo footer.
- Confirmed: omit the copy button because most email clients block its scripting;
  make the code prominent and selectable instead. No copy hint is needed.
- Scope is login-code messages; preserve reminders and recruiter-access notifications.

## Change

- Add an HTML MIME alternative alongside plain text in each existing email function.
- Escape interpolated code; keep the subject, configured expiry and SMTP transport.
- Use inline table styles and the existing public company logo/link, with text fallback.
- Update existing mail checks, documentation and the partial Ticket 70/JT-097 status.

## Reuse

- Standard-library EmailMessage, existing SMTP boundaries, expiry values and logo.

## Verify

- Focused MIME roundtrip, code/expiry, escaping and SMTP/TLS tests with network disabled.
- Synthetic HTML previews at desktop and phone widths; no real SMTP or source data.

## Out of scope

- Authentication changes, code-bearing links, copy-page flows, dependencies,
  environment/proxy changes, real mail, source restarts, commit/push or deployment.
