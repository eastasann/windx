# プロセス標準

| # | 文書 | 何が書いてあるか |
| --- | --- | --- |
| 01 | [ライフサイクルと 4 つのゲート](01-lifecycle.md) | 着想から出荷までの流れ、人間が判断する 4 地点 |
| 02 | [役割分担](02-roles.md) | 人間と AI の責務（RACI）、レビュアの決め方 |
| 03 | [design doc 運用規約](03-design-doc.md) | いつ書くか、何を書くか、状態遷移、AI 向け拡張 |
| 04 | [レビュー規約](04-review.md) | doc レビューと code レビュー、SLA、反対意見の扱い |
| 05 | [Issue とロードマップ](05-issues-roadmap.md) | ラベル体系、Projects 設計、Milestone 運用 |
| 06 | [エージェント実行プロトコル](06-agent-protocol.md) | AI の実行ループ、セッション設計、自律範囲 |
| 07 | [完了の定義](07-definition-of-done.md) | DoR / DoD、品質ゲート |
| 08 | [ADR 運用規約](08-adr.md) | 意思決定記録の書き方と棄却・置換 |
| 09 | [導入チェックリスト](09-setup-checklist.md) | 人間が GitHub 上で行う設定（Projects、ブランチ保護ほか） |

## 1 枚要約

```
G0 問題定義 ──→ G1 設計合意 ──→ G2 実装承認 ──→ G3 出荷判断
  Issue          Design Doc       Pull Request      Release
```

- **AI がやること**: 調査・執筆・分解・実装・検証・記録
- **人間がやること**: ゲートでの判断だけ（Decision Points、受け入れ、出荷可否）
- **記録の置き場所**: 全部 GitHub（Issues / PR / `docs/` / Projects / Milestones）

## 変更のしかた

本プロセス自体もプロセスに従う。変更したい場合:

1. `type/process` ラベルで Issue を立てる
2. 影響が大きいなら design doc を書く（このプロセス自身は `DD-0001`）
3. PR でレビューし、確定した判断は ADR に残す
