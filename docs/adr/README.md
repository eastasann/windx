# ADR 索引

意思決定記録（ADR）の一覧。書き方の規約は [`docs/process/08-adr.md`](../process/08-adr.md)。

```bash
python3 scripts/new_doc.py adr "<決定を能動態で>" --slug <english-slug>
python3 scripts/validate_docs.py
```

**ADR は accepted 後に書き換えない。** 決定が変わったら新しい ADR を書き、
旧 ADR を `superseded` にする（`status` と `superseded_by` の 2 行だけが許される編集）。

## 状態

| status | 意味 |
| --- | --- |
| `proposed` | 提案中（PR レビュー中） |
| `accepted` | 採用。現行の方針 |
| `rejected` | 却下（記録として残す） |
| `superseded` | 新 ADR に置換（`superseded_by` を参照） |
| `deprecated` | 前提が消滅した |

## 一覧

| ID | タイトル | status | 日付 |
| --- | --- | --- | --- |
| [ADR-0001](ADR-0001-github-as-single-source-of-truth.md) | GitHub を単一の真実とし、外部ツールに決定を置かない | `proposed` | 2026-09-22 |
| [ADR-0002](ADR-0002-design-doc-as-agent-context.md) | design doc を AI エージェントへのコンテキスト入力として構造化する | `proposed` | 2026-09-22 |
| [ADR-0003](ADR-0003-human-gates-at-decision-points.md) | 人間のレビューを doc 全体ではなく Decision Points に限定する | `proposed` | 2026-09-22 |
