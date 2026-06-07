# Seedance Ad Replicator

`seedance-ad-replicator` 是一个面向 Seedance 2.0 广告视频创作的 Skill，用来把一条已有广告视频拆解成可复刻的广告生成方案。

它会分析源广告的视频结构、节奏、镜头语言、音频设计、屏幕文字、卖点表达和 CTA 流程，然后把视频切分成多个自然的、**小于 15 秒** 的段落，并为每个段落生成一个可直接用于 Seedance 的复刻 Prompt。

这个项目强调的是：

> **复刻广告结构，而不是复制受保护资产。**

也就是说，我们学习的是成熟广告里的 Hook、节奏、构图、转场、卖点演绎和转化逻辑；但原品牌 Logo、包装、人物身份、音乐、原始文案等受版权或商标保护的内容，需要替换成你自己拥有授权的素材。

---

## 这个 Skill 能做什么？

- 把广告视频反向拆解成结构化广告策略。
- 自动规划每个小于 15 秒的自然分段。
- 为每个分段生成 Seedance 2.0 复刻 Prompt。
- 明确区分：源视频中哪些元素可以参考，哪些元素必须替换。
- 帮你保留广告的节奏、镜头、构图、表演节奏、音频设计和卖点表达方式。
- 在 Prompt 中加入产品稳定、Logo 稳定、人物一致性、无乱码字幕、无水印、无源品牌泄露等约束。
- 提供辅助脚本，用于调用 Gemini 分析视频，以及按时间段切分视频文件。

---

## 适合什么场景？

你可以在这些场景使用它：

- 看到一条爆款广告，想学习它的广告结构。
- 想把一个广告视频反推出 Seedance Prompt。
- 想分析一条广告的 Hook、痛点、产品露出、卖点证明和 CTA。
- 想把源广告里的旧产品替换成自己的产品。
- 想把一条较长广告拆成多个 Seedance 可生成片段。
- 想做电商广告、社媒广告、种草视频、UGC/KOC、口播带货、品牌广告、效果广告等素材。

---

## 仓库结构

```text
seedance-ad-replicator/
├── SKILL.md
├── README.md
├── requirements.txt
├── agents/
│   └── openai.yaml
├── references/
│   └── seedance-ad-replication-guide.md
└── scripts/
    ├── analyze_ad_video.py
    └── split_video_segments.py
```

文件说明：

| 文件 | 作用 |
| --- | --- |
| `SKILL.md` | Skill 的核心说明文件，定义使用场景、输出格式、分段规则和复刻规则。 |
| `references/seedance-ad-replication-guide.md` | 辅助参考文档，包含镜头短语、多模态素材规则、常见失败修复等。 |
| `agents/openai.yaml` | Agent/Skill 展示配置。 |
| `scripts/analyze_ad_video.py` | 调用 Gemini 分析广告视频，并输出 Markdown 拉片和复刻 Prompt。 |
| `scripts/split_video_segments.py` | 使用 ffmpeg 按指定时间段切分视频。 |
| `requirements.txt` | Python 依赖。 |

---

## 快速开始

### 1. 安装依赖

如果你要使用视频分析脚本，需要安装：

```bash
python -m pip install -r requirements.txt
```

如果你只想安装核心依赖，也可以：

```bash
python -m pip install google-genai
```

如果你要切分视频文件，需要本地安装 `ffmpeg`。

macOS：

```bash
brew install ffmpeg
```

Ubuntu / Debian：

```bash
sudo apt-get install ffmpeg
```

---

### 2. 设置 Gemini API Key

视频分析脚本目前使用 Gemini。请先设置环境变量：

```bash
export GEMINI_API_KEY="your_api_key_here"
```

不要把 API Key 写进代码、README、`.env` 或提交到 GitHub。  
也不建议通过命令行参数传递 API Key，因为它可能出现在 shell history 或进程列表中。

---

### 3. 分析一条广告视频

```bash
python scripts/analyze_ad_video.py "/path/to/ad-video.mp4"
```

如果你想指定 Gemini 模型，可以这样：

```bash
GEMINI_MODEL="gemini-2.5-flash" python scripts/analyze_ad_video.py "/path/to/ad-video.mp4"
```

脚本会输出 Markdown，内容包括：

- 全片广告策略；
- 分段总览；
- 每段拉片笔记；
- 每段 Seedance 复刻 Prompt；
- 替换素材建议。

注意：这个脚本会把视频上传到 Gemini / Google 进行处理。请不要上传未授权、保密或敏感视频，除非你确认自己有权限，并接受对应服务商的数据处理政策。

---

### 4. 按时间段切分视频

如果你需要把源视频实际切成多个小于 15 秒的视频片段，可以使用：

```bash
python scripts/split_video_segments.py "/path/to/ad-video.mp4" \
  --segments "0-12.5,12.5-24.0" \
  --out-dir ./segments
```

如果你希望切点更准确，可以加 `--reencode`：

```bash
python scripts/split_video_segments.py "/path/to/ad-video.mp4" \
  --segments "0-12.5,12.5-24.0" \
  --out-dir ./segments \
  --reencode
```

每个分段必须 **小于 15 秒**。如果某个区间大于或等于 15 秒，脚本会报错。

