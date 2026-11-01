# G01 Meta console gate note — 2026-11-01

Method: (1) official Meta Model API docs at `dev.meta.ai/docs/*` plus the
`meta-models/meta-model-cookbook` SAM recipe; (2) **second pass 2026-11-01 in
the real BrowserOS Neo browser** (MCP `http://127.0.0.1:9010/mcp`, server
`browseros-neo 0.0.72`, session group `meta-console-gate`): after human
sign-in the authenticated console was opened and read — Dashboard
(`dev.meta.ai/platform`), Models (`/platform/models`), API keys
(`/api-keys`), Usage (`/usage`), Segment playground
(`/playground/segmentation?model_id=sam-3.1`) with SAM settings dialog, and
Chat playground (`model_id=muse-wonder-1.0`); (3) live API cross-check with
the team key: `GET https://api.meta.ai/v1/models` returned 9 ids including
`muse-wonder-1.0`, `sam-3.1`, `muse-spark-1.3`. No value below is invented:
every VERIFIED row cites the doc page or console page it came from. Code/docs
grep confirms no invented endpoint or model id in the repo (`api/*.py` reads
`META_API_KEY`/`META_API_BASE`/`META_PARSE_MODEL` from env only; `*.md` name
only generic "Muse Spark" / "SAM 3.1" / "Meta Model API"). Full keys are
never recorded here — masked form only.

## 1. Muse Spark — VERIFIED (docs)

- Base URL: `https://api.meta.ai/v1`
  Source: `dev.meta.ai/docs/models`, `/docs/image-understanding`,
  `/docs/sam/overview` (`baseURL: "https://api.meta.ai/v1"` in every example).
- Endpoints (all three carry Spark):
  `POST /v1/responses` (recommended, only one that carries reasoning across
  turns), `POST /v1/chat/completions`, `POST /v1/messages`
  (Anthropic-compatible). Source: `dev.meta.ai/docs/models` use-case table,
  `promptfoo.dev/docs/providers/meta` (base URL + surface mapping).
- Full Responses URL: `https://api.meta.ai/v1/responses`.
  Note: repo `.env` value `META_API_BASE=https://api.meta.ai/v1/responses`
  matches this exactly. `.env` is git-ignored, not a doc claim.
- Auth: `Authorization: Bearer $MODEL_API_KEY`, key format `LLM_<id>_<secret>`,
  created in the Model API dashboard. Source: `dev.meta.ai/docs/authentication`.
- Model ids: `muse-spark-1.3` (latest, recommended for new work),
  `muse-spark-1.2`, `muse-spark-1.1`,
  `muse-spark-1.3-contributor`, `muse-spark-1.2-contributor`
  (Contributor mode = discounted, content may train future models; Standard
  mode = content not used for training). Source: `dev.meta.ai/docs/models`
  ("Muse Spark availability"), `/docs/pricing-rate-limits`.
  Note: repo `.env` value `META_PARSE_MODEL=muse-spark-1.3` matches.
