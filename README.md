# Pet Drama Studio

> 项目状态：阶段 A 实施中，尚未租用或部署 GPU
> 文档日期：2026-08-21
> 交接对象：继续推进本项目的 AI Agent
> 当前分支：`codex/stage-a`

## 1. 项目目标

本项目要建立一套运行在 **AutoDL 云 GPU + ComfyUI** 上的个人 AI 宠物短剧生产环境。

目标不是简单地“把 ComfyUI 跑起来”，而是逐步形成一套可重复、可恢复、可自动化的短视频制作流程，用于兴趣创作并发布到抖音、TikTok 等短视频平台，尝试积累观众和粉丝。

计划制作的内容包括：

- AI 宠物爆笑短剧
- 宠物拟人短剧
- 固定角色连续剧情
- 动漫或国风漫剧
- 多角色竖屏短剧
- 参考图片驱动的视频镜头
- 后续可能扩展的复杂 AI 视频内容

当前属于个人兴趣项目。近期不以商业部署、团队 SaaS、企业 SLA 或大规模并发为目标。模型选择仍应记录许可证，但不需要为了潜在商业化牺牲当前创作质量和易用性。

## 2. 当前明确决策

除非实测证明存在严重兼容性或成本问题，后续 AI 应以这一条主路线推进，不要再次提供大量平行选项。

### 2.1 云计算平台

- 平台：AutoDL
- 实例类型：容器实例、按量计费
- GPU：单张 NVIDIA RTX 5090 32GB
- 系统内存：至少 90GB；同价时优先选择 128GB
- 本地数据盘：总容量 200GB（默认 50GB + 付费扩容 150GB）
- 不使用多卡
- 不租 A100、H100 或其他高价数据中心卡

选择 RTX 5090 的原因：5090 的 32GB 显存、Blackwell 低精度计算能力和较高内存带宽适合 FLUX.2 与 22B 视频模型。2026-08-21 实时调查时，西北 B 区 RTX 5090 会员按量价格为约 2.78 元/小时，常见配置为 25 核 CPU 与 90–92GB 内存；价格、库存和具体主机配置在租用前仍须重新确认。

AutoDL 本地数据盘会员参考价格约为 0.0066 元/GB/日。总容量 200GB 时付费容量约 150GB，即约 0.99 元/日、29.70 元/30日；数据盘在实例关机后仍继续收费，直到缩容或释放实例。第一阶段不扩到 500GB。

### 2.2 核心软件

- ComfyUI 官方稳定 Release
- ComfyUI 当前集成的 Manager / Registry
- 浏览器自动化：ego-browser（ego-lite）
- 服务器操作：SSH + shell 脚本
- 生成任务：ComfyUI HTTP/WebSocket API
- 后期剪辑：剪映或 DaVinci Resolve，暂不纳入第一阶段自动化

生产/稳定环境不自动跟随 ComfyUI `master`、nightly 或 custom nodes 最新提交。所有可运行版本最终必须记录 tag、commit 或版本号。

### 2.3 图像模型

首选：**FLUX.2 [dev] FP8 Mixed + Mistral BF16 + 官方 VAE**。

用途：

- 多参考图角色生成
- 单图和多图编辑
- 固定角色更换动作、服装和场景
- 角色、物体、背景和风格组合
- 为视频生成高质量起始帧或首尾帧

固定使用 ComfyUI 官方工作流列出的文件，不下载完整 BF16 Transformer：

```text
diffusion_models/flux2_dev_fp8mixed.safetensors
text_encoders/mistral_3_small_flux2_bf16.safetensors
vae/flux2-vae.safetensors
```

这组文件约 71.4GB。Transformer 使用 FP8 Mixed，文本编码器保留 BF16 以优先保证提示词理解和多参考图质量；RTX 5090 运行时由 ComfyUI 管理 CPU offload。只有实测 90GB 系统内存不足或速度不可接受时，才把文本编码器降级为 FP4/FP8，不提前下载平行版本。

已有 RTX 5090、20 步 FP8 Mixed 的社区实测显示：首次冷启动约 56 秒，模型热加载后约 20–25 秒/张。项目预算按普通首帧 20–60 秒、多参考或高分辨率首帧 30–90 秒估算，最终以首次 AutoDL 黄金镜头测试为准。

FLUX.1 Kontext-dev 作为后备方案保留，不作为默认主线。它是 12B、单参考编辑更轻更快；只有当 FLUX.2 在 5090 上实测速度不可接受、工作流不稳定或磁盘/内存不足时，才降级到 FLUX.1 Kontext-dev。

