# Seedance Ad Replicator

`seedance-ad-replicator` is a Claude/OpenAI-style skill for turning an existing advertising video into a Seedance 2.0 remake plan. It analyzes the ad's strategy, pacing, camera language, audio design, screen text, and selling-point flow, then splits the video into natural sub-15-second segments and writes one Seedance-ready remake prompt for each segment.

The goal is **structure replication, not asset copying**: learn the mechanics of a proven ad while replacing protected brand assets, logos, packaging, characters, and exact copy unless you own or are licensed to use them.

## What This Skill Does

- Reverse-engineers an ad video into a structured ad strategy.
- Splits longer ads into natural segments under 15 seconds.
- Generates compact Seedance 2.0 remake prompts per segment.
- Defines what to copy from the source video and what to replace.
- Adds prompt constraints for product/logo stability, character consistency, no unwanted subtitles, no watermark, no flicker, and no source-brand leakage.
- Provides optional helper scripts for video analysis and physical video splitting.

## When to Use It

Use this skill when you want to:

- Recreate the structure of a viral ad in Seedance.
- Convert an ad video into prompts.
- Study a product ad's hook, pacing, scene logic, and CTA flow.
- Replace a source product with your own product assets.
- Generate sub-15-second Seedance prompts for a longer ad.
- Create ad variants for e-commerce, social ads, UGC/KOC videos, live-commerce clips, brand films, or performance ads.

## Repository Structure

```text
seedance-ad-replicator/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   └── seedance-ad-replication-guide.md
└── scripts/
    ├── analyze_ad_video.py
    └── split_video_segments.py
```

## Quick Start

### 1. Install Dependencies

For video analysis with Gemini:

```bash
python -m pip install google-genai
```

For physical video splitting:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### 2. Set Your API Key

The analysis script uploads the video to Google Gemini. Set your API key as an environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Do **not** commit API keys to this repository. Avoid passing secrets as command-line arguments because they may be saved in shell history or process listings.

### 3. Analyze an Ad Video

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4"
```

Optional model override:

```bash
GEMINI_MODEL="gemini-2.5-flash" python scripts/analyze_ad_video.py "/path/to/ad-video.mp4"
```

The output is Markdown containing:

- Full-ad strategy
- Segment overview
- Shot-by-shot notes
- One Seedance remake prompt per segment
- Asset replacement suggestions

### 4. Split the Video into Physical Clips

Only use this when you need actual video files for each segment:

```bash
python scripts/split_video_segments.py "/path/to/ad-video.mp4" \
  --segments "0-12.5,12.5-24.0" \
  --out-dir ./segments
```

For frame-accurate cuts, add `--reencode`:

```bash
python scripts/split_video_segments.py "/path/to/ad-video.mp4" \
  --segments "0-12.5,12.5-24.0" \
  --out-dir ./segments \
  --reencode
```

Each segment must be **less than 15 seconds**.

## Example Prompt to Use With the Skill

```text
Use seedance-ad-replicator to analyze this ad video and generate sub-15-second Seedance remake prompts.

Video path: /Users/me/Desktop/source-ad.mp4
Target product: @图片1中的蓝色精华露
Target actor: @图片2中的男性模特
Platform: vertical short-form video
Language: Chinese
Subtitle policy: do not add new subtitles unless the source segment already has screen text
CTA policy: preserve CTA position only; replace copy with my own approved text later
```

## Example Output Shape

```text
## 爆款广告复刻分析

### 全片策略
- 广告类型：效果广告 / 种草 / UGC / 品牌TVC / ...
- 产品/品类：...
- 目标受众：...
- 核心卖点：...
- 结构节奏：Hook -> 痛点/场景 -> 产品/方案 -> 证明 -> CTA/记忆点
- 可复刻资产：运镜、节奏、构图、表演、音频、字幕/屏幕文字、CTA
- 需要替换资产：产品、品牌、人物、场景、台词、Logo 等

### 分段总览
| 段落 | 时间 | 时长 | 功能 | 复刻重点 |
| --- | --- | ---: | --- | --- |

### 段落 1｜0.0-12.5s
#### 拉片笔记
| 镜号 | 时间 | 景别/角度 | 运镜 | 画面内容 | 音频/文字 | 广告功能 |

#### Seedance 复刻 Prompt（不得超过2000字）
【全局设定】...
【素材参考】...
【镜头1｜0-3s】...
【声音设计】...
【后期约束】...

#### 替换建议
- @图片1：新产品包装、Logo、瓶身颜色参考
- @图片2：新人物身份和外观参考
- @音频1：BGM/口播音色参考
```

## Prompt Rules

Each generated Seedance remake prompt should include:

- `【全局设定】`: ad type, duration, aspect ratio if known, mood, commercial objective.
- `【素材参考】`: define each `@图片`, `@视频`, and `@音频` before using it.
- `【镜头N｜X-Ys】`: timing, shot size, camera movement, subject action, selling-point beat, audio/screen text if relevant.
- `【声音设计】`: BGM, SFX, voice, subtitle policy, lip sync when relevant.
- `【后期约束】`: product/logo/identity stability, no unwanted text, no watermark, no duplicated faces, no deformation, no flicker.

The skill intentionally avoids adding `4K`, `60fps`, `HDR`, weight tags, new slogans, prices, or CTA copy by default.

## Privacy and Security Notes

- `scripts/analyze_ad_video.py` uploads the provided video to Gemini for processing. Do not analyze confidential or third-party videos unless you have permission and accept the provider's data policy.
- API keys are read from `GEMINI_API_KEY`. Do not store keys in this repo.
- `scripts/split_video_segments.py` invokes `ffmpeg` via `subprocess.run` with an argument list, not `shell=True`.
- The scripts do not intentionally collect, store, or transmit data except for the explicit Gemini upload in the analysis script.

## Ethics and Rights

This project is intended for lawful ad-structure analysis and creative adaptation. It should not be used to copy protected brand assets, logos, packaging, characters, music, exact scripts, or other copyrighted/trademarked materials without authorization.

Recommended phrasing inside remake prompts:

```text
参考源视频的快节奏运镜和痛点到产品的结构，不复刻原品牌Logo和包装。
```

```text
仅参考人物手势节奏和镜头切换，不参考原人物身份。
```

```text
将源视频中的旧产品替换为@图片1中的新产品，保持位置、动作、透视、光影和节奏一致。
```

## Limitations

- Video understanding quality depends on the model used.
- The included analysis script currently uses Gemini. Other providers can be added by implementing a separate provider script or an extraction workflow such as `video -> frames -> ASR/OCR -> vision model -> prompt generation`.
- Generated segment boundaries should be reviewed before production.
- Product claims and visual proof should be checked for legal/compliance accuracy.

## License

Choose and add a license before publishing. If you want broad open-source reuse, MIT is a common option.