- Multimodal image-input format (Spark reads visuals, returns text):
  - Responses API: `{"type": "input_image",
    "image_url": "<public URL | data:image/...;base64,...>"}` or
    `{"type": "input_image", "file_id": "file-..."}` (Files API upload);
    also `input_file` with `file_url` for server-fetched URLs.
  - Chat Completions: `{"type": "image_url", "image_url":
    {"url": "<public URL | data URL>"}}` (object wrapper, not plain string).
  - Up to 50 images per request (a PDF contributes at most its first
    50 page-images); per-image inline max 50 MB (50,000,000 bytes);
    Files API upload max 1 GiB; MIME `image/jpeg`, `image/jpg` (alias),
    `image/png`, `image/gif`, `image/webp`, `image/x-icon`.
  Source: `dev.meta.ai/docs/image-understanding` ("Provide each image one of
  three ways", "You can include up to 50 images", "Supported formats and
  limits"), `/docs/file-handling` ("Size limits", "PDF handling").
- Spark rate limits (per team): 3000 RPM / 4,000,000 TPM for
  `muse-spark-1.3/1.2/1.1`; 150 RPM / 3,000,000 TPM for contributor variants.
  Source: `dev.meta.ai/docs/pricing-rate-limits` ("Rate limits").

## 2. Muse Wonder — VERIFIED (docs)

- Model id: `muse-wonder-1.0` (in preview). Source: `dev.meta.ai/docs/models`
  ("Muse Wonder availability"), `/docs/pricing-rate-limits` ("Model:
  `muse-wonder-1.0`").
- Endpoint: same as Spark — `https://api.meta.ai/v1` with `POST /v1/responses`,
  `/v1/chat/completions`, `/v1/messages`. "Muse Wonder and Muse Spark take the
  same requests on the same endpoints, so moving a workload between them is a
  model ID change." Source: `dev.meta.ai/docs/models` ("Choose Muse Wonder or
  Muse Spark").
- Auth: same `Bearer $MODEL_API_KEY`. Source: `dev.meta.ai/docs/authentication`
  (every Model API request).
- API availability: pay-as-you-go + every Muse Code plan, Standard mode only
  ("Contributor mode isn't available for Muse Wonder on Model API").
  Source: `dev.meta.ai/docs/models`, `/docs/pricing-rate-limits`.
- Rate limits (per team): 3000 RPM / 4,000,000 TPM.
  Source: `dev.meta.ai/docs/pricing-rate-limits`.
- Context window: **1,048,576 tokens — VERIFIED in BrowserOS Neo** (second
  pass). Docs page read in Neo: "Muse Wonder takes text, image, video, audio,
  and PDF input, returns text, has a 1,048,576-token context window"
  (`dev.meta.ai/docs/models`). Console Models page shows the same card as
  "Context 1M" with Input $4.00 / Cached $0.20 / Output $20.00, matching the
  `dev.meta.ai/models/muse-wonder` pricing table (`muse-wonder-1.0` … `1M`).
  Earlier UNVERIFIED flag is removed; third-party-only status no longer
  applies.

## 3. SAM 3.1 hosted availability — VERIFIED HOSTED (docs)

The "blog confirms checkpoints and Playground only" premise is now stale:
the current official docs list SAM as hosted on Meta Model API.

- Hosted: YES. "Muse Wonder, Muse Spark, Muse Image, Muse Voice Transcribe,
  and Segment Anything Model (SAM) are hosted on Meta Model API"
  (`dev.meta.ai/docs/models`); "Its latest version, SAM 3.1, is now available
  on Meta Model API" (`dev.meta.ai/docs/sam/overview`). Cookbook recipe
  `meta-models/meta-model-cookbook/07_sam/01_api_basics` shows live
  `sam-3.1` image+video runs over the API.
- Model id: `sam-3.1`. Source: `dev.meta.ai/docs/models` ("`| sam-3.1 | Text
  prompt, image, video | Boxes and masks |`"), `/docs/sam/overview`.
- Endpoint: `POST https://api.meta.ai/v1/responses` (`baseURL:
  "https://api.meta.ai/v1"`, `model: "sam-3.1"`), `stream: true` recommended
  (each frame arrives as `response.output_text.delta`, stream ends at
  `response.completed`); non-streaming returns the complete result in one
  response. One concept per request; one request per concept.
  Source: `dev.meta.ai/docs/media-segmentation`, `/docs/sam/segmenting`,
  `/docs/sam/overview`.
- Auth: same `Bearer $MODEL_API_KEY` (`MODEL_API_KEY`, dashboard-created).
  Source: `dev.meta.ai/docs/sam/segmenting` examples, `/docs/authentication`.
- Image encoding: `input_image` part with `image_url` = public URL or base64
  data URL (`data:image/png;base64,...`), or `file_id` from a Files API upload
  (`POST /v1/files`, `purpose=user_data`); video via `input_video` with
  `video_url` (MP4/MOV, H.264/H.265/MPEG-4) or uploaded `file_id`; prompt in
  an `input_text` part as a short noun phrase (`"yellow school bus"`), or box
  / point prompts (`<|point;x=..;y=..;w=..;h=..|>` with `w,h` = media pixels).
  Source: `dev.meta.ai/docs/sam/segmenting` ("Send every coordinate in the
  media's own pixels", "`image_url` / `video_url`: a public URL or a base64
  data URL").
- bbox/mask response schema: `output_text` lane, one line per frame:
  `<Nf>id<|box;x1=..;y1=..;x2=..;y2=..;w=<frameW>;h=<frameH>[;c=<conf>]|>`
  `<|mask;x=0;y=0[;c=<conf>];data=<H>,<W>,<enc>payload|>`, comma-separated
  records, exactly one box + one mask per record, box first. Box corners are
  source pixels; `w,h` repeat the source frame size. Mask `H,W` is
  height-first raster dims (smaller than frame); `<enc>` is `~` lossless
  default or `!` one_bit (set via `metadata.mask_encoding`); decode with
  `decodeMaskToRaster` → row-major `Uint8Array` of `H*W` 0/1 entries
  (`@meta-sam/parser` / `meta_sam_parser`). Zero matches = empty
  `output_text` with `response.completed`, a valid result, not an error.
  Source: `dev.meta.ai/docs/sam/reading-segmentation` (full grammar),
  `/docs/sam/client-libraries`, cookbook `summary.json` / `mask-*.svg`.
- Size limits: **no SAM-specific pixel/resolution cap is published — verified
  negative in BrowserOS Neo** (second pass). Searched in Neo for
  pixel/resolution/dimension/limit on `/docs/sam/segmenting`,
  `/docs/media-segmentation`, `/docs/file-handling`,
  `/docs/image-understanding`, plus the Segment playground and its SAM
  settings dialog (Model `sam-3.1` disabled, Mask encoding Lossless/1-bit,
  Include confidence): no pixel, resolution, or megapixel cap appears
  anywhere. Binding caps are therefore the transport caps only: 50 MB
  (50,000,000 bytes) inline / 1 GiB Files-API upload / 100 GiB team storage
  (`dev.meta.ai/docs/file-handling`). Verified SAM numeric limits that do
  exist: **up to 16 prompted objects** ("More than 16 prompted objects →
  invalid prompt: 17 objects exceed this model's limit of 16") and **video
  tracks up to 16 objects per frame** (`dev.meta.ai/docs/sam/segmenting`).
  Do not invent a pixel number for Kohu; enforce the 50 MB file cap and the
  16-object cap. Earlier UNVERIFIED flag is replaced by this checked
  negative.
- Rate limits: `sam-3.1` 3000 RPM, no TPM (billed per image/frame, not per
  token). Source: `dev.meta.ai/docs/pricing-rate-limits` ("Rate limits").
- Pricing: image segmentation $2.50 / 1,000 images; video $0.20 / 1,000
  frames; each video request billed for at least 50 frames
  (`usage.video_frames_processed` reports billed frames).
  Source: `dev.meta.ai/docs/pricing-rate-limits` ("Segment Anything Model 3.1").

## Fallback (recorded, not triggered)

Hosted SAM is confirmed by the current docs, so no self-host fallback is
triggered. If hosted SAM later proves unreachable from this team/key, self-host
the SAM 3.1 checkpoint and label every such region `region_source='checkpoint'`
(own checkpoint), never as Meta Model API SAM; `pptx-shape` boxes stay
labelled `pptx-shape` and zero-region runs `fallback-text`, per V04.

## Console-dashboard visual check — VERIFIED (BrowserOS Neo, 2026-11-01)

Authenticated console opened in the real BrowserOS Neo browser after human
sign-in (login at `auth.meta.com`, "How will you use the Model API?"; help
request resolved in cockpit). Observed, not inferred:

- Dashboard `dev.meta.ai/platform?team_id=…&project_id=…` (title "Model
  API"): greeting account, primary nav Dashboard / Chat / Image / Audio /
  Segment, team nav API keys / Usage / Models / Billing. Cards: Requests,
  Input tokens, Output tokens (Oct 26–Nov 1), **API keys: 3**, Spend Rp 0.
  Team/project ids are in the URL; they are identifiers, not secrets, and
  are not copied here.
- Models `/platform/models`: cards confirm **Muse Wonder — Context 1M**,
  Input $4.00 / Cached $0.20 / Output $20.00, "Try in playground
  `model_id=muse-wonder-1.0`"; **SAM 3.1 — Segment**, Image $2.50 / 1,000
  images, Video $0.20 / 1,000 frames, playground
  `model_id=sam-3.1`; **Muse Spark 1.3 — Context 1M**, Input $1.25 / Cached
  $0.15 / Output $4.25, playground `model_id=muse-spark-1.3` (Contributor
  card also listed).
- API keys `/api-keys`: 3 pay-as-you-go keys listed by name/project/creator/
  date; the Default Project key shows masked as `LLM_1154...CcLk`, which
  matches the repo `.env` key's prefix/suffix (full key never recorded).
- Usage `/usage`: spend/token/request charts plus dedicated **Video frames
  segmented** and **Images segmented** meters (both 0 so far) — SAM billing
  meters exist for this team.
- Segment playground `model_id=sam-3.1`: examples (Umbrella/Cleat/Spacebar/
  Snowboarder), "Attach image or video", SAM settings dialog with Model
  `sam-3.1` (disabled), Mask encoding Lossless / 1-bit, Include confidence.
  No pixel/resolution cap shown. Chat playground for `muse-wonder-1.0`
  shows "Attach images, videos, PDFs, and text files up to 25MB each" —
  that 25 MB is a playground UI limit, not the API limit (API inline cap
  stays 50 MB per §1/§3).
- Live API cross-check (team key from `.env`, masked only):
  `GET https://api.meta.ai/v1/models` → 9 ids: `muse-wonder-1.0`, `sam-3.1`,
  `muse-spark-1.3-contributor`, `muse-voice-transcribe-1.0`,
  `muse-spark-1.3`, `muse-image-1.0`, `muse-spark-1.2-contributor`,
  `muse-spark-1.2`, `muse-spark-1.1`; single-model GETs for
  `muse-wonder-1.0` / `muse-spark-1.3` / `sam-3.1` each returned
  `owned_by: "meta"`. Entitlement for all three gate models is confirmed
  for this team/key without relying on the dashboard alone.

No UNVERIFIED flags remain in this note. Anything not listed above (for
example a SAM pixel cap) was searched for and does not exist in the checked
console/docs surfaces — see §3 for the binding caps to enforce instead.
