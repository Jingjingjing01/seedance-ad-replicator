# 给 AI Agent 的部署说明：Seedance Ad Replicator

这份文档是专门写给 AI Agent / 低代码平台 / 自动部署助手看的。目标是让不会代码的用户可以直接把本 GitHub 项目链接交给 Agent，然后让 Agent 帮忙完成安装、配置、运行和二次开发。

项目地址：

```text
https://github.com/Jingjingjing01/seedance-ad-replicator
```

---

## 你是 Agent 时，需要完成什么？

用户可能会对你说：

```text
请帮我部署这个 GitHub 项目：
https://github.com/Jingjingjing01/seedance-ad-replicator
```

你需要帮助用户完成：

1. 克隆仓库；
2. 创建 Python 环境；
3. 安装依赖；
4. 配置模型 API Key；
5. 根据用户选择的模型提供运行命令；
6. 测试脚本是否可用；
7. 告诉用户如何上传/指定广告视频；
8. 输出 Seedance 复刻 Prompt；
9. 如用户需要，帮他切分视频片段。

---

## 项目功能概述

这个项目用于：

```text
广告视频
-> 广告策略分析
-> 小于15秒自然分段
-> 拉片笔记
-> 每段 Seedance 2.0 复刻 Prompt
```

核心脚本：

```text
scripts/analyze_ad_video.py
```

辅助切片脚本：

```text
scripts/split_video_segments.py
```

---

## 最小部署步骤

### 1. 克隆项目

```bash
git clone https://github.com/Jingjingjing01/seedance-ad-replicator.git
cd seedance-ad-replicator
```

### 2. 创建虚拟环境

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果用户需要使用非 Gemini 的本地抽帧模式，还要安装 `ffmpeg`。

macOS：

```bash
brew install ffmpeg
```

Ubuntu / Debian：

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

---

## 支持的模型模式

当前 `scripts/analyze_ad_video.py` 支持四种 provider：

| provider | 用途 | 输入方式 | 需要的环境变量 |
| --- | --- | --- | --- |
| `gemini` | 默认模式，直接上传本地视频给 Gemini 分析 | 本地视频文件 | `GEMINI_API_KEY`，可选 `GEMINI_MODEL` |
| `openai` | OpenAI 官方接口或兼容视觉模型 | `--video-url` 或本地抽帧 | `OPENAI_API_KEY`，可选 `OPENAI_MODEL` |
| `ark` | 火山方舟 / 豆包 OpenAI-compatible 接口 | `--video-url` 或本地抽帧 | `ARK_API_KEY`，`ARK_MODEL` |
| `openai-compatible` | 任意 OpenAI-compatible 接口 | `--video-url` 或本地抽帧 | 默认 `LLM_API_KEY`，`LLM_MODEL`，也可自定义 |

注意：

- `gemini` 模式会把本地视频上传到 Gemini。
- 非 Gemini 模式有两种用法：
  - 如果模型支持 `video_url`，可以传 `--video-url`；
  - 如果模型不支持直接视频输入，可以让脚本用 ffmpeg 从本地视频抽帧，再把关键帧发给视觉模型分析。
- 抽帧模式只包含视觉关键帧，不包含完整音频。如果广告强依赖口播或音乐，建议用户额外提供音频转写，放在 `--context` 或 `--context-file` 中。

---

## 运行方式一：Gemini 默认模式

适合：用户有 Gemini API Key，希望直接上传本地视频分析。

配置：

```bash
export GEMINI_API_KEY="用户的 Gemini API Key"
export GEMINI_MODEL="gemini-2.5-flash"
```

运行：

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4"
```

---

## 运行方式二：OpenAI 官方或兼容模型，本地抽帧分析

适合：模型支持图片输入，但不一定支持直接视频输入。

配置：

```bash
export OPENAI_API_KEY="用户的 OpenAI API Key"
export OPENAI_MODEL="gpt-4.1-mini"
```

运行：

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" \
  --provider openai \
  --max-frames 12 \
  --frame-width 768
```

如果用户的视频比较长，可以增加关键帧数量：

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" \
  --provider openai \
  --max-frames 20
```

注意：关键帧越多，消耗 token / 图片额度越多。

---

## 运行方式三：OpenAI 官方或兼容模型，video_url 直接视频理解

适合：用户使用的模型和 API 确认支持 `video_url` 输入。

```bash
python scripts/analyze_ad_video.py \
  --provider openai \
  --video-url "https://example.com/ad-video.mp4"
```

如果接口不支持 `video_url`，通常会返回类似：

```text
unsupported content type: video_url
```

这时应改用本地抽帧模式。

---

## 运行方式四：火山方舟 / 豆包 / Ark

适合：用户希望接入火山方舟 OpenAI-compatible 接口。

配置：

```bash
export ARK_API_KEY="用户的火山方舟 API Key"
export ARK_MODEL="用户的模型名或 endpoint id"
```

本地抽帧模式：

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" \
  --provider ark \
  --max-frames 12
```

如果用户确认该模型支持 `video_url`，可以尝试：

```bash
python scripts/analyze_ad_video.py \
  --provider ark \
  --video-url "https://example.com/ad-video.mp4"
```

如果返回不支持 `video_url`，改用本地抽帧模式。

