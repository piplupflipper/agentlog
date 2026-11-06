# agentlog 📈💅 — session metrics for AI agents

**English** | [日本語](README.ja.md)

agentlog reads the transcripts that Claude Code and Codex leave behind, once when each session ends, and squishes them into a jsonl file with one line per session 💖✨  
It doesn't use an LLM to summarize anything, sooo measuring adds zero tokens to your actual sessions 🪶

- 🐍 What it is: a single file, `agentlog` (Python 3.9+, standard library only)
- 💾 Where it saves: `~/.local/share/agentlog/sessions.jsonl` (not tracked by Git)

## 📦 Install

```sh
install -m 755 agentlog ~/.local/bin/agentlog
```

The hook calls `~/.local/bin/agentlog`, so put it right there okay? 🙏

## 🚀 Usage

```sh
agentlog install-hook          # idempotently register a SessionEnd hook in ~/.claude/settings.json and ~/.codex/hooks.json (first time only)
agentlog scan --since 7d       # import sessions from before the hook, or ones it missed, from transcripts
agentlog show --since 7d       # list (start time / origin / minutes / turns / output tokens / final context / tools / prompt)
agentlog stats --since 30d     # totals for a period (4 token kinds, origins, tools, primitive commands, skills)
agentlog show --json | jq ...  # raw records
```

Filters: `--agent claude|codex` / `--origin user|headless|subagent` / `--no-sub` 🔍  
Updated the schema? Recount with `agentlog scan --since 30d --force` 🔁

## 📝 What gets recorded

| Field | Contents |
|---|---|
| Prompt | First 200 characters of the first user input |
| Results | `git commit` messages, edited files |
| Tokens | output / cache_creation / input / cache_read / thinking / final context |
| Tools | Call count per tool name (Bash / Read / Edit / LSP / mcp__* ...) |
| Primitive commands | How often each leading shell command shows up (grep / sed / awk / jq ...) |
| skills | Names of the Skills that were invoked |
| Tracked commands | Count of commands matching the regexes in `config.json` |
| Related | issue / MR numbers (from branch names, glab commands, commit messages) |
| Structure | Number of subagents, `parent_id` |

## ⚙️ Config

Wanna count how many times some specific command runs? Write a name and a regex in `~/.config/agentlog/config.json` (follows `XDG_CONFIG_HOME`) 💡

```json
{
  "tracked_commands": {
    "deploy": "\\bdeploy\\.sh\\b"
  }
}
```

The counts go into the record's `tracked_commands`, and show up on the `tracked:` line of `agentlog stats` 📊  
No config file means nothing gets counted.

## 🧭 Origin

You can tell apart sessions a human started from ones an agent kicked off 👀

| origin | Meaning |
|---|---|
| `user` | Started interactively by a human (Claude's cli, Codex's tui / remote) |
| `headless` | Started non-interactively (`codex exec`, etc.). Called by a script or another agent |
| `subagent` | A child spawned by Claude's Agent tool / Codex's spawn_agent. `parent_id` points to the parent |

When Codex is launched from Claude's Bash, the hook sees `CLAUDECODE=1` and adds `launcher: claude` (the scan path can't pick this up) 🔗

## ⚠️ Good to know

- git commits are picked up from the `[branch hash] message` output, so ones silenced with `git commit -q` aren't counted
- Codex skills are guessed from commands that read `skills/<name>/SKILL.md` (for Claude, Skill tool calls are the source of truth)
- For Codex's SessionEnd hook, the only thing confirmed is that the real binary contains the strings `SessionEnd` / `transcript_path` (2026-09-08). Anything it misses gets filled in by `agentlog scan`
- As of 2026-09-08, Claude's `entrypoint` has only ever been seen as `cli`. If some other value shows up, it's folded into `headless` and the raw value is kept in `launch_via`

## 📜 License

MIT 💖
