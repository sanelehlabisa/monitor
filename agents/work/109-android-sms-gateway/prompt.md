# Task 109: Android SMSGate adapter

## Outcome
Connect the existing sender to SMS Gateway for Android in Local Server mode,
using the owner's SIM and the research .env. Reuse the five/day CSV state flow.

## Questions and answers
- The owner reports sending email successfully and asks for Android setup through
  .env configuration and rerunning the existing script.
- Recommend SMSGate's standard APK from its official release page, Local Server
  mode on the same trusted Wi-Fi as this computer. The owner installs/configures
  the app; do not download/install Android software on their behalf.
- Official local API: POST http://PHONE_IP:PORT/message, Basic Authentication,
  JSON textMessage.text and phoneNumbers containing one destination per request.
  Keep credentials only in the private research .env, not chat or command history.
- The phone IP/port and app credentials will come from its Local Server screen.
  Existing SMS_GATEWAY_URL/USERNAME/PASSWORD keys are sufficient; no API key is
  needed for this local mode. Preserve the working SMTP settings and email history.
- Five real emails are now marked sent; zero SMS are sent/scheduled and no real
  phone-only groups are confirmed. Do not reset or automatically assign them.
- The owner approved Task 109 and installed/configured the app. Existing private
  .env values are sufficient; do not change or print them. Read-only installed
  Swagger confirms /messages and HTTP 202. Earlier local-start docs use legacy
  /message; use /messages for a base URL and respect an explicit legacy path.

## Scope and reuse
1. Extend the existing send_sms boundary in send_due_messages.py for SMSGate's
   documented local request/receipt format and Basic Authentication. Verify the
   exact response contract using current official docs; do not invent a generic
   Android API. Keep two Python scripts, no SDK/framework/service or schema.
2. Support independent email/SMS selection. --channel sms must send no email;
   normal all mode may use real email and the selected real gateway together.
   Canonical real data may never be marked sent by a mock adapter; mock fixtures
   may never reach the real gateway. Preserve existing mock-only defaults.
3. Read only the three research gateway values. Permit the owner's local/private
   IP endpoint with no proxy/redirect forwarding; no public plaintext gateway,
   router changes or TLS-verification bypass. Never echo credentials or response
   bodies that may contain messages/phone data.
4. Reuse channel date eligibility, five attempted contacts/day, lock/atomic saves,
   bounded safe retries, email-first groups and suppression/reply checks. Record
   a valid queued receipt in the existing private attempt log, without adding
   a table/CSV column. A gateway receipt means accepted for sending, not confirmed
   handset delivery. Unknown acceptance stays held; never retry blindly.
5. Update the safe .env.example and concise setup/run instructions. Actual SMTP
   keys and real delivery fields remain unchanged. The owner enters gateway
   secrets locally; do not solicit them in chat.
6. No automatic selection/scheduling of the 917 phone records. Explain confirming
   phone-only/mobile eligibility and setting sms_scheduled_at before production.
   The owner first tests to their own number via the app docs/UI. Sending to real
   research contacts is a later explicit owner action, not agent verification.

## Verification
Controlled local fake-server tests cover the real API body/auth/receipt contract,
success/rejection/timeout, sanitized errors, five/day/restart/no duplicates and
ambiguous holds. Check mixed transport guards and SMS-only email isolation.
Verify old mocks still work and preserve current canonical CSV/email attempts/
SMTP settings. Phone reachability may be checked read-only after configuration;
do not send a real SMS, install an app or alter contacts during this task.

## Exclusions
No live-contact messages, bulk scheduling, automatic follow-ups, inbox polling,
cloud gateway, Android installation, app Compose changes, commit or push.

## References
- https://docs.sms-gate.app/installation/
- https://docs.sms-gate.app/getting-started/local-server/
- https://docs.sms-gate.app/integration/api/
- https://github.com/capcom6/android-sms-gateway/releases/latest
