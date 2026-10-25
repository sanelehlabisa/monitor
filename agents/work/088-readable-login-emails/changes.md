# Task 088 changes

## Result

- Monitor and Job Talk now send multipart/alternative login emails: plain text
  first, then compact HTML with inline monochrome table styles and a prominent
  contiguous code. Leading zeroes are preserved and inserted code is HTML-escaped.
- Retained each subject and expiry source: Monitor OTP_TTL and Job Talk's
  recruiter_code_ttl_minutes. Both versions explain personal use, non-sharing
  and ignoring unrequested emails, followed by the Roventics team/company footer.
- Reused https://roventics.com/images/logo.png and the company homepage. Text
  remains readable if images are blocked. No code or user data is put in links.
- User confirmed no copy button; there are no scripts, copy hints, extra pages,
  auth changes, new dependencies or SMTP changes. Existing message functions
  remain the integration points. Reminder and recruiter-access emails are unchanged.
- Ticket 70 stays open for reminder HTML/app links. Job Talk records JT-097;
  its feature branch is codex/088-login-email-layout. Changes are uncommitted.

## Checks

- Monitor: 6 focused email tests passed using cached production dependencies,
  readonly source mounting, synthetic environment values and network disabled.
- Job Talk: 7 focused email tests passed with the existing matching dependency
  image, readonly source/candidate mounting, mocked SMTP, network disabled and
  disposable /tmp SQLite configuration. Existing admin-notification checks pass.
- MIME bytes were round-tripped, confirming plain/HTML order, code and expiry
  agreement, escaping and retained TLS transport behavior.
- Four browser previews passed at 800px and 320px with no horizontal overflow;
  visually reviewed both narrow screenshots. Public logo loaded, code stayed
  contiguous and prominent, and footer/security text was readable.
- Initial preview harness mistakes (escaped digit matching and different fixture
  codes) were corrected; no app changes were required. These are HTML previews,
  not full Gmail/Outlook inbox-client acceptance.
- Temporary test containers and isolated browser were cleaned; no source services,
  real email, live database, environment files, certificates or other sites changed.
- Evidence: .tmp/task088/monitor-tests.log, monitor-checks.json,
  jobtalk-email-tests.log, jobtalk-email-check-results.json, preview-results.json,
  synthetic .eml/.html files and screenshots. No files were deleted.
- Existing Job Talk server-output.md was preserved outside the changes.

The user accepted selectable text after the email-client scripting limitation was
explained. Reference: [Mailchimp HTML-email limitations](https://mailchimp.com/help/limitations-of-html-email/).

## Publication follow-up

On 25 October 2026 the user approved committing and pushing both app repositories
to master, including Job Talk's feature-branch merge. Earlier uncommitted/no-push
wording describes implementation completion. Publication reuses the passing
focused checks and reviewed code; no further implementation changes were made.
Backend rebuilds and the optional existing-proxy reload are operator commands,
not executed on the VPS by this Git handoff.
