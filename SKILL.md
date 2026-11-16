---
name: story-so-far
description: Catch someone up on a fast-moving public story (an outage, a launch gone wrong, a license change, a lawsuit, a policy U-turn, an online controversy) with a dated, sourced brief that keeps what is solid apart from what is only loud. Use when the user asks "what's going on with X", "catch me up on X", "is it true that X", or "what changed since I last looked".
---

# story-so-far

## What this is

A method for turning a noisy, still-moving public story into a one-page catch-up brief that a busy person can trust.

When something blows up, the feed is a mix of the original event, honest reporting, the parties' own spin, recaps of recaps, jokes that get taken literally, retractions nobody shares, and prediction-market odds quoted as if they were facts. Ordinary "search and summarize" flattens all of that into one confident paragraph. The result sounds informed and is often wrong in exactly the places that matter.

This skill keeps three things apart that summaries usually merge:

1. **When something happened vs. when it was reported.** Every beat carries an event time, and a report time when they differ.
2. **How sure we are vs. how many people repeat it.** Each claim gets a status from a fixed ladder. Repetition never upgrades a status: ten posts that all trace back to one forum thread count as one source.
3. **What is true vs. what people are loudest about.** Engagement tells you what the crowd cares about. It is reported in its own section and never used as evidence.

The output is a brief, plus a small `story.json` file. Next time the user asks, you compare against it and report only what moved.

## When to use it

- "What's going on with ___?" / "Catch me up on ___" / "Explain the ___ drama"
- "Is it true that ___?" about something currently circulating
- "What changed since yesterday / since I last asked?"
- Before a meeting, a purchase, an upgrade, or a post where the user needs the current state of a public story
- When a teammate or a channel is reacting to something and the user wants the facts before joining in

Not for: settled history (use ordinary research), private disputes between people the user knows, or verifying a single photo or video (that is image forensics, a different job).

## Status ladder

| Status | Meaning | Minimum evidence |
|---|---|---|
| CONFIRMED | Treat as fact | A primary record from someone who is not a party (court docket, merged commit, status page, regulator filing), or two independent reports where each outlet had its own access |
| REPORTED | Credible but single-sourced | At least one reporting-layer source with a named outlet |
| CLAIMED | A party says so | Name who says it. Self-interest is the point to note |
| RUMOR | Circulating without a traceable source | Allowed with no source; say where it is circulating |
| DISPUTED | Credible sources conflict | Cite both sides of the conflict |
| CORRECTED / RETRACTED | Walked back by the outlet or person who said it | Link the correction itself |
| SUPERSEDED | Overtaken by later events | Point to the claim that replaced it |

Source layers: **primary** (the actors and the records), **reporting** (outlets with named reporters), **community** (forums, social posts, videos, newsletters), **market** (prediction markets, price moves). Markets are sentiment. They never move a claim up the ladder.

## Steps

