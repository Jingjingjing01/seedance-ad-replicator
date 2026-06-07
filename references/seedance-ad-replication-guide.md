# Seedance Ad Replication Guide

Use this reference to convert source-ad analysis into compact Seedance remake prompts.

## Segment Function Labels

- Hook: first visual or audio grab, usually 0-3s.
- Pain point: user problem, frustration, contrast, or curiosity gap.
- Product reveal: product/brand/solution enters clearly.
- Benefit proof: visible demonstration of the selling point.
- Lifestyle context: usage scene and target audience identification.
- Social proof: testimonial, creator reaction, crowd, review, before/after.
- Offer/CTA: price, promotion, app action, live room, purchase cue.
- Brand memory: logo, slogan, pack shot, mascot, signature sound.

## Replication Prompt Skeleton

```text
【全局设定】
复刻源广告第N段的结构与节奏，时长X秒，广告类型为「...」。目标是用新产品/新品牌复刻源视频的「Hook/痛点/产品展示/卖点证明/CTA」功能。整体风格：...

【素材参考】
@视频1：源广告，仅参考运镜、剪辑节奏、镜头结构和表演节奏，不参考原品牌Logo/包装/人物身份。
@图片1：新产品外观、包装、Logo参考。
@图片2：人物/场景/风格参考。
@音频1：口播音色/BGM/节奏参考。

【镜头1｜0-Xs】
景别/机位/运镜：...
主体/动作：...
广告功能：Hook/痛点/卖点...
音频/文字：...

【后期约束】
新产品外观和Logo稳定清晰；不出现源广告品牌信息；无多余字幕、水印、乱码；人物不变脸、不多人同脸；动作自然，画面不跳闪。
```

## Compact Camera Phrases

- 特写慢推：产品细节、Logo、材质、表情。
- 中景固定：口播、达人种草、直播带货。
- 手持轻微跟拍：UGC真实感、街采、门店探访。
- 微距切特写：食品质感、液体、面料、护肤质地、清洁效果。
- 快切固定镜头：投流广告节奏，避免过度复杂运镜。
- 环绕+定格：产品全貌展示后锁定核心卖点。
- 横摇/竖摇揭示：从痛点场景揭示产品或结果。
- 匹配剪辑：前后对比、旧产品到新产品、使用前到使用后。

## Multimodal Rules

- Define references before using them.
- Use stable names: `达人@图片2`, `主商品@图片1`, `源广告@视频1`.
- If copying a source video, specify `只参考` and `不参考`.
- For replacement: `将源视频中的旧产品替换为@图片1中的新产品，保持位置、大小、透视、遮挡、动作和运镜一致`.
- For voice: `@音频1仅参考音色、语速和情绪，不复刻原广告具体文案` unless the user owns the source copy.

## Ad-Specific Constraints

- Product appearance, packaging, color, logo, and readable text should stay stable when supplied.
- Do not invent exaggerated product proof that could be misleading.
- If source has screen text, preserve the timing/position style but replace copy only when the user provides approved text.
- If source has CTA and user did not provide new CTA, describe it generically: `结尾出现购买/进直播间引导位置，具体文案由后期替换`.
- If user says no subtitles, enforce `画面无字幕、无中文、无任何屏幕文字`.
- Do not add `4K`, `60fps`, `HDR`, or weight tags by default.

## Common Failure Fixes

- ID drift: request or use a cropped face reference; add `五官、发型、妆容、服装全程一致`.
- Product drift: use product-only reference; repeat `主商品@图片1外观、比例、Logo、包装文字全程不变形`.
- Source brand leakage: add `不要出现源广告品牌、旧Logo、旧包装文字、原人物身份信息`.
- Duplicate person: add `不要复制同一人物，不要多人同脸`.
- Subtitle noise: add `无乱码、无多余字幕、无水印、无无关Logo`.
- Segment continuity: end one segment with a clear state and start the next with `承接上一段尾帧状态`.
