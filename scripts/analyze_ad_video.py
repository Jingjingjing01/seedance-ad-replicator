#!/usr/bin/env python3
"""Analyze an ad video and generate sub-15s Seedance replication prompts.

Supported provider modes:
- gemini: upload a local video file to Gemini Files API, then analyze it.
- openai-compatible / openai / ark: call an OpenAI-compatible chat/completions
  endpoint. These modes can use either:
  1) --video-url, if the provider supports video_url input; or
  2) local frame sampling with ffmpeg, if the provider supports image inputs.

Security and privacy notes:
- The selected provider may receive your video, video URL, extracted frames, and
  optional context. Read the provider's data policy before analyzing confidential
  or third-party videos.
- Provide API keys through environment variables. Do not put secrets in code,
  README files, shell history, or git commits.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PROMPT = """你是一名广告视频拉片与 Seedance 2.0 爆款复刻提示词专家。请仔细分析上传的视频，把它转化为可复刻的广告视频生成方案。

目标：
1. 理解全片广告策略：产品/品类、目标受众、Hook、卖点演绎、节奏、镜头、音频、字幕/CTA。
2. 按自然广告节奏分段，每段必须小于15秒；不要在关键动作、台词、转场中间切断。
3. 为每个分段生成一个 Seedance 2.0 复刻 Prompt。每个 Prompt 必须小于2000个中文字。
4. 复刻的是广告结构、节奏、运镜、画面组织、音频设计和卖点表达方式；不要要求复刻原品牌Logo、包装、人物身份或受版权保护的具体资产，除非它们是用户自己的素材。

输出格式必须为 Markdown：

## 爆款广告复刻分析

### 全片策略
- 广告类型：品牌TVC / 效果广告 / 种草 / 口播带货 / UGC / 剧情植入 / 出海广告 / 其他
- 产品/品类：
- 目标受众：
- 核心卖点：
- 结构节奏：Hook -> 痛点/场景 -> 产品/方案 -> 证明 -> CTA/记忆点
- 画面整体风格：
- 音频整体风格：
- 可复刻资产：运镜、节奏、构图、表演、音频、字幕/屏幕文字、CTA等
- 需要替换资产：产品、品牌、人物、场景、台词、Logo等

### 分段总览
| 段落 | 时间 | 时长 | 广告功能 | 复刻重点 |
| --- | --- | ---: | --- | --- |

### 段落 1｜0.0-xx.xs
#### 拉片笔记
| 镜号 | 时间 | 景别/角度 | 运镜 | 画面内容 | 音频/文字 | 广告功能 |
| --- | --- | --- | --- | --- | --- | --- |

#### Seedance 复刻 Prompt（不得超过2000字）
使用以下结构输出一个完整可复制的提示词：
【全局设定】...
【素材参考】@视频1为源广告，仅参考本段运镜、剪辑节奏、镜头结构和表演节奏，不参考原品牌Logo/包装/人物身份；@图片1作为新产品外观、包装、Logo参考；如需要人物/场景/音频参考，请写明@图片2/@图片3/@音频1的职责。
【镜头1｜0-Xs】景别/机位/运镜、主体动作、场景光影、广告功能、音频/文字。
【镜头2｜...】...
【声音设计】...
【后期约束】新产品外观和Logo稳定清晰；不出现源广告品牌信息；无多余字幕、水印、乱码；人物不变脸、不多人同脸；动作自然，画面不跳闪。

#### 替换建议
- @图片1：
- @图片2：
- @音频1：

### 段落 2｜...
[重复同样结构]

