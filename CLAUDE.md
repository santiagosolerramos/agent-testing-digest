# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

`agent-testing-digest` is a daily research tool for an AI PM at Connectly. It automatically searches for new papers, posts, docs, and releases on agent evaluation, LLM testing, regression testing for agents, and synthetic user simulation — and generates a Markdown report with findings relevant to Connectly's context.

**Connectly context:** Connectly builds conversational agents on WhatsApp. They have an internal test framework called Test Framework that validates agent behavior using simulated personas (test cases with objectives, evaluations, and mock data). The digest is meant to help the team track how the most advanced AI companies approach agent testing and evaluation today.

## Running the digest

```bash
python main.py                  # Run the full digest pipeline
python main.py --date 2024-01-15  # Run for a specific date (if supported)
```

Output is written to `reports/digest_YYYY-MM-DD.md`.

## Architecture

The pipeline runs in three stages:

1. **Fetch** (`sources/`) — Each source module queries a specific channel (arXiv, Hacker News, Twitter/X, GitHub releases, LLM vendor blogs, etc.) and returns a list of raw items with title, url, summary, and date.

2. **Rank & Filter** (`ranker.py`) — Scores items by relevance to the core topics (agent evaluation, synthetic user simulation, LLM testing, regression testing for agents) and filters out noise and duplicates.

3. **Render** (`renderer.py`) — Takes the ranked items and calls the Claude API to produce a coherent Markdown digest grouped by theme, with a short editorial summary at the top.

### Key topics the ranker prioritizes
- Agent evaluation frameworks and benchmarks
- Synthetic user / persona simulation
- LLM regression testing and CI/CD for agents
- Red-teaming and adversarial testing of conversational agents
- Evals-as-code approaches (YAML/JSON test case formats, assertion libraries)

## Configuration

`config.py` holds API keys (loaded from `.env`) and tunable parameters (lookback window in days, relevance score threshold, max items per source, output directory).

`.env.example` documents all required environment variables.
