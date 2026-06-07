#!/usr/bin/env python3
"""Analyze an ad video and generate sub-15s Seedance replication prompts.

Security and privacy notes:
- The video is uploaded to Google Gemini for processing.
- Read the provider's data policy before analyzing confidential videos.
- Provide the API key through the GEMINI_API_KEY environment variable. Avoid
  passing secrets as command-line arguments because they may be stored in shell
  history or visible in process listings.
"""

import argparse
import os
import sys
import time
from pathlib import Path

from google import genai


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


def analyze_video(video_path: str, api_key: str, model: str, poll_interval: float, timeout: float) -> str:
    path = Path(video_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"视频文件不存在: {path}")
    if not path.is_file():
        raise ValueError(f"路径不是文件: {path}")

    client = genai.Client(api_key=api_key)
    mime_type = guess_mime_type(path)

    print(f"正在上传视频: {path}", file=sys.stderr)
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an ad video with Gemini and generate Seedance remake prompts.")
    parser.add_argument("video_path", help="Local ad video path")
    parser.add_argument("--model", default=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), help="Gemini model name")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Polling interval in seconds")
    parser.add_argument("--timeout", type=float, default=600.0, help="Upload processing timeout in seconds")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("错误: 请设置 GEMINI_API_KEY 环境变量。", file=sys.stderr)
        print("示例: export GEMINI_API_KEY='your_api_key'", file=sys.stderr)
        sys.exit(1)

    try:
        print(analyze_video(args.video_path, api_key, args.model, args.poll_interval, args.timeout))
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
