# Camera firmware (deferred)

Not part of active V1. Future ESP32-class C/C++ firmware has no implementation
or fixed board. Revisit it only if measured manual-entry friction justifies
automation and a new ticket approves the work.

Record board, camera, PSRAM/flash, toolchain and pin mapping before coding.
Keep capture, recognition and transport boundaries small and testable.
Use device credentials; do not embed private credentials in tracked sources.
Document timestamp source, retries and duplicate handling before upload work.
Validate on-device memory and actual timing, not only desktop results.

One preserved setup idea is a temporary local access point where
the owner supplies network details and an authorised owner email. Provisioning
must result in a device UUID and independently revocable credential; it must not
copy a human OTP or browser session onto the device. Firmware implementation and
the final provisioning security details require a future approved ticket.
