# Camera firmware

Future ESP32-class C/C++ firmware; no implementation or fixed board yet.
Ticket 11 selects/tests capture hardware; Ticket 16 sends readings (or an
explicitly approved image payload) to the REST API after Tickets 10 and 15.

Record board, camera, PSRAM/flash, toolchain and pin mapping before coding.
Keep capture, recognition and transport boundaries small and testable.
Use device credentials; do not embed private credentials in tracked sources.
Document timestamp source, retries and duplicate handling before upload work.
Validate on-device memory and actual timing, not only desktop results.

The proposed first-time setup contract is a temporary local access point where
the owner supplies network details and an authorised owner email. Provisioning
must result in a device UUID and independently revocable credential; it must not
copy a human OTP or browser session onto the device. Firmware implementation and
the final provisioning security details require their own approved ticket.