### 1. Write the story card (one minute)
Pin down, in the user's words where you can:
- the story in one line
- what the user already knows, and since when (this sets the window)
- why they care: **decide**, **act**, **talk**, or just **curious**. This sets how much "what to watch" matters
- depth: a 60-second brief or a 5-minute brief
- anything out of scope (for example, people's private lives)

If the user gave you none of this, infer it and state your guess in one line. Do not interrogate them.

### 2. Find the origin
Work backwards from the loudest version to the earliest traceable item: the first post, filing, commit, status update, or statement. Record what it actually said, its event time in UTC, and its link. Many stories change shape on the way out. The distance between the origin and the viral version is often the most useful thing in the brief.

### 3. Sweep by layer, not by site
For each layer, look for what exists inside the window:
- **primary**: official accounts, changelogs, status pages, court and regulator records, repos, earnings releases. Mark whether each one is a party to the story (`self_interested`)
- **reporting**: outlets that name a reporter and say how they know (documents seen, people interviewed, on the record or not). Mark `own_access` only when they did their own work and are not rewriting someone else's scoop
- **community**: where people are reacting. Useful for what people care about and for leads. Weak as evidence
- **market**: only if it exists and the user would care

For every source, write down who, when, link, and whether it is an **echo** of another source (`echo_of`). Recaps, reposts, "according to [outlet]" articles, and aggregator videos are echoes.

### 4. Break it into claims and grade each one
Split the story into atomic, checkable sentences. Give each the lowest status its evidence supports. Rules:
- collapse echoes first, then count sources
- a party confirming its own story makes it CLAIMED, not CONFIRMED
- hedge words ("reportedly", "sources say") do not belong in a CONFIRMED sentence
- when a later source contradicts an earlier one, do not quietly delete the earlier claim. Mark it DISPUTED, CORRECTED, or SUPERSEDED so the reader sees the story moved
- numbers that are still changing (casualties, affected users, money lost) get a time stamp and the source in the sentence itself

### 5. Build the timeline
List beats in event-time order. Mark the **turns**, the two or three moments that changed the story's direction. Most readers only need the turns.

### 6. State the sides fairly
For each party with a stake, write the strongest honest version of their position in one or two sentences, based on what they actually said. No mind-reading and no labels for motives.

### 7. Report the heat separately
What are people loudest about? Give the topic and, only if you actually fetched it, the engagement number with the time you fetched it. Heat often points at the real question ("will there be a fork?") rather than at the facts.

### 8. Look forward
- **What to watch**: dated, scheduled things (a hearing, a vote, a release, a deadline, an earnings call)
- **What would change the picture**: the specific evidence that would flip your headline

### 9. Write the headline last
One sentence, with an "as of" time, that a reader could repeat to someone else without misleading them. Then write the brief in this order: headline, what is solid, what is still loose, walked back, timeline (turns only for the 60-second version), sides, heat, watch, sources.

### 10. Next time, report the delta
Keep `story.json`. When the user asks again, rebuild it and diff: new claims, claims that changed status, new beats, a new headline. Lead with what moved. Say plainly when nothing did.

## Helper script (optional)

`scripts/storybrief.py` uses only the Python standard library.

```bash
python3 scripts/storybrief.py new ./quarry "Quarry DB license change"
python3 scripts/storybrief.py lint ./quarry/story.json      # ladder, echo, and timeline rules
python3 scripts/storybrief.py render ./quarry/story.json --lang en   # or --lang zh
python3 scripts/storybrief.py diff old.json new.json        # what moved since last time
```

What `lint` enforces: CONFIRMED needs a non-party primary record or two independent reports with their own access, counted after echoes collapse (L03). REPORTED needs a reporting source (L04). CLAIMED names its claimant (L05). DISPUTED cites the other side (L06). Corrections link the correction (L07). SUPERSEDED points forward (L08). Market-only claims cannot be facts (L10). Engagement needs a fetch time (H01). There is a warning when three or more sources share one root ("one source, many mouths").

## Example (fictional)

The user asks: "Is Quarry DB going closed source? Everyone's posting about it."

60-second brief, as of 2026-03-04 09:00 UTC:
- **Where it stands:** A license change has been proposed, not merged. The company says it affects 9.0+ only. The "every version goes closed" story traces back to a single forum post.
- **Solid:** a pull request proposing a source-available license is open in the main repo.
- **Loose:** "all past releases will be relicensed" is a RUMOR. Three posts repeat it, and all of them trace back to one forum thread. "Only 9.0+ changes" is CLAIMED by Quarry Inc.
- **Turn:** 2 Mar 18:10 UTC, the PR was opened.
- **Watch:** maintainer call on 10 Mar, where the PR is up for a decision.
- **Would change it:** the PR merging or closing, or a statement from the foundation that holds the trademark.

A week later the user asks "anything new?" The diff leads with: the PR merged (CONFIRMED, 9.0+ only), the "all versions" rumor is SUPERSEDED, and a fork was announced (CLAIMED by its organisers). The full files are in `examples/`.

## Tips

- Spend the most care on the gap between the origin and the viral version. That is usually the story inside the story.
- Do not fill holes with guesses. "Unknown as of 09:00 UTC" is a valid line and readers trust it.
- Put times in UTC, and add the user's local time if they are in one timezone.
- Breaking news with injuries or deaths: use official figures with their time stamp, do not name suspects or victims who have not been officially identified, and expect early numbers to change.
- Private individuals swept into a public story stay out of the brief unless their role is the story. Even then, describe the role, not the person.
- If the user's own source turns out to be an echo or a rumor, say so kindly and show the trail.
- Keep quotes short and attributed. Paraphrase everything else.
- A brief is a snapshot, not a verdict. Always print the "as of" time.
