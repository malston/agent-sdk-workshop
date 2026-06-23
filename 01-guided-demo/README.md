# 01 — Guided Demo

**One agent. One task. Four runs.** Flip a switch between each run and watch the agent get progressively better at preparing a company briefing.

---

## The loop

1. Run `./workshop demo` (from the repo root)
2. Read the output
3. Open `config.py`, flip the next switch
4. Repeat

**`config.py` is the only file you edit.** Three boolean switches, flipped one at a time.

---

## The stages

→ **See [`GUIDE.md`](./GUIDE.md) for the full stage-by-stage walkthrough** — what to do, what to observe, what's happening under the hood at each stage.

| Stage | Switch             | What changes                              |
| ----- | ------------------ | ----------------------------------------- |
| 0     | _(all off)_        | Baseline — just chat with a system prompt |
| 1     | `ENABLE_TOOLS`     | Agent can look things up                  |
| 2     | `ENABLE_SUBAGENTS` | Agent delegates to specialists            |
| 3     | `ENABLE_MEMORY`    | Agent remembers between runs              |

---

## Available companies (mock data)

- **Tinplate Merchant Systems** — mid-market fintech, high growth, not yet profitable
- **Bucklefern Commerce Holdings** — mature public company, growth slowing
- **Ironvane Freight Systems** — supply chain software, recent leadership change

The data is interlinked — Ironvane's departing CPO shows up in Tinplate's hiring news. Gives the fact-checker sub-agent something real to verify.

---

## File map

| File                     | Purpose                                                     | Edit it?        |
| ------------------------ | ----------------------------------------------------------- | --------------- |
| **`config.py`**          | The three toggles + stretch goals                           | **YES**         |
| `GUIDE.md`               | Stage-by-stage walkthrough                                  | No (read it!)   |
| `agent.py`               | Entry point. **`build_options()` is the lesson** — read it. | No              |
| `tools.py`               | `@tool`-decorated research tools                            | Peek at Stage 1 |
| `subagents.py`           | `AgentDefinition` specs                                     | Peek at Stage 2 |
| `memory.py`              | Memory tool + context-injection hook                        | Peek at Stage 3 |
| `mock_data/*.json`       | Fictional company data                                      | No              |
| `replay.py`              | Offline transcript replay (no API key)                      | No              |
| `sample_transcript.json` | Bundled sample for `./workshop replay`                      | No              |

---

## Offline replay (no API key)

The demo runs the agent live through the SDK, so it needs an API key. To present it with no key and no flakiness, replay a captured transcript:

```bash
./workshop replay              # render the bundled sample
./workshop replay --verbose    # also show tool calls
```

Capture a fresh transcript from a real run, then replay it:

```bash
./workshop demo --record 01-guided-demo/sample_transcript.json
```

---

→ When you've done all four stages, head to [`../02-breakouts/`](../02-breakouts/).