---

## 如何在对话中使用这个 Skill？

你可以这样描述任务：

```text
请使用 seedance-ad-replicator 分析这个广告视频，并生成小于15秒的 Seedance 分段复刻 Prompt。

视频路径：/Users/me/Desktop/source-ad.mp4
目标产品：@图片1中的蓝色精华露
目标人物：@图片2中的男性模特
平台：竖版短视频
语言：中文
字幕策略：不主动新增字幕，除非源视频对应段落本来就有屏幕文字
CTA策略：保留CTA出现位置，但具体文案后期替换成我自己的版本
```

如果你没有目标产品或人物素材，也可以只提供视频路径。Skill 会在输出中提示你应该补充哪些素材，例如：

```text
@图片1：建议提供新产品外观、包装、Logo参考。
@图片2：建议提供新人物形象参考。
@音频1：如需复刻口播音色或BGM节奏，可提供音频参考。
```

---

## 输出格式示例

这个 Skill 的典型输出结构如下：

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

---

## Seedance 复刻 Prompt 的生成规则

每段 Seedance 复刻 Prompt 通常包含：

- `【全局设定】`：广告类型、段落时长、画幅、整体调性、商业目标。
- `【素材参考】`：定义 `@图片`、`@视频`、`@音频` 的职责。对于复刻任务，要明确“参考什么”和“不参考什么”。
- `【镜头N｜X-Ys】`：镜头时间、景别、机位、运镜、主体动作、卖点节奏、音频或屏幕文字。
- `【声音设计】`：BGM、音效、口播、字幕策略、口型同步等。
- `【后期约束】`：产品稳定、Logo 稳定、人物一致、无乱码字幕、无水印、无重复人脸、无变形、无跳闪。

默认不会主动添加：

- `4K`
- `60fps`
- `HDR`
- 权重标签
- 新 slogan
- 新价格
- 新 CTA 文案
- 源视频里没有的字幕或屏幕文字

除非用户明确要求，或者源广告对应段落原本就有这些元素。

---

## 推荐的复刻措辞

为了避免不当复制源广告资产，建议在 Prompt 中使用类似措辞：

```text
参考源视频的快节奏运镜和痛点到产品的结构，不复刻原品牌Logo和包装。
```

```text
仅参考人物手势节奏和镜头切换，不参考原人物身份。
```

```text
将源视频中的旧产品替换为@图片1中的新产品，保持位置、动作、透视、光影和节奏一致。
```

```text
@视频1为源广告，仅参考本段镜头结构、剪辑节奏和表演节奏，不参考原品牌、原包装、原人物身份和原始文案。
```

---

## 隐私与安全说明

请特别注意：

- `scripts/analyze_ad_video.py` 会把你提供的视频上传到 Gemini 进行处理。
- 请不要分析没有授权的第三方视频、保密视频、内部素材或敏感内容，除非你确认自己有权限并接受服务商的数据政策。
- API Key 只通过 `GEMINI_API_KEY` 环境变量读取，不应该写进代码或提交到仓库。
- `scripts/split_video_segments.py` 使用 `subprocess.run` 的参数列表调用 `ffmpeg`，没有使用 `shell=True`。
- 本项目脚本不会主动收集或保存用户数据；除 Gemini 分析脚本中的明确视频上传外，没有其他外部传输行为。

---

## 合规与版权提醒

这个项目适用于合法的广告结构分析和创意改编，不应用于未经授权地复制：

- 原品牌 Logo；
- 原产品包装；
- 原人物身份；
- 原广告音乐；
- 原始广告文案；
- 受版权、商标权或肖像权保护的具体素材。

更推荐的做法是：

```text
学习广告方法论，替换成自己的品牌资产。
```

也就是复刻：

- 节奏；
- 镜头结构；
- 卖点表达方式；
- 情绪转折；
- 痛点到产品的叙事逻辑；
- CTA 出现位置。

但替换：

- 品牌；
- 产品；
- 包装；
- 人物；
- 台词；
- Logo；
- 具体商业文案。

---

## 局限性

- 视频理解效果取决于所使用的模型。
- 当前脚本默认使用 Gemini。如果你想使用其他模型，可以扩展为 `视频 -> 抽帧 -> ASR/OCR -> 视觉模型分析 -> Prompt 生成` 的流程。
- 自动生成的分段时间建议上线前人工复核。
- 涉及产品功效、医疗、美妆、食品、金融等敏感品类时，卖点表达和视觉证明需要做合规审核。
- 如果源视频音频复杂，建议单独进行 ASR 转写或人工补充台词内容。

---

## 开源协议

本项目使用 MIT License。详见 [LICENSE](./LICENSE)。

---

## 一句话总结

`seedance-ad-replicator` 是一个面向广告视频创作者的 Seedance 复刻 Skill：

```text
广告视频
-> 广告策略分析
-> 小于15秒自然分段
-> 拉片笔记
-> Seedance 复刻 Prompt
-> 替换成自己的产品和品牌资产
```

它适合用来把成熟广告的结构迁移到自己的产品视频生产中。  
核心原则是：**复刻结构，替换资产，避免侵权。**
