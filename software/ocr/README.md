# OCR experiments

Read one real meter reliably before generalising. Tickets 12-15 cover labelled
photos, recognition, balance parsing and rejection/retry of unclear results.
No OCR package, model or dataset is installed by this scaffold.

## PC-first approach

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
reliability. Backend-hosted inference is the preferred initial integration for
fast iteration. Device inference remains a later measured option; this direction
does not prove accuracy, latency or embedded suitability.

Keep large/private local datasets and weights in ignored `data/` and
`models/`; document provenance and reproducible training/export when added.
Only small sanitised fixtures should be considered for version control.

Ticket 15 must represent unreadable images as failures, never guessed balances.
Sampling frequency must support the desired history/alerts; a monthly summary
does not require, or justify, capturing only once a month.
