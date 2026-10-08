# OCR experiments (deferred)

OCR is not part of active V1. The app first validates whether fast manual kWh
entry creates enough value; only measured entry friction can justify reopening
automation research. Historical Tickets 12-15 covered labelled photos,
recognition, balance parsing and rejection/retry of unclear results. No OCR
package, model or dataset is installed by this scaffold.

## Preserved future PC-first approach

1. Use saved, consented meter photos as the camera input.
2. Crop the display consistently and label the correct digits, decimal and unit.
3. Test simple display-specific recognition before adding a neural model.
4. If needed, use familiar Python/PyTorch tooling for a small digit model.
5. Measure accuracy on held-out images, including glare and changing digits.
6. Evaluate export/runtime/operator support and peak RAM on the actual ESP32.

Saved-photo tests exercise the pipeline, not a full ESP32-CAM emulator.
An exported model runs through a compatible embedded inference runtime, not
desktop PyTorch installed on the MCU. Five-minute inference may be acceptable
for an experiment but does not remove memory limits or prove monthly reading
reliability. Backend-hosted inference would be the simplest future integration
for rapid experimentation. Device inference would remain a later measured option;
neither direction is approved or evidence of accuracy, latency or embedded
suitability.

Keep large/private local datasets and weights in ignored `data/` and
`models/`; document provenance and reproducible training/export when added.
Only small sanitised fixtures should be considered for version control.

Any future OCR must represent unreadable images as failures, never guessed balances.
Sampling frequency must support the desired history/alerts; a monthly summary
does not require, or justify, capturing only once a month.
