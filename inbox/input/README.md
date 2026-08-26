# inbox/input

Channel adapters drop **raw** lead files here (PDF, images, original messages).

A separate document service (Tesseract or Azure AI Document Intelligence) must:

1. Extract body text, tables as markdown, and image descriptions as text.
2. Write `.md` / `.txt` files.
3. Move the lead folder to `inbox/pending/`.

This repository **does not read `input/`** and does not run OCR. See `docs/adrs/adr001.md`.
