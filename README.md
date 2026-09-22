# CogVideoX API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/tongyi/wan2.2?utm_source=github&utm_medium=ugc&utm_campaign=cogvideox-dev&utm_content=readme-badge&utm_term=tier-a)

CogVideoX is the open video diffusion transformer family from Zhipu AI and Tsinghua University, best known for turning a still image plus a prompt into a short clip. This package is a CogVideoX-class video generation API client for Python: one `pip install` gives you image-to-video and text-to-video as HTTPS calls, with no 5B-parameter checkpoints to download and no GPU to provision.

You get a blocking `run()` that returns the video URL, a submit-and-poll path (clips take a minute or more, so you will want it), webhook delivery on completion, and one runtime dependency (`httpx`). It is built for content pipelines, product demos and research scripts that need generated video without owning inference hardware.

> **Try it now:** [https://synexa.ai/explore/tongyi/wan2.2](https://synexa.ai/explore/tongyi/wan2.2?utm_source=github&utm_medium=ugc&utm_campaign=cogvideox-dev&utm_content=readme-top&utm_term=tier-a) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About CogVideoX](#about-cogvideox)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **No GPU to provision.** CogVideoX-5B in bf16 wants a 24 GB class card for comfortable inference, and CPU offload makes each clip take many minutes. The hosted endpoints run on managed GPUs.
- **No environment to maintain.** No diffusers/PyTorch/CUDA version matching, no multi-gigabyte T5 and transformer downloads, no VAE tiling tuning. Install, set a key, call `run()`.
- **No cold starts on your side.** Loading a video diffusion model and its text encoder takes minutes; keeping them warm costs money around the clock. Here you pay per prediction only.
- **Known price per clip.** `tongyi/wan2.2` image-to-video is $0.20 per run; `bytedance/seedance-2.5` text-to-video is $0.473 per run for clips up to 30 seconds with audio. No idle GPU billing.

## Installation

```bash
pip install git+https://github.com/cogvideox-dev/cogvideox-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=cogvideox-dev&utm_content=readme-apikey&utm_term=tier-a)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import cogvideox_api

output = cogvideox_api.run({
    "prompt": "A woman is talking",
    "input_image": "https://example.com/input.png"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from cogvideox_api import Client

client = Client(api_key="sk-...")
output = client.run({"prompt": "A woman is talking", "input_image": "https://example.com/input.png"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`tongyi/wan2.2`](https://synexa.ai/explore/tongyi/wan2.2?utm_source=github&utm_medium=ugc&utm_campaign=cogvideox-dev&utm_content=readme-models&utm_term=tier-a) | image-to-video | Generate 5s 480p videos using Wan 2.2 14B. A comprehensive video foundation models that pushes the boundaries of video generation. | $0.2 |
| [`bytedance/seedance-2.5`](https://synexa.ai/explore/bytedance/seedance-2.5?utm_source=github&utm_medium=ugc&utm_campaign=cogvideox-dev&utm_content=readme-models&utm_term=tier-a) | text-to-video | Seedance 2.5 generates a single-shot video of up to 30 seconds from a text prompt, with synchronised audio. | $0.473 |

The default model is **`tongyi/wan2.2`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `tongyi/wan2.2`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A woman is talking` | — | Input prompt |
| `input_image` | file | yes | `https://files.synexa.ai/models/wan-image…` | — | Input image to start generating from |
| `aspect_ratio` | string | no | `9:16` | 9:16, 1:1, 16:9 | Video Resolution |
| `seed` | integer | no | `random` | — | Random seed. Leave blank to randomize the seed |
| `num_frames` | integer | no | `81` | 1, 81 | Video Frames |

### `bytedance/seedance-2.5`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A lone fisherman rows out at dawn across…` | — | The text prompt used to generate the video |
| `resolution` | string | no | `720p` | 480p, 720p, 1080p | Video resolution - 480p for faster generation, 720p for balance, 1080p for high quality. |
| `duration` | string | no | `auto` | auto, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 1… | Duration of the video in seconds. Supports 4 to 30 seconds, or auto to let the model decide based on the prompt. |
| `aspect_ratio` | string | no | `auto` | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | The aspect ratio of the generated video. Use 16:9 for landscape, 9:16 for portrait/vertical, 1:1 for square, 21:9 for ultrawide cinematic, or auto to let the model decide. |
| `generate_audio` | boolean | no | `True` | — | Whether to generate synchronized audio for the video, including sound effects, ambient sounds, and lip-synced speech. The cost of video generation is the same regardless of whether audio is generated or not. |
| `bitrate_mode` | string | no | `standard` | standard, high | Output bitrate mode. 'high' requests a higher-quality, larger-file encode from the model; 'standard' uses the default bitrate. |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from cogvideox_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About CogVideoX

CogVideoX is described in *CogVideoX: Text-to-Video Diffusion Models with an Expert Transformer* from Zhipu AI (Z.ai) and Tsinghua University, open-sourced in 2024 with 2B and 5B text-to-video checkpoints and a 5B image-to-video variant, followed by CogVideoX1.5 later that year.

The architecture has three notable parts: a 3D causal VAE that compresses video in both space and time so the transformer works on a compact latent; an *expert transformer* that fuses T5 text embeddings and video latents with expert adaptive LayerNorm instead of cross-attention; and 3D full attention across frames, which is what gives the clips coherent motion rather than flicker. The models are trained with progressive resolution and length schedules on captioned video data.

Typical outputs: the original 2B/5B checkpoints produce 49 frames at 720×480 and 8 fps (about 6 seconds); CogVideoX1.5-5B extends this to roughly 10 seconds at up to 1360×768 and 16 fps. Limits: fixed clip lengths, English prompts through T5, no audio, and generation times of minutes per clip on consumer hardware.

The hosted endpoints used by this client are different models that provide the same capability. `tongyi/wan2.2` (Wan 2.2 14B from Alibaba's Tongyi lab) is the default and generates a 5-second 480p clip from a start image and a prompt; `bytedance/seedance-2.5` generates single-shot text-to-video of 4 to 30 seconds at up to 1080p with synchronised audio. The original CogVideoX weights are available at https://github.com/zai-org/CogVideo if you want to self-host.

**Official project:** https://github.com/zai-org/CogVideo

## Use cases

- **Animate product photos** — call `run({"prompt": "slow orbit, studio lighting", "input_image": url})` on a packshot to get a 5-second hero clip.
- **Social video from stills** — turn a campaign image into a vertical clip by setting `aspect_ratio` for portrait output.
- **Storyboard previsualisation** — generate one clip per storyboard frame with `wait=False` and assemble the results when the webhook fires.
- **Text-to-video with sound** — switch to `model="bytedance/seedance-2.5"` and request a 20-second clip with `generate_audio=True` for ambient sound and speech.
- **Concept testing** — batch 50 prompt variants overnight at a fixed `seed` and compare outputs before committing to a shoot.
- **Research baselines** — script hundreds of image-to-video runs from a dataset and score the outputs without provisioning a GPU cluster.

## FAQ

**Is there a CogVideoX API?**

Not from the original authors; CogVideoX is released as open weights. This client exposes the same image-to-video and text-to-video capability through hosted endpoints (`tongyi/wan2.2` and `bytedance/seedance-2.5`) that you call over HTTPS.

**How much does the CogVideoX API cost?**

The default `tongyi/wan2.2` image-to-video model is $0.20 per run (a 5-second 480p clip). `bytedance/seedance-2.5` text-to-video is $0.473 per run for clips of 4 to 30 seconds, with or without audio. Billing is per prediction.

**Can I run CogVideoX without a GPU?**

With this client, yes: generation happens on the hosted service and your code only makes HTTP requests. Self-hosting CogVideoX-5B needs a CUDA GPU with a large amount of memory, or CPU offload at a heavy speed cost.

**Does this client work with the original CogVideo repo, diffusers or ComfyUI?**

No. It does not load the zai-org/CogVideo checkpoints, and it is not a diffusers pipeline or a ComfyUI node. It is a network client for hosted endpoints. If you need the exact CogVideoX weights, run the official repository locally.

**What input formats does it accept?**

For `tongyi/wan2.2`: `prompt` (text) and `input_image` (a publicly reachable image URL), with optional `aspect_ratio`, `seed` and `num_frames`. For `bytedance/seedance-2.5`: `prompt` only, with optional `resolution` (480p/720p/1080p), `duration` (4–30 seconds or `auto`), `aspect_ratio`, `generate_audio` and `bitrate_mode`. The output is a video URL.

**Is this the official CogVideoX SDK?**

No. This is an independent, community-maintained client and is not affiliated with Zhipu AI or the CogVideo authors. The official project lives at https://github.com/zai-org/CogVideo.

## Related

- [CogVideo / CogVideoX (official repository)](https://github.com/zai-org/CogVideo) — paper, weights and inference code.
- [Synexa Python client](https://github.com/synexa-ai/synexa-python) — the general-purpose client this package wraps.
- [tongyi/wan2.2](https://synexa.ai/explore/tongyi/wan2.2) — the default hosted image-to-video model (Wan 2.2 14B, 5 s at 480p).
- [bytedance/seedance-2.5](https://synexa.ai/explore/bytedance/seedance-2.5) — hosted text-to-video with synchronised audio, up to 30 s.

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of CogVideoX. Model weights and trademarks belong to their respective owners.

_Last reviewed: 2026-09-22_
