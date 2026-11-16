# story-so-far（事件进展）

[English](README.md) | **简体中文**

> 一页纸跟上一件正在发酵的公共事件：哪些站得住、哪些还没落地、哪些已经撤回、接下来盯什么，以及和你上次问时相比有什么变化。

`story-so-far` 是一个智能体技能，适用于 Claude Code、Codex、Cursor，以及任何能读取 `SKILL.md` 的智能体。当某件事突然爆了（服务宕机、产品翻车、开源协议变更、诉讼、政策反转、网络群嘲），而你想知道的是“现在到底什么情况”、不是“最吵的版本”时，就用它。

## 为什么需要

“搜一下再总结”的回答，会把一件乱糟糟的事压成一段很自信的话：把同一个论坛帖的十条转发算成十个来源，把公司对自己的表态当成证实，把预测市场赔率当新闻引用，还漏掉了昨天刚发的更正。`story-so-far` 给智能体一套简短而严格的流程，把这些东西分开。

## 功能

- **每条说法都定级**：CONFIRMED / REPORTED / CLAIMED / RUMOR / DISPUTED / CORRECTED·RETRACTED / SUPERSEDED，每级都有最低证据门槛
- **回声合并**：综述、转帖、“据某某报道”的文章，先追到源头再计数（“一个源头，很多张嘴”）
- **当事方检查**：当事方证实自己的说法，仍然只算 CLAIMED
- **区分发生时间与报道时间**，并标出**转折点**
- **源头追溯**：在简报里写明最早那条和爆款版本之间的差距
- **热度单列**：互动量只说明大家关心什么，永远不当证据，并且必须带抓取时间
- **公平陈述各方**，依据是他们实际说过的话
- **往前看**：有日期的待观察事项，以及能推翻结论的证据
- **增量模式**：保留 `story.json`，下次对比后先报变化
- **中英双语输出**：简报可渲染为中文或英文
- 可选的零依赖辅助脚本 `storybrief.py`（`new` / `lint` / `render` / `diff`），附测试

## 安装

把整个文件夹复制到智能体的技能目录：

| 智能体 | 位置 |
|---|---|
| Claude Code | `~/.claude/skills/story-so-far/`（或项目内 `.claude/skills/`） |
| Codex | `~/.codex/skills/story-so-far/` |
| Cursor | 项目内 `.cursor/skills/story-so-far/` |
| 其他 | 智能体加载 `SKILL.md` 技能的目录，或直接把 `SKILL.md` 放进系统提示词 |

```bash
git clone https://github.com/fangdididi/story-so-far.git ~/.claude/skills/story-so-far
```

## 使用

像平时一样提问就行：

- “Quarry DB 改协议那事怎么回事？”
- “支付宕机导致卡号泄露，是真的吗？”
- “用 60 秒帮我捋一下 ___ 诉讼”
- “___ 从昨天到现在有新进展吗？”

智能体会写事件卡、追源头、按层扫描来源、逐条定级，然后给出简报。需要文件的话，它会保留 `story.json`，下次提问时直接给出变化。

直接使用辅助脚本：

```bash
python3 scripts/storybrief.py new ./mystory "一句话描述事件"
python3 scripts/storybrief.py lint ./mystory/story.json
python3 scripts/storybrief.py render ./mystory/story.json --lang zh
python3 scripts/storybrief.py diff yesterday.json today.json
python3 -m unittest discover -s tests
```

## 示例（虚构）

第 1 天（`examples/story-day1.json`）：协议变更 PR 确实已开（CONFIRMED）。“所有版本闭源”是 RUMOR，三个来源合并后只剩一个论坛帖。“只改 9.0+”是公司的 CLAIMED。

第 8 天（`examples/story-day8.json`），`diff` 输出：

```
MOVED    c2 RUMOR -> SUPERSEDED: All past releases will be relicensed
NEW      c4 [CONFIRMED] The merged change applies to 9.0 and later only; 8.x tags keep the old license
NEW      c5 [CLAIMED] A community fork will be maintained from the last 8.x tag
BEAT     2026-03-10T19:00Z: PR merged after maintainer call
```

渲染后的简报见 `examples/brief-day8.en.md` 和 `examples/brief-day8.zh-CN.md`。

## 文件结构

```
story-so-far/
├── SKILL.md                 # 技能说明（英文）
├── SKILL.zh-CN.md           # 技能说明（中文）
├── README.md
├── README.zh-CN.md
├── LICENSE
├── scripts/
│   └── storybrief.py        # new / lint / render / diff（仅标准库）
├── examples/
│   ├── story-day1.json      # 虚构事件，首份简报
│   ├── story-day8.json      # 同一事件一周后
│   ├── brief-day8.en.md
│   └── brief-day8.zh-CN.md
└── tests/
    └── test_storybrief.py
```

## 许可证

MIT © fangdididi
