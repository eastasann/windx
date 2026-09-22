# windx — 開発プロセス標準

Google の **design docs 文化**を AI 駆動開発に落とし込み、
**チケット管理・ロードマップ・意思決定記録のすべてを GitHub で完結**させるための
プロセス標準とツール一式です。

---

## 1. なぜ design doc なのか（AI 駆動での再定義）

Google の design doc の本質は 2 つでした。

1. **書くことによる思考** — 散文で書くと、曖昧な設計は書けない
2. **レビューによる合意** — 実装前に、安い段階で反対意見を受け取る

AI 駆動開発では、ここに構造変化が起きます。

| | 従来 | AI 駆動 |
| --- | --- | --- |
| 設計書の執筆コスト | 高い（数日） | **ほぼゼロ**（数分） |
| 実装コスト | 高い | 低い |
| **ボトルネック** | 執筆と実装 | **判断と検証** |
| 代替案の検討 | 建前になりがち | **実際に 3 案出せる** |
| 設計書の読者 | 人間のみ | **人間 + AI エージェント** |

結論はこうです。

> **doc は「人間が合意するための文書」であると同時に、「AI に渡す最大のコンテキスト入力」である。**

だから本プロセスの design doc は、Google 流の散文構造を保ちながら、
機械可読な front matter・受け入れ条件・エージェント向け制約を併せ持ちます。
そして人間は doc 全文を承認するのではなく、**Decision Points だけを判断します**。

詳しい設計判断は [`docs/design/DD-0001-development-process.md`](docs/design/DD-0001-development-process.md)
（このプロセス自身の design doc）にあります。

---

## 2. 全体像

```
   ┌── G0 ──────┐   ┌── G1 ──────┐   ┌── G2 ──────┐   ┌── G3 ──────┐
   │ 問題を定義 │ → │ 設計に合意 │ → │ 実装を承認 │ → │ 出荷を判断 │
   └────────────┘   └────────────┘   └────────────┘   └────────────┘
     Issue            Design Doc         Pull Request      Release
    (type/*)          (DD-xxxx)          (1 PR = 1 Issue)   (Milestone)
        │                  │                   │                 │
        └──────────────────┴─────── ADR (ADR-xxxx) ──────────────┘
                     「なぜそう決めたか」の永続記録

   AI:    起案・執筆・分解・実装・検証の実行
   人間:  ゲートでの判断（Decision Points / 受け入れ / 出荷可否）
```

GitHub 上での対応物:

| 概念 | GitHub 上の実体 |
| --- | --- |
| 課題・タスク | Issues（`type/*` ラベルで種別） |
| 設計文書 | `docs/design/DD-xxxx-*.md` + 追跡 Issue |
| 意思決定記録 | `docs/adr/ADR-xxxx-*.md` |
| ロードマップ | GitHub Projects（Roadmap ビュー）+ Milestones |
| レビューと合意 | Pull Request（doc も PR でレビューする） |
| 品質ゲート | GitHub Actions |

---

## 3. 最初の一歩

| やりたいこと | 読むもの |
| --- | --- |
| プロセス全体を理解する | [`docs/process/01-lifecycle.md`](docs/process/01-lifecycle.md) |
| 誰が何を決めるのか知る | [`docs/process/02-roles.md`](docs/process/02-roles.md) |
| design doc を書く | [`docs/process/03-design-doc.md`](docs/process/03-design-doc.md) / [テンプレート](docs/templates/design-doc.md) |
| レビューする | [`docs/process/04-review.md`](docs/process/04-review.md) |
| Issue とロードマップを運用する | [`docs/process/05-issues-roadmap.md`](docs/process/05-issues-roadmap.md) |
| AI エージェントを走らせる | [`docs/process/06-agent-protocol.md`](docs/process/06-agent-protocol.md) |
| 完了の定義を確認する | [`docs/process/07-definition-of-done.md`](docs/process/07-definition-of-done.md) |
| 意思決定を記録する | [`docs/process/08-adr.md`](docs/process/08-adr.md) |
| **GitHub 側の設定を済ませる** | [`docs/process/09-setup-checklist.md`](docs/process/09-setup-checklist.md) |

AI エージェント（Claude Code 等）は [`CLAUDE.md`](CLAUDE.md) を常時ルールとして読みます。

---

## 4. 付属ツール

```bash
# 新しい design doc / ADR を採番して作成
python3 scripts/new_doc.py design "アップロードパイプラインの再設計"
python3 scripts/new_doc.py adr    "オブジェクトストレージに S3 を採用する"

# doc の構造検証（CI と同じチェックをローカルで）
python3 scripts/validate_docs.py
```

Claude Code 用スキル（`.claude/skills/`）:

| スキル | 役割 |
| --- | --- |
| `design-doc` | 課題から design doc をドラフトし、代替案と Decision Points を提示する |
| `decompose` | 承認済み design doc を実装 Issue 群に分解して起票する |
| `adr` | 確定した意思決定を ADR として記録する |

---

## 5. 原則（迷ったらここに戻る）

1. **判断は人間、作業は AI。** 人間の時間は判断にだけ使う。
2. **合意は実装より前に。** 手戻りが一番高くつくのは実装後の設計変更。
3. **書かれていない決定は、存在しない。** 会話で決めたことは doc か ADR に落とす。
4. **検証できない完了はない。** 受け入れ条件は必ず検証手段とセットで書く。
5. **doc は生きた資産。** 実装が doc から乖離したら、doc を直す。
6. **すべて GitHub に。** 外部ツールに決定を置かない。リンク切れは知識の消失。
