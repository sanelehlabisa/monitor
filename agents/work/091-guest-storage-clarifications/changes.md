# Task 091 changes

Guest operations use local storage; verified signed-in operations use the backend.
Homepage has guest entry; the guest-only account-saving prompt disappears after login.
The final user answer confirms that this flow saves the existing local meter/history
after successful OTP, with no separate copy screen. Retain local originals, report
server-confirmed success and cover duplicate/retry/partial-success behavior in 68.1.
Ordinary login does not implicitly import data. Checked remembered login is three days.
No speculative schema/index work; no unresolved product questions remain.

Updated root/component READMEs and current context. Previous work stays historical.
This continues the authorized planning task; no product implementation.

Checks: clarified scope, local links, documentation-only diffs and Git whitespace.
Existing source/data/user files preserved. No files deleted, tests added, services changed, commits or pushes.
