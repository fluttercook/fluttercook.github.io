---
title: "Vision models in production: the parts the demo skips"
description: "Passing an image to a model is one line of code. Deciding what resolution to send, how to handle a 40-page scanned PDF, what to do when the answer is confidently wrong, and what it all costs — that is the actual project."
seoDescription: "Practical engineering for multimodal LLM features: image resolution and token cost, document and PDF handling, structured extraction with schemas, verification strategies, latency, and privacy."
keywords:
  - multimodal llm production
  - vision model document extraction
  - image tokens cost llm
  - ocr vs vision model
  - structured extraction from images
  - pdf processing llm
category: "Guide"
topic: "AI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-05"
emoji: "👁️"
tags: ["AI", "Multimodal", "Vision", "OCR", "Production"]
sources:
  - name: "Vision — Anthropic API documentation"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/vision"
  - name: "Images and vision — OpenAI API documentation"
    url: "https://platform.openai.com/docs/guides/images-vision"
  - name: "PDF support — Anthropic API documentation"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/pdf-support"
  - name: "Tesseract OCR documentation"
    url: "https://tesseract-ocr.github.io/"
  - name: "Pillow — Python imaging library documentation"
    url: "https://pillow.readthedocs.io/"
  - name: "JSON Schema specification"
    url: "https://json-schema.org/"
related:
  - slug: "ai-chunking-strategies-that-matter"
    title: "Chunking for retrieval: the decision that quietly caps your RAG quality"
  - slug: "ai-synthetic-data-for-evals"
    title: "Synthetic data for evals: building a test set you can trust"
draft: false
---

The demo works on the first try: photograph a receipt, get back structured JSON with the merchant, date and total. Then you ship it, and users send you a receipt photographed at an angle in bad light with a thumb over the total, a 40-page scanned contract, a screenshot of a spreadsheet, and a blurry photo of another screen showing a receipt.

The model handles more of that than you would expect, and the parts it does not handle are the ones that determine whether the feature is usable.

## Resolution is the cost dial

Images become tokens, and the count scales with pixel area. The precise formula differs by provider, but the shape is universal: a large image can cost more than a page of text, and most providers downscale images above a maximum dimension before processing anyway.

Two consequences follow.

**Sending a full-resolution phone photo is usually waste.** An 12-megapixel image gets downscaled by the provider, so you paid to upload pixels that were discarded. Resize before sending:

```python
from PIL import Image

def prepare(path, max_dim=1568):
    img = Image.open(path)
    img = img.convert("RGB")
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                         Image.LANCZOS)
    return img
```

Check your provider's documented maximum before fixing that constant — the number changes and differs between APIs.

**But small text needs pixels.** Downscale a dense contract page too far and the model reads plausible-looking wrong words. For document work, the useful move is the opposite of downscaling: **crop and send regions at high resolution** rather than the whole page at low resolution. A table you care about, sent as its own image, is read far more reliably than the same table as one twelfth of a page.

## Documents are not images

A scanned PDF is the most common real input, and treating it as "a list of images" gets you a system that is expensive and forgets everything across page boundaries.

What has worked for me, in order:

1. **If the PDF has a text layer, use it.** A very large share of "scanned" PDFs are digitally generated and contain perfect text. Extract it and skip vision entirely. This single check removes most of the cost from most document pipelines.
2. **If it does not, decide between OCR and a vision model.** Traditional OCR is far cheaper per page and gives you character-level positions; a vision model understands layout, handles handwriting and poor scans better, and can answer questions directly. Running OCR first and giving the model both the image and the OCR text often beats either alone.
3. **Process page by page, carry a running summary.** Sending forty page images in one request is expensive and dilutes attention. Extract per page into a structured record, then reconcile.
4. **Handle tables that span pages explicitly.** Nothing generic does this correctly; you need to detect the continuation and stitch the rows yourself.

## Ask for structure, and validate it

Free-text answers about an image are hard to use and hard to evaluate. Define a schema and require it:

