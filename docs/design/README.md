# Design Docs 索引

設計文書（DD）の一覧。書き方の規約は [`docs/process/03-design-doc.md`](../process/03-design-doc.md)。

```bash
python3 scripts/new_doc.py design   "<タイトル>" --slug <english-slug>   # 通常の DD
python3 scripts/new_doc.py onepager "<タイトル>" --slug <english-slug>   # 軽量版
python3 scripts/validate_docs.py                                        # 提出前の検証
```

## 状態

| status | 意味 |
| --- | --- |
| `draft` | 執筆中。レビュー依頼前 |
| `in-review` | レビュー中（PR オープン） |
| `approved` | G1 通過。実装に進んでよい |
| `implemented` | 実装完了・as-built 更新済み |
| `rejected` | 却下（記録として残す。削除しない） |
| `superseded` | 新しい DD に置換 |

## 一覧

| ID | タイトル | status | owner | 更新 |
| --- | --- | --- | --- | --- |
| [DD-0001](DD-0001-development-process.md) | AI 駆動開発プロセスの標準化 | `in-review` | @eastasann | 2026-09-22 |
