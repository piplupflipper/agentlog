# agentlog 📈💅 — AI エージェントのセッション計測

[English](README.md) | **日本語**

Claude Code と Codex が残す transcript を、セッションが終わったときに 1 回だけ読んで、1 セッション 1 行の jsonl にまとめちゃうよ💖✨  
LLM で要約とかしないから、計測のせいでセッション本体のトークンが増えることはゼロ！🪶

- 🐍 実体: `agentlog` の 1 ファイル (Python 3.9 以上、標準ライブラリだけ)
- 💾 保存先: `~/.local/share/agentlog/sessions.jsonl` (Git 管理外)

## 📦 導入

```sh
install -m 755 agentlog ~/.local/bin/agentlog
```

hook は `~/.local/bin/agentlog` を呼ぶから、ここに置いてね🙏

## 🚀 使い方

```sh
agentlog install-hook          # ~/.claude/settings.json と ~/.codex/hooks.json に SessionEnd hook を冪等登録 (初回のみ)
agentlog scan --since 7d       # hook を入れる前のセッションや取りこぼしを transcript から取り込む
agentlog show --since 7d       # 一覧 (開始時刻 / 起動元 / 所要分 / ターン数 / 出力トークン / 最終コンテキスト / ツール / 指示)
agentlog stats --since 30d     # 期間集計 (トークン 4 区分・起動元・ツール・原始コマンド・skills)
agentlog show --json | jq ...  # 生レコード
```

絞り込み: `--agent claude|codex` / `--origin user|headless|subagent` / `--no-sub` 🔍  
schema を更新したら `agentlog scan --since 30d --force` で集計し直してね🔁

## 📝 記録する項目

| 項目 | 中身 |
|---|---|
| 指示 | 最初のユーザー入力の先頭 200 字 |
| 成果 | `git commit` のメッセージ、編集したファイル |
| トークン | output / cache_creation / input / cache_read / thinking / 最終コンテキスト |
| ツール | ツール名ごとの呼出回数 (Bash / Read / Edit / LSP / mcp__* ...) |
| 原始コマンド | シェルの先頭コマンド頻度 (grep / sed / awk / jq ...) |
| skills | 呼んだ Skill 名 |
| 追跡コマンド | `config.json` で指定した正規表現に一致したコマンドの回数 |
| 関連 | issue / MR 番号 (ブランチ名・glab コマンド・コミットメッセージから) |
| 構造 | サブエージェント数、`parent_id` |

## ⚙️ 設定

特定のコマンドを何回呼んだか数えたいときは、`~/.config/agentlog/config.json` (`XDG_CONFIG_HOME` に従うよ) に名前と正規表現を書いてね💡

```json
{
  "tracked_commands": {
    "deploy": "\\bdeploy\\.sh\\b"
  }
}
```

回数はレコードの `tracked_commands` に入って、`agentlog stats` の `tracked:` 行に出るよ📊  
設定ファイルが無ければ何も数えないよ。

## 🧭 起動元 (origin)

人が起動したのか、エージェントが起こしたのかを分けて見られるよ👀

| origin | 意味 |
|---|---|
| `user` | 人が対話で起動 (Claude の cli、Codex の tui / remote) |
| `headless` | 非対話起動 (`codex exec` など)。スクリプトや他エージェントが呼ぶ形 |
| `subagent` | Claude の Agent ツール / Codex の spawn_agent が起こした子。`parent_id` が親を指す |

Codex が Claude の Bash から起動されたときは、hook が `CLAUDECODE=1` を見て `launcher: claude` を付けるよ (scan 経路では取れないよ) 🔗

## ⚠️ 知っといてほしいこと

- git commit は `[branch hash] message` の出力から拾うから、`git commit -q` で黙らせたものは数えないよ
- Codex の skills は `skills/<name>/SKILL.md` を読んだコマンドから推定してるよ (Claude は Skill ツールの呼び出しが正)
- Codex 側の SessionEnd hook は、実バイナリに `SessionEnd` / `transcript_path` の文字列があることだけ確認済みだよ (2026-09-08)。取りこぼしは `agentlog scan` で埋まるよ
- Claude の `entrypoint` は 2026-09-08 時点で `cli` しか見たことないよ。別の値が来たら `headless` に寄せて、生の値を `launch_via` に残すよ

## 📜 ライセンス

MIT 💖