官方来源：

- [FLUX.2 dev 模型卡](https://huggingface.co/black-forest-labs/FLUX.2-dev)
- [FLUX.1 Kontext-dev 模型卡](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev)
- [ComfyUI 官方仓库](https://github.com/Comfy-Org/ComfyUI)

### 2.4 视频模型

首选：**LTX 2.5 Distilled Comfy INT8 ConvRot**。

第一阶段目标是图片驱动视频：将 FLUX.2 生成并经人工确认的首帧交给 LTX 2.5，生成 3–5 秒镜头。Distilled 使用官方固定 8 步路线，优先保证前期迭代速度；不下载 Dev Transformer。同步音频能力和所有官方辅助组件均准备好，但提示词增强与时间超分由任务参数控制，不强制对每个镜头启用。

计划使用的唯一 LTX 2.5 文件组：

```text
diffusion_models/ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors
text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors
text_encoders/gemma4_e2b_it_int8_convrot.safetensors
vae/ltx-2.5-video-vae-bf16.safetensors
vae/ltx-2.5-audio-vae-bf16.safetensors
model_patches/ltx-2.5-duration-head-bf16.safetensors
latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors
latent_upscale_models/ltx-2.5-latent-temporal-upscaler-x2-bf16-1.0.safetensors
```

其中第二个 Gemma 文件是可选提示词增强器，约 5GB，启用时通常额外增加约 1–2 分钟；Audio VAE 用于同步音频编码和解码；Spatial Upscaler 用于空间分辨率提升；Temporal Upscaler 用于补充中间帧、提高有效帧率；Duration Head 用于根据提示词自动预测时长。所有组件下载，但提示词增强器和 Temporal Upscaler 默认关闭，需要时按镜头开启。

这组文件约 45GB。不下载 Dev、BF16 Transformer、NVFP4、多个量化版本或 Dev 双阶段所需的 Distilled LoRA。RTX 5090 的 Distilled 社区实测约为 8–10 秒视频 1–2 分钟；项目对 3–5 秒 I2V 镜头先按 40–100 秒估算，最终以首次部署实测为准。结构错误、角色变形和动作失败必须在生成阶段通过有限候选解决；DaVinci Resolve 只承担本地剪辑、调色、降噪、补帧与超分，不能替代生成质量判断。

官方来源：

- [LTX 2.5 模型卡](https://huggingface.co/Lightricks/LTX-2.5)
- [LTX-2 官方推理仓库](https://github.com/Lightricks/LTX-2)
- [LTX ComfyUI 扩展与工作流](https://github.com/Lightricks/ComfyUI-LTXVideo)

## 3. 用户期望的创作流程

```text
创意或剧本
    ↓
拆成6–12个短镜头
    ↓
建立固定角色参考图与角色设定
    ↓
FLUX.2生成每个镜头的首帧候选
    ↓
人工挑选和批准首帧
    ↓
LTX 2.5生成每个3–5秒视频镜头
    ↓
人工挑选可用镜头
    ↓
剪映或DaVinci完成剪辑、配音、音效和字幕
    ↓
导出9:16竖屏成片
    ↓
发布到短视频平台
```

第一阶段不要直接生成完整 30–60 秒连续视频。以镜头为任务单位；某个镜头失败时只重跑该镜头。

## 4. 项目最终应承担的职责

本项目是“生产控制仓库”，不把逻辑散落在 AutoDL 实例中。

阶段 A 已开始创建以下结构：

```text
pet-drama-studio/
├── README.md
├── config/
│   ├── models.yaml
│   ├── nodes.yaml
│   └── storage.yaml
├── characters/
│   └── <character-id>/
├── stories/
│   └── <project-id>/
├── workflows/
│   ├── flux2-multireference.ui.json
│   └── ltx25-image-to-video.ui.json
├── prompts/
│   ├── character.md
│   ├── shot.md
│   └── video-motion.md
├── jobs/
├── manifests/
│   ├── model-lock.yaml
│   ├── nodes-lock.yaml
│   └── environment-lock.txt
└── scripts/
    ├── bootstrap-autodl.sh
    ├── download-models.sh
    ├── start-comfyui.sh
    ├── submit-workflow.py
    ├── sync-results.sh
    └── shutdown-after-job.sh
```

当前 `*.ui.json` 是固定 commit 的 ComfyUI 官方 UI 模板原件。首次部署验证后，需要从锁定的 ComfyUI 版本导出对应的 `*.api.json`，再由 `submit-workflow.py` 提交；在 API 文件生成并验证前，不把 UI JSON 误当作可提交工作流。

项目应保存：

- 模型 ID、revision、下载 URL、文件大小和 SHA256
- ComfyUI 版本
- custom nodes 的仓库地址和固定 commit
- 可直接通过 API 提交的 workflow JSON
- 角色设定和参考资产索引
- 剧本、分镜和 ShotSpec
- 每次生成的 prompt、seed、参数、模型版本和输出 hash
- 下载、启动、同步、关机和恢复脚本

## 5. AutoDL 存储设计

AutoDL 实例内部建议使用以下路径：

```text
/root/autodl-tmp/pet-drama-studio/       # 本地高速数据盘，可丢失、可重建
├── ComfyUI/
│   ├── models/
│   │   ├── diffusion_models/
│   │   ├── text_encoders/
│   │   ├── vae/
│   │   ├── model_patches/
│   │   ├── latent_upscale_models/
│   │   ├── loras/
│   │   ├── controlnet/
│   │   └── upscale_models/
│   ├── input/
│   ├── output/
│   ├── custom_nodes/
│   └── user/
├── cache/
├── temp-frames/
└── jobs/

/root/autodl-fs/pet-drama-studio/        # 同地区可靠共享层
├── manifests/
├── workflows/
├── characters/
├── jobs/
├── logs/
└── approved-outputs/
```

规则：

- 大模型、缓存、临时帧放 `/root/autodl-tmp`。
- 工作流、角色参考图、自训 LoRA、提示词、任务记录和精选成片放 `/root/autodl-fs`，并尽可能再备份到用户控制的外部存储。
- 不把大模型放入 30GB 系统盘。
- 不把完整模型库保存进 AutoDL 私有镜像。
- ComfyUI 可通过 `extra_model_paths.yaml` 指向统一模型目录，避免复制权重。

已核实的 AutoDL 事实：

- `/root/autodl-tmp` 是本地数据盘，速度快但无冗余，不进入系统镜像。
- `/root/autodl-fs` 是同地区可跨实例挂载的文件存储，20GB 免费，超出部分按量计费。
- 按量实例关机停止实例费，但扩容数据盘、文件存储、网盘和超额镜像可能继续收费。
- 实例连续关机 15 天会被释放，本地系统盘和数据盘内容随后无法恢复。
- AutoDL 普通容器实例内部不支持再次运行 Docker。

官方文档：

- [AutoDL 实例与目录](https://www.autodl.com/docs/env/)
- [数据保留](https://www.autodl.com/docs/instance_data/)
- [本地数据盘](https://www.autodl.com/docs/local_disk/)
- [文件存储](https://www.autodl.com/docs/fs/)
- [计费规则](https://www.autodl.com/docs/price/)

## 6. 自动化架构

不要让 ego-lite 通过拖拽 ComfyUI 节点画布承担核心生成逻辑。节点画布是视觉化、动态布局界面，使用坐标自动化容易受到缩放、窗口尺寸和节点位置影响。

正确分工：

| 能力 | 推荐方式 |
|---|---|
| AutoDL 登录、查看库存和价格 | ego-lite |
| 创建、启动、关闭实例 | ego-lite；涉及付费或租用前必须获得用户明确授权 |
| 验证码、登录确认 | ego-lite 将控制权交给用户 |
| 系统检查和模型下载 | SSH + shell 脚本 |
| 启动和停止 ComfyUI | SSH + shell 脚本 |
| 提交 FLUX/LTX 工作流 | ComfyUI API |
| 查询任务进度 | ComfyUI API/WebSocket |
| 校验文件和同步输出 | 脚本、checksum 和日志 |
| 视觉质量判断 | AI 视觉检查 + 人工最终选择 |
| AutoDL 关机 | 任务脚本执行 `/usr/bin/shutdown`，控制台作为兜底 |

ego-lite 可以在隔离的浏览器任务空间中复用用户登录状态。遇到验证码、支付、租用确认或用户接管时，Agent 必须暂停并交还控制，不能绕过或自行重试敏感操作。

## 7. Project 与 Skill 的关系

当前先做项目，不先创建 Skill。

- **Project** 保存脚本、配置、工作流、角色资产、任务和状态，是实际系统。
- **Skill** 是教 AI Agent 如何使用该项目的可复用操作说明，不应该替代项目本身。
- **ego-lite** 是网页操作通道，不是任务数据库，也不是生成编排器。

只有在手工或半自动完成至少 3 次完整的“启动实例 → 生成 → 同步 → 关机”流程，并确认步骤稳定后，才创建 `autodl-pet-drama` Skill。未来 Skill 应调用项目脚本，而不是重复实现下载和工作流逻辑。

## 8. 后续 AI 的推进阶段

### 阶段 A：本地项目设计，不租 GPU

目标：在不触发任何付费行为的前提下，把项目建设成可部署状态。

任务：

1. 建立上文建议的项目目录。
2. 编写模型 manifest，使用官方 Hugging Face 文件，记录大小与 hash。
3. 选择支持 FLUX.2 和 LTX 2.5 的具体 ComfyUI 稳定版本。
4. 选择最少量 custom nodes；优先使用 ComfyUI native nodes 和官方 LTX 集成。
5. 准备可恢复的安装脚本，但不要在本机执行。
6. 准备 ComfyUI 启动、健康检查、任务提交、结果同步和自动关机脚本。
7. 准备一个最小角色数据格式和 ShotSpec 格式。
8. 写清首次部署时需要用户完成的 Hugging Face 许可接受和 Token 输入步骤。

阶段 A 验收：仓库中不存在模型文件或密钥；脚本默认 dry-run；所有付费和远程写入步骤都有明显的用户确认点。

### 阶段 B：首次 AutoDL 部署

开始条件：用户明确授权租用 GPU 和产生费用。

任务：

1. ego-lite 打开 AutoDL 并读取当时 RTX 5090 的真实库存、CPU、RAM、数据盘和价格。
2. 在真正创建实例之前，把完整配置与预计成本展示给用户确认。
3. 用户确认后创建一张 5090 实例。
4. 使用官方基础镜像，不使用来源不明的社区整合镜像。
5. 通过 SSH 运行 bootstrap 和下载脚本。
6. 模型全部下载到 `/root/autodl-tmp/pet-drama-studio/ComfyUI/models/`。
7. 启动 ComfyUI 并运行健康检查。
8. 只验证一个 FLUX.2 工作流和一个 LTX 2.5 I2V 工作流。
9. 将工作流、日志和样片同步到可靠存储。
10. 确认同步成功后关闭实例。

### 阶段 C：黄金镜头测试

建立 10 个固定测试镜头：

- 单角色正面
- 单角色侧面
- 全身动作
- 快速运动
- 明显表情
- 两个角色同框
- 遮挡
- 手持道具或宠物爪与物体交互
- 室内场景
- 室外或复杂背景

每个镜头记录：

- FLUX.2 首帧生成次数和入选率
- LTX 2.5 候选次数和可用率
- 单次耗时
- 峰值显存
- 是否发生 CPU offload
- GPU 卡时成本
- 角色一致性问题
- 肢体、动作、背景和镜头问题

### 阶段 D：第一条完整短剧

限制范围：

- 30–45 秒
- 9:16 竖屏
- 两个固定宠物角色
- 一个主要场景
- 6–12 个镜头
- 每个生成镜头 3–5 秒
- 最终剪辑和发布由用户确认

第一条短剧的目标不是爆款，而是证明整条技术链能够完成、恢复、计费和复现。

### 阶段 E：稳定后封装 Skill

只有阶段 B–D 已反复成功，才创建 Skill。建议支持以下请求：

- “启动宠物短剧环境”
- “把这个剧本拆成镜头任务”
- “为这些镜头生成 FLUX.2 首帧”
- “把已批准首帧提交给 LTX 2.5”
- “继续失败的镜头”
- “同步结果并关闭 AutoDL”
- “检查本次生成消耗和失败原因”

## 9. 安全与成本边界

后续 AI 必须遵守：

- 在用户明确授权前，不租 GPU、不创建 AutoDL 实例、不购买存储、不充值。
- 不在本机下载几十或上百 GB 模型。
- 不把 Hugging Face Token、AutoDL Cookie、SSH 密钥写入 Git 或日志。
- 不从无法追溯来源的网盘下载模型。
- custom nodes 是可执行代码；安装前检查仓库、最近活动、依赖和 Registry 状态。
- 不自动更新全部 custom nodes。
- 不在任务失败时无限重试并持续消耗 GPU。
- 生成完成后必须先验证输出已经保存，再关闭实例。
- 设置任务级关机、墙钟超时关机和 AutoDL 控制台定时关机三层保护。
- 关闭浏览器标签页不等于关闭 AutoDL 实例。

## 10. 第一阶段不做什么

- 不做多 GPU 并行。
- 不做 Kubernetes 或 Docker Compose；普通 AutoDL 容器内不支持 Docker。
- 不做 7×24 在线服务。
- 不做复杂 Web 管理后台。
- 不训练角色 LoRA，除非参考图方案在多条样片中稳定失败。
- 不一次安装几十个 custom nodes。
- 不一次下载多个 FLUX 和视频大模型。
- 不直接追求一分钟连续生成。
- 不自动发布到短视频平台。
- 不自动进行充值、购买、租用或其他资金操作。

## 11. 最小任务数据格式

后续可以把每个镜头表示为：

```yaml
project_id: pet-comedy-001
episode_id: e01
shot_id: s001
duration_s: 4
aspect_ratio: "9:16"
characters:
  - cat_mi
  - dog_dou
location: living-room-v1
story_action: "小猫偷偷藏起零食，小狗突然回头"
camera: "medium two-shot, eye level, subtle push-in"
references:
  - characters/cat_mi/front.png
  - characters/dog_dou/front.png
  - locations/living-room-v1.png
image_workflow: flux2-multireference-v1
video_workflow: ltx25-i2v-v1
candidates:
  image: 4
  video: 3
status: planned
```

任务运行后还应记录模型 revision、节点版本、seed、prompt、分辨率、帧数、执行时间、GPU、峰值显存、退出码和输出 hash。

## 12. 验收标准

### 环境验收

- AutoDL 实例能从空白基础镜像按脚本恢复。
- ComfyUI 可以从固定版本启动。
- FLUX.2 与 LTX 2.5 模型路径正确且 hash 一致。
- 两个黄金工作流可通过 API 提交，不依赖手工拖节点。
- 重要输出能同步到可靠存储。
- 任务结束后实例能自动关机。

### 创作验收

- 同一个宠物角色在不同镜头中可被辨认。
- 首帧生成支持多参考图。
- 每个镜头至少能从有限候选中选出一个可用版本。
- 单个失败镜头可以独立重跑。
- 生成结果能够完成 9:16 短剧剪辑。

### 成本验收

- 每次任务有开始时间、结束时间和 GPU 卡时记录。
- 没有生成任务时实例不会长期保持运行。
- 下载、上传或调试优先使用无卡模式或在预算内完成。
- 能计算每条成片和每个可用镜头的大致成本。

## 13. 必须重新核实的动态信息

以下信息会变化，后续 AI 在实施当日必须查官方来源，不能直接沿用本文数字：

- AutoDL RTX 5090 的实时价格、库存、地区、CPU、RAM 和磁盘配置
- AutoDL 存储与镜像计费规则
- ComfyUI 最新稳定版本及原生 FLUX.2/LTX 2.5 支持情况
- LTX 2.5 和 FLUX.2 官方模型文件、推荐量化方式及目录
- RTX 5090 所需 PyTorch、CUDA、驱动及 Comfy INT8/FP8 兼容组合
- custom nodes 的维护状态、Registry 验证状态和依赖冲突
- 模型许可证是否更新

## 14. 给下一位 AI 的首个任务

在不租 GPU、不安装软件、不下载模型的前提下，把本项目推进到“可部署但尚未执行”的阶段：

1. 生成 `models.yaml`，锁定本文确定的唯一模型组合，列出精确文件名、官方 URL、大小、revision、SHA256 获取方法和目标目录。
2. 选择并锁定包含 FLUX.2 与 LTX 2.5 原生工作流的 ComfyUI 官方稳定版本。
3. 设计可重复执行、默认 dry-run 的 AutoDL bootstrap 与模型下载脚本。
4. 设计 ComfyUI API 健康检查、任务提交、输出同步和安全关机方式。
5. 准备角色数据格式、ShotSpec 和生成运行记录格式。
6. 提交文件变更给用户审阅；没有用户明确授权，不租用实例、不下载大模型、不产生费用。

最终目标是让用户可以对 AI Agent 说：

> “这是剧本和角色参考图。帮我启动环境、拆分镜头、生成首帧候选和视频候选，保存所有结果，然后关闭 AutoDL。”

AI Agent 应能在必要确认点与用户协作，完成其余可自动化步骤，并留下完整、可复现的记录。
