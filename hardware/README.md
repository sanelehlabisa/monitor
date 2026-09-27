# Monitor hardware

Plan only: an external camera observes one existing prepaid meter/display.
Do not open, wire into, modify or bypass the meter. No final ESP32 board,
camera, power supply or enclosure has been selected.

- [Firmware](firmware/README.md): C/C++ device code and REST transport.
- [Camera](camera/README.md): readable images, crop, placement and lighting.
- [Mechanical](mechanical/README.md): removable mount/enclosure.
- [Experiments](experiments/README.md): evidence before hardware commitments.

Tickets 11-12 establish repeatable capture; 22-24 refine placement/lighting
alongside OCR. Ticket 25 follows measured hardware dimensions; 26-27 verify the
complete pipeline over several days. Ticket 16 needs authenticated transport
and an agreed image/reading payload before real uploads.

Develop on PC with saved photos while hardware is unavailable. This does not
emulate sensor exposure, PSRAM, Wi-Fi power use or inference timing. Compare
on-device OCR feasibility with sending approved image crops to the backend;
do not assume either is already implemented.
