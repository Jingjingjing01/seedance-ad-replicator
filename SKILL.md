---
name: seedance-ad-replicator
description: Analyze an advertising video, split it into natural sub-15-second segments, and generate Seedance 2.0 remake prompts for each segment so the user can replicate a proven ad structure, pacing, camera language, audio design, and selling-point flow. Use when the user provides a local ad video and asks for viral ad replication, video-to-prompt reverse engineering, ad remake prompts, Seedance prompts by segment, or 爆款广告复刻.
---

# Seedance Ad Replicator

## Purpose

Turn an existing ad video into a Seedance 2.0 replication plan:

1. Understand the full ad: product/category, audience, hook, selling point, scene logic, rhythm, camera language, audio, screen text, and CTA.
2. Split the video into natural segments, each strictly under 15 seconds. Do not cut mid-action, mid-line, or mid-transition unless unavoidable.
3. Generate one Seedance-ready remake prompt per segment, keeping the ad's structure while allowing the user to replace product, actor, scene, or brand assets.

This is advertising-specific. If the source video is not clearly an ad, still reverse-engineer it, but state which commercial elements are missing.

## Inputs

The user should provide a local video path. Optional context improves output:

- Target product or brand to replace into the remake.
- Available assets, such as `@图片1` product image, `@图片2` actor, `@视频1` source ad, `@音频1` voice/BGM.
- Target platform, aspect ratio, language, subtitle policy, and CTA policy.

If optional context is missing, generate prompts that explicitly say which references should be supplied, such as `@图片1作为新产品外观参考`.

## Tool Workflow

Prefer using `scripts/analyze_ad_video.py` when a video path is available:

```bash
python scripts/analyze_ad_video.py "<video_path>"
```

Set `GEMINI_API_KEY` in the environment:

```bash
export GEMINI_API_KEY="your_api_key_here"
python scripts/analyze_ad_video.py "<video_path>"
```

The script uploads the video to Gemini and returns Markdown. Videos may be sent to Google for processing. Avoid passing API keys as command-line arguments because they may appear in shell history or process listings. If the API key or dependency is missing, explain the requirement and provide a manual analysis template.

Dependency for video analysis:

```bash
python -m pip install google-genai
```

Use `scripts/split_video_segments.py` only when the user asks for physical video clips. It requires `ffmpeg`:

```bash
python scripts/split_video_segments.py "<video_path>" --segments "0-12.5,12.5-25.0" --out-dir ./segments
```

## Output Format

Use Chinese by default.

```text
## 爆款广告复刻分析

### 全片策略
- 广告类型：...
- 产品/品类：...
- 目标受众：...
- 核心卖点：...
- 结构节奏：Hook -> 痛点/场景 -> 产品/方案 -> 证明 -> CTA/记忆点
- 可复刻资产：运镜、节奏、构图、表演、音频、字幕/屏幕文字、CTA
- 需要替换资产：产品、品牌、人物、场景、台词、Logo 等

### 分段总览
| 段落 | 时间 | 时长 | 功能 | 复刻重点 |
| --- | --- | ---: | --- | --- |

### 段落 1｜0.0-xx.xs
#### 拉片笔记
| 镜号 | 时间 | 景别/角度 | 运镜 | 画面内容 | 音频/文字 | 广告功能 |

#### Seedance 复刻 Prompt（不得超过2000字）
...

#### 替换建议
- @图片1：...
- @图片2：...
- @音频1：...

### 段落 2｜...
...
```

Each segment prompt must be under 2000 Chinese characters. The analysis and tables are not included in this limit.

## Segmentation Rules

- Each segment must be less than 15 seconds. Prefer 8-14.5 seconds for complex ads.
- Split on natural ad beats: hook, product reveal, benefit demonstration, social proof, price/offer, CTA, scene change, music phrase, or transition.
- Keep spoken lines intact. If a line crosses 15 seconds, split at a sentence boundary and note the audio continuation.
- Keep a segment self-contained enough to generate independently in Seedance.
- For source videos longer than 15 seconds, preserve continuity by making the end state of one segment the start reference for the next.

## Prompt Generation Rules

Each Seedance remake prompt should contain:

- `【全局设定】`: ad type, segment duration, aspect ratio if known, target mood, commercial objective.
- `【素材参考】`: define `@图片/@视频/@音频` duties clearly. For replication, specify what to copy from the source and what to replace.
- `【镜头N｜X-Ys】`: shot timing, scene size, camera movement, subject action, selling-point beat, audio/screen text when needed.
- `【声音设计】`: BGM, SFX, voice, subtitle policy, lip sync when relevant.
- `【后期约束】`: no unwanted text/subtitles/watermarks, stable product/logo/identity, no duplicated faces, no deformation, no jump flicker.

Do not add `4K`, `60fps`, `HDR`, or weight tags such as `{1.2}` by default. Do not add screen text, subtitles, slogan, price, or CTA unless they appear in the source ad or the user asks for them.

## Replication Ethics and Practicality

Frame output as structure replication, not exact infringement. Preserve useful mechanics: pacing, shot type, offer flow, proof style, and emotional turn. Replace protected brand assets, logos, characters, and exact copy unless the user has rights or explicitly asks to keep their own source material.

When describing source video references, use language like:

- `参考源视频的快节奏运镜和痛点到产品的结构，不复刻原品牌Logo和包装。`
- `仅参考人物手势节奏和镜头切换，不参考原人物身份。`
- `将源视频中的旧产品替换为@图片1中的新产品，保持位置、动作、透视、光影和节奏一致。`

## Quality Gates

Before finalizing, check:

- Every segment is under 15 seconds.
- Every segment has a Seedance prompt under 2000 Chinese characters.
- Prompts define all multimodal references before use.
- Prompts distinguish copied elements from replaced elements.
- Audio, dialogue, subtitles, and CTA are assigned to specific shots.
- The first segment preserves the ad hook.
- Product/brand stability constraints are present.

Read `references/seedance-ad-replication-guide.md` when you need compact camera, multimodal, or failure-fix phrasing.