```json
{
  "merchant_name": "string | null",
  "date": "YYYY-MM-DD | null",
  "total": "number | null",
  "currency": "ISO 4217 code | null",
  "line_items": [{"description": "string", "amount": "number"}],
  "unreadable_fields": ["string"],
  "notes": "string"
}
```

Two fields in that schema are the important ones and are usually missing from people's first attempt.

**Nullable everything.** A model asked for a total will produce a total. If the total is obscured by a thumb, forcing a non-null field means you get an invented number rather than an admission. Nulls must be legal and the prompt must say so explicitly.

**An `unreadable_fields` list.** This gives the model somewhere to put uncertainty other than into the value. In my experience it is the single most effective addition to an extraction schema, because it converts silent errors into flagged ones — which is the difference between a feature you can automate and one you cannot.

Then validate: parse the JSON, check types, check the date is a real date, check that line items sum near the total. **Arithmetic verification is free and catches a large share of extraction errors**, and a mismatch is a signal to escalate rather than a reason to discard.

## Verification, because confidence is not calibrated

A vision model returns no probability you can threshold on, and it does not hedge in a way you can parse. Confident wrong answers look exactly like confident right ones. Build verification into the pipeline:

- **Cross-check within the data.** Sums, dates within plausible ranges, IDs matching a known format, totals matching the sum of line items.
- **Check against your own systems.** If the extracted merchant is not in your vendor list, or the invoice number already exists, flag it.
- **Two independent extractions** for high-stakes fields — a second pass with a differently worded prompt, and disagreement routes to a human. This doubles the cost of the few fields that matter, not the whole document.
- **Always keep the source image alongside the extraction**, linked and viewable. Every review workflow needs it, and adding it later means reprocessing.

Design the human step from the start. A feature that extracts 90% of fields correctly is excellent if the remaining 10% land in a review queue, and useless if they land silently in your database.

## Latency, and what the user sees

Vision requests are slower than text requests — the upload, the encoding, and the processing all add up, and a multi-page document multiplies it. That shapes the UX more than anything else:

- Do the resize **on the device**. It cuts upload time on mobile networks dramatically and costs nothing.
- Show progress per page, not one spinner for the whole document.
- Return partial results as they complete. A user who sees the first page's data while page seven is processing perceives a fast system.
- Process asynchronously with a job ID for anything over a few pages. A synchronous request that takes ninety seconds will hit a timeout somewhere in your stack.

## Privacy, which is not optional here

Images carry more than their content. A photo of a receipt may contain a card number in the frame, a person in the background, and GPS coordinates in EXIF.

- **Strip EXIF before upload.** Location, device identifiers and timestamps are in there by default, and users do not expect to send them.
- **Tell users what leaves the device**, plainly, at the point of capture.
- **Set a retention period for uploaded images** and enforce it. "We keep them for debugging" turns into an indefinite archive of your users' documents.
- **Consider on-device pre-processing** to detect and blur regions you do not need — a full card number, a face — before anything is transmitted.
- Check whether your provider's data-retention terms match what you told your users. This is a written commitment, not a technical detail.

## FAQ

**Is a vision model better than dedicated OCR?**

For layout understanding, handwriting, poor scans and answering questions, generally yes. For high-volume plain-text extraction at low cost, OCR still wins. Combining both is often the strongest option.

**Can I send multiple images in one request?**

Yes, and it helps when they are related — comparing two pages, or a document plus a reference. It costs the sum of their tokens, so batch deliberately rather than by default.

**How do I handle rotated or upside-down photos?**

Detect and correct orientation before sending. Models tolerate rotation to a degree, but accuracy drops and you have cheap deterministic tools for this.

**What about video?**

Sample frames and treat them as images unless your provider supports video natively. Frame selection — not model quality — is usually what determines the result.

**Do I need to fine-tune?**

Rarely. Better prompts, better crops and a stricter schema fix most extraction problems at a fraction of the effort.

---

*Image handling, token accounting, size limits and PDF support differ by provider and change over time; check the API documentation linked above for the numbers that apply to your integration rather than relying on the values here. The pipeline ordering, the schema recommendations including `unreadable_fields`, the verification strategies and the privacy checklist are my own judgement from building document-processing features.*