硬性要求：
- 每段时长必须小于15秒。如果原视频某段超过15秒，请继续拆分。
- 每段 Seedance 复刻 Prompt 必须小于2000个中文字。
- 每段 Prompt 必须能独立用于生成该段视频。
- 不要添加4K、60fps、HDR、权重标注。
- 不要主动新增字幕、Slogan、价格或CTA；只有源视频里有或确实是该段广告功能时，才描述其位置/时机，并建议替换成用户自己的文案。
- 明确写出“参考源视频什么”和“不参考源视频什么”。
- 音频、台词、音效、字幕要分配到具体镜头。
- 景别/角度：全景/中景/近景/特写 + 平视/俯视/仰视/低角度等。
- 运镜：固定/慢推/拉远/横摇/竖摇/跟拍/手持轻微抖动/环绕/微距等，单镜头不要堆砌过多运镜。
"""

PROVIDER_PRESETS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4.1-mini",
    },
    "ark": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "api_key_env": "ARK_API_KEY",
        "model_env": "ARK_MODEL",
        "default_model": "",
    },
    "openai-compatible": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "LLM_API_KEY",
        "model_env": "LLM_MODEL",
        "default_model": "",
    },
}


def guess_mime_type(video_path: Path) -> str:
    suffix = video_path.suffix.lower()
    if suffix == ".mov":
        return "video/quicktime"
    if suffix == ".avi":
        return "video/x-msvideo"
    if suffix == ".webm":
        return "video/webm"
    if suffix == ".mkv":
        return "video/x-matroska"
    return "video/mp4"


def require_local_file(video_path: str) -> Path:
    path = Path(video_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"视频文件不存在: {path}")
    if not path.is_file():
        raise ValueError(f"路径不是文件: {path}")
    return path


def analyze_video_gemini(video_path: str, api_key: str, model: str, poll_interval: float, timeout: float) -> str:
    try:
        from google import genai
    except ImportError as exc:
        raise ImportError("缺少 google-genai，请运行：python -m pip install google-genai") from exc

    path = require_local_file(video_path)
    client = genai.Client(api_key=api_key)
    mime_type = guess_mime_type(path)

    print(f"正在上传视频到 Gemini: {path}", file=sys.stderr)
    video_file = client.files.upload(file=str(path), config={"mime_type": mime_type})

    print("上传完成，等待处理...", file=sys.stderr)
    start_time = time.monotonic()
    while video_file.state != "ACTIVE":
        if video_file.state == "FAILED":
            raise RuntimeError("视频文件处理失败")
        if time.monotonic() - start_time > timeout:
            raise TimeoutError(f"视频处理超时：超过 {timeout:.0f} 秒仍未完成")
        time.sleep(poll_interval)
        video_file = client.files.get(name=video_file.name)
        print(f"文件状态: {video_file.state}", file=sys.stderr)

    print("处理完成，正在分析...", file=sys.stderr)
    response = client.models.generate_content(
        model=model,
        contents=[PROMPT, video_file],
    )
    return response.text or ""


def run_command(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def get_video_duration(video_path: Path) -> float | None:
    try:
        out = run_command([
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ])
        return float(out)
    except Exception:
        return None


def extract_frames(video_path: str, max_frames: int, width: int, tmp_dir: Path) -> list[Path]:
    path = require_local_file(video_path)
    duration = get_video_duration(path)
    interval = max((duration or max_frames) / max_frames, 1.0)
    output_pattern = tmp_dir / "frame_%04d.jpg"
    vf = f"fps=1/{interval:.3f},scale='min({width},iw)':-1"
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(path),
        "-vf",
        vf,
        "-q:v",
        "3",
        str(output_pattern),
    ]
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError("未找到 ffmpeg。使用非 Gemini 的本地抽帧模式时，请先安装 ffmpeg。") from exc

    frames = sorted(tmp_dir.glob("frame_*.jpg"))[:max_frames]
    if not frames:
        raise RuntimeError("抽帧失败：没有生成任何图片帧。")
    return frames


def image_to_data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def build_openai_content(
    *,
    video_url: str | None,
    frame_paths: list[Path],
    context: str,
    frame_mode: bool,
) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    extra_context = f"\n\n用户补充背景：\n{context.strip()}" if context.strip() else ""

    if video_url:
        parts.append({
            "type": "text",
            "text": PROMPT + extra_context + "\n\n下面提供的是源广告视频 URL。请直接进行视频理解分析。",
        })
        parts.append({"type": "video_url", "video_url": {"url": video_url}})
        return parts

    if frame_mode:
        parts.append({
            "type": "text",
            "text": PROMPT
            + extra_context
            + "\n\n注意：下面提供的是从源广告视频按时间顺序抽取的关键帧，不包含完整音频。请基于视觉帧进行广告结构推断；如果无法判断口播、BGM、字幕或精确转场，请在结果中说明需要用户补充音频转写或原视频。",
        })
        for index, frame_path in enumerate(frame_paths, start=1):
            parts.append({"type": "text", "text": f"关键帧 {index}，按时间顺序排列。"})
            parts.append({"type": "image_url", "image_url": {"url": image_to_data_url(frame_path)}})
        return parts

    raise ValueError("openai-compatible 模式需要 --video-url，或提供本地 video_path 进行抽帧。")


def post_chat_completions(base_url: str, api_key: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI-compatible API 请求失败，HTTP {exc.code}: {body}") from exc


def extract_chat_text(response: dict[str, Any]) -> str:
    try:
        message = response["choices"][0]["message"]
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    texts.append(item.get("text", ""))
            return "\n".join(texts)
    except Exception:
        pass
    return json.dumps(response, ensure_ascii=False, indent=2)


def analyze_video_openai_compatible(
    *,
    provider: str,
    video_path: str | None,
    video_url: str | None,
    api_key: str,
    base_url: str,
    model: str,
    max_frames: int,
    frame_width: int,
    context: str,
    timeout: float,
) -> str:
    if not model:
        raise ValueError(f"{provider} 模式需要设置模型名，例如 --model 或对应环境变量。")

    frame_paths: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="seedance_ad_frames_") as tmp:
        if not video_url:
            if not video_path:
                raise ValueError("请提供本地 video_path 或 --video-url。")
            print(f"正在从本地视频抽取关键帧: {video_path}", file=sys.stderr)
            frame_paths = extract_frames(video_path, max_frames=max_frames, width=frame_width, tmp_dir=Path(tmp))
            print(f"已抽取 {len(frame_paths)} 张关键帧，正在调用 {provider} 模型分析...", file=sys.stderr)
        else:
            print(f"正在使用 video_url 调用 {provider} 模型分析...", file=sys.stderr)

        content = build_openai_content(
            video_url=video_url,
            frame_paths=frame_paths,
            context=context,
            frame_mode=not bool(video_url),
        )
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "temperature": 0,
            "max_tokens": 4096,
        }
        response = post_chat_completions(base_url, api_key, payload, timeout=timeout)
        return extract_chat_text(response)


def read_context(context: str | None, context_file: str | None) -> str:
    values = []
    if context:
        values.append(context)
    if context_file:
        values.append(Path(context_file).expanduser().read_text(encoding="utf-8"))
    return "\n".join(values)


def resolve_openai_provider_config(args: argparse.Namespace) -> tuple[str, str, str]:
    preset = PROVIDER_PRESETS[args.provider]
    base_url = args.base_url or os.getenv("LLM_BASE_URL") or preset["base_url"]
    api_key_env = args.api_key_env or preset["api_key_env"]
    model_env = preset["model_env"]
    api_key = os.getenv(api_key_env)
    model = args.model or os.getenv(model_env) or preset["default_model"]
    if not api_key:
        raise ValueError(f"请设置 {api_key_env} 环境变量，或用 --api-key-env 指定已存在的密钥环境变量。")
    return base_url, api_key, model


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an ad video and generate Seedance remake prompts.")
    parser.add_argument("video_path", nargs="?", help="Local ad video path. Required for gemini and frame-sampling modes.")
    parser.add_argument(
        "--provider",
        choices=["gemini", "openai", "ark", "openai-compatible"],
        default=os.getenv("VIDEO_ANALYSIS_PROVIDER", "gemini"),
        help="Model provider mode. Default: gemini",
    )
    parser.add_argument("--model", default=None, help="Model name or endpoint id. Overrides provider-specific model env vars.")
    parser.add_argument("--base-url", default=None, help="OpenAI-compatible base URL, e.g. https://api.openai.com/v1")
    parser.add_argument("--api-key-env", default=None, help="Environment variable that stores the OpenAI-compatible API key")
    parser.add_argument("--video-url", default=None, help="HTTPS video URL for providers that support video_url input")
    parser.add_argument("--max-frames", type=int, default=12, help="Max frames to sample for non-Gemini local analysis")
    parser.add_argument("--frame-width", type=int, default=768, help="Sampled frame width for non-Gemini local analysis")
    parser.add_argument("--context", default="", help="Optional extra context, e.g. target product, platform, subtitle policy")
    parser.add_argument("--context-file", default=None, help="Optional text file with extra context")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Gemini polling interval in seconds")
    parser.add_argument("--timeout", type=float, default=600.0, help="Provider request / processing timeout in seconds")
    args = parser.parse_args()

    try:
        context = read_context(args.context, args.context_file)
        if args.provider == "gemini":
            if not args.video_path:
                raise ValueError("gemini 模式需要提供本地 video_path。")
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("请设置 GEMINI_API_KEY 环境变量。示例: export GEMINI_API_KEY='your_api_key'")
            model = args.model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            print(analyze_video_gemini(args.video_path, api_key, model, args.poll_interval, args.timeout))
            return

        base_url, api_key, model = resolve_openai_provider_config(args)
        print(analyze_video_openai_compatible(
            provider=args.provider,
            video_path=args.video_path,
            video_url=args.video_url,
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_frames=args.max_frames,
            frame_width=args.frame_width,
            context=context,
            timeout=args.timeout,
        ))
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