---

## 运行方式五：任意 OpenAI-compatible 服务

适合：用户使用 OpenRouter、国产大模型网关、自建代理、本地服务等。

配置：

```bash
export LLM_API_KEY="用户的 API Key"
export LLM_MODEL="模型名"
```

运行：

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" \
  --provider openai-compatible \
  --base-url "https://your-provider.example.com/v1"
```

如果用户希望使用不同的密钥环境变量，例如 `MY_API_KEY`：

```bash
export MY_API_KEY="用户的 API Key"

python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" \
  --provider openai-compatible \
  --base-url "https://your-provider.example.com/v1" \
  --api-key-env MY_API_KEY \
  --model "your-model-name"
```

---

## 如何把用户补充信息传给模型？

用户可能会提供目标产品、目标平台、字幕策略、CTA 策略等信息。请用 `--context` 传入：

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" \
  --provider openai \
  --context "目标产品：@图片1中的蓝色精华露；目标平台：抖音竖版；不要新增价格和CTA。"
```

如果上下文较长，写入一个文本文件：

```bash
cat > context.txt <<'EOF'
目标产品：@图片1中的蓝色精华露
目标人物：@图片2中的男性模特
目标平台：抖音竖版
字幕策略：不新增字幕，除非源视频里已有屏幕文字
CTA策略：保留CTA位置，文案后期替换
EOF

python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" \
  --provider openai \
  --context-file context.txt
```

---

## 如何切分视频？

当用户需要实际导出视频片段时，使用：

```bash
python scripts/split_video_segments.py "/path/to/ad-video.mp4" \
  --segments "0-12.5,12.5-24.0" \
  --out-dir ./segments
```

如果需要更准确的切点：

```bash
python scripts/split_video_segments.py "/path/to/ad-video.mp4" \
  --segments "0-12.5,12.5-24.0" \
  --out-dir ./segments \
  --reencode
```

每段必须小于 15 秒。

---

## 给不会代码用户的推荐交互话术

你可以让用户这样提供信息：

```text
请把这个广告视频拆解成 Seedance 复刻 Prompt。

视频路径：xxx
目标产品：xxx
目标平台：xxx
是否需要字幕：xxx
是否需要CTA：xxx
我使用的模型：Gemini / OpenAI / 火山方舟 / 其他
我的 API Key 已经配置在环境变量：xxx
```

如果用户没有配置 API Key，请指导用户只设置环境变量，不要把 Key 发到公开聊天、README 或 GitHub。

---

## 故障排查

### 1. 报错：没有 API Key

检查用户是否设置了对应 provider 的环境变量：

```bash
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY
echo $ARK_API_KEY
echo $LLM_API_KEY
```

不要在公开日志中打印完整 Key。

---

### 2. 报错：找不到 ffmpeg

说明用户在非 Gemini 本地抽帧模式下没有安装 ffmpeg。安装后重试。

---

### 3. 报错：unsupported content type: video_url

说明当前模型/API 不支持直接传视频 URL。改成本地抽帧模式：

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" --provider openai
```

或：

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" --provider ark
```

---

### 4. 结果里音频分析不准

如果使用抽帧模式，模型只能看到关键帧，看不到完整口播和音乐。请让用户提供音频转写，例如：

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" \
  --provider openai \
  --context "音频转写：这里填口播内容。BGM：轻快电子音乐。"
```

---

### 5. 分段超过 15 秒

让模型重新生成，强调：

```text
每段必须严格小于15秒，请重新切分，不要出现大于或等于15秒的段落。
```

---

## 安全要求

Agent 必须遵守：

1. 不要把用户 API Key 写进代码；
2. 不要把 API Key 提交到 Git；
3. 不要在日志里完整打印 API Key；
4. 不要上传未经授权的敏感视频；
5. 告知用户 Gemini / OpenAI-compatible provider 可能会接收视频、视频 URL 或抽帧图片；
6. 不要鼓励复制原品牌 Logo、包装、人物身份、音乐和原广告文案；
7. 如果用户要开源修改后的项目，先检查 `.env`、视频文件、缓存文件和密钥是否被误提交。

---

## Agent 可以做的二次开发

如果用户要求“接入其他模型”，优先使用 `openai-compatible` 模式，而不是重写整个项目。

通用命令模板：

```bash
export LLM_API_KEY="用户的 API Key"
export LLM_MODEL="模型名"

python scripts/analyze_ad_video.py "/path/to/ad-video.mp4" \
  --provider openai-compatible \
  --base-url "https://provider.example.com/v1"
```

如果该 provider 支持 `video_url`：

```bash
python scripts/analyze_ad_video.py \
  --provider openai-compatible \
  --base-url "https://provider.example.com/v1" \
  --video-url "https://example.com/ad.mp4"
```

如果该 provider 不支持视频但支持图片，就使用本地视频路径，让脚本自动抽帧。

---

## 最终交付给用户时应该说明

部署完成后，请告诉用户：

1. 项目安装路径；
2. 当前使用的 provider 和模型；
3. API Key 是通过哪个环境变量读取的；
4. 如何运行视频分析命令；
5. 如何切分视频；
6. 输出结果保存在哪里；
7. 隐私提醒：视频或抽帧可能会发送给模型服务商。
