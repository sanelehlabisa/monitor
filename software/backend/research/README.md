# Backend research

Offline experiments live here, outside the application runtime. Do not import
research modules from app code or change production dependencies to run them.

- [Forecasting](forecasting/README.md): simulator.py is the single normal
  entrypoint for offline generation, rolling-linear replay, two graphs and error
  exports. Low/Mid/High controls randomness, not household usage classes.

Use synthetic files only, never the development or household database. Research
results do not approve app integration; Ticket 66.5 requires separate evidence
and approval. Research is excluded from the backend Docker build context.
Matplotlib and NumPy are installed only in the forecasting research environment.
