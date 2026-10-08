# Monitor hardware (deferred)

Hardware is not part of the active software-only V1. These files preserve early
research in case real usage later proves that manual kWh entry is too inconvenient.
No hardware should be purchased or developed under an active V1 ticket.

The preserved concept uses an external camera to observe an existing prepaid
meter/display. Never open, wire into, modify or bypass the meter. No final ESP32
board, camera, power supply or enclosure has been selected.

- [Firmware](firmware/README.md): C/C++ device code and REST transport.
- [Camera](camera/README.md): readable images, crop, placement and lighting.
- [Mechanical](mechanical/README.md): removable mount/enclosure.
- [Experiments](experiments/README.md): evidence before hardware commitments.

Historical Tickets 10-16 and 21-27 are deferred. If automation is reconsidered,
create a newly approved research ticket with evidence from V1 manual-entry use;
do not resume those tickets implicitly.

Future PC work with saved photos does not
emulate sensor exposure, PSRAM, Wi-Fi power use or inference timing. Compare
on-device OCR feasibility with sending approved image crops to the backend;
do not assume either is already implemented.
