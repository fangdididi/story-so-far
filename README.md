# story-so-far

**English** | [简体中文](README.zh-CN.md)

> Catch up on a fast-moving public story in one page. You get what is solid, what is still loose, what was walked back, what to watch next, and what moved since you last asked.

`story-so-far` is an agent skill for Claude Code, Codex, Cursor, and any agent that reads `SKILL.md` files. Use it when something blows up (an outage, a botched launch, a license change, a lawsuit, a policy U-turn, an online pile-on) and you want the current state of things, not the loudest version of them.

## Why

Search-and-summarize answers flatten a messy story into one confident paragraph. They count ten reposts of one forum thread as ten sources. They take a company's statement about itself as confirmation. They quote prediction-market odds as if they were news, and they miss the correction that came out yesterday. `story-so-far` gives your agent a short, strict routine that keeps these things apart.

## Features

- **Status ladder for every claim**: CONFIRMED, REPORTED, CLAIMED, RUMOR, DISPUTED, CORRECTED/RETRACTED, SUPERSEDED, each with a minimum bar of evidence
- **Echo collapse**: recaps, reposts, and "according to…" pieces are traced back to their root before anything is counted ("one source, many mouths")
- **Party check**: a party confirming its own story stays CLAIMED
- **Event time vs report time** on every beat, with the **turns** marked
- **Origin trace**: the distance between the first item and the viral version, shown in the brief
- **Heat kept separate**: engagement shows what people care about. It is never used as evidence, and it always carries the time it was fetched
- **Sides stated fairly**, based on what each party actually said
- **Forward look**: dated things to watch, plus the evidence that would change the headline
- **Delta mode**: keep `story.json`, then diff the next run to lead with what moved
- **Bilingual output**: render the brief in English or Chinese
- Optional zero-dependency helper `storybrief.py` (`new` / `lint` / `render` / `diff`) with tests

## Install

Copy the folder into your agent's skills directory:

| Agent | Location |
|---|---|
| Claude Code | `~/.claude/skills/story-so-far/` (or `.claude/skills/` in a project) |
| Codex | `~/.codex/skills/story-so-far/` |
| Cursor | `.cursor/skills/story-so-far/` in your project |
| Others | wherever your agent loads `SKILL.md` skills, or paste `SKILL.md` into the system prompt |

```bash
git clone https://github.com/fangdididi/story-so-far.git ~/.claude/skills/story-so-far
```

## Usage

Ask the way you normally would:

- "What's going on with the Quarry DB license thing?"
- "Is it true that the payment outage leaked card numbers?"
- "Catch me up on the ___ lawsuit in 60 seconds"
- "Anything new on ___ since yesterday?"

The agent writes a story card, traces the origin, sweeps the sources layer by layer, grades each claim, and returns the brief. If you want a file, it keeps `story.json` so the next question gets a delta.

Using the helper directly:

```bash
python3 scripts/storybrief.py new ./mystory "One-line description of the story"
python3 scripts/storybrief.py lint ./mystory/story.json
python3 scripts/storybrief.py render ./mystory/story.json --lang en
python3 scripts/storybrief.py diff yesterday.json today.json
python3 -m unittest discover -s tests
```

## Example (fictional)

Day 1 (`examples/story-day1.json`): a license-change PR is open (CONFIRMED). "Every version goes closed" is a RUMOR, and its three sources collapse into a single forum thread. "Only 9.0+" is CLAIMED by the company.

Day 8 (`examples/story-day8.json`), `diff` output:

```
MOVED    c2 RUMOR -> SUPERSEDED: All past releases will be relicensed
NEW      c4 [CONFIRMED] The merged change applies to 9.0 and later only; 8.x tags keep the old license
NEW      c5 [CLAIMED] A community fork will be maintained from the last 8.x tag
BEAT     2026-03-10T19:00Z: PR merged after maintainer call
```

The rendered briefs are in `examples/brief-day8.en.md` and `examples/brief-day8.zh-CN.md`.

## File structure

```
story-so-far/
├── SKILL.md                 # skill instructions (English)
├── SKILL.zh-CN.md           # skill instructions (Chinese)
├── README.md
├── README.zh-CN.md
├── LICENSE
├── scripts/
│   └── storybrief.py        # new / lint / render / diff (standard library only)
├── examples/
│   ├── story-day1.json      # fictional story, first brief
│   ├── story-day8.json      # same story a week later
│   ├── brief-day8.en.md
│   └── brief-day8.zh-CN.md
└── tests/
    └── test_storybrief.py
```

## License

MIT © fangdididi
