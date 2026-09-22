# 03. design doc 運用規約

## Google の design doc から引き継ぐもの / 変えるもの

| | Google の design doc | 本プロセス | 理由 |
| --- | --- | --- | --- |
| 形式 | 散文（箇条書きの羅列を避ける） | **継承** | 散文でしか書けない曖昧さの検出機能がある |
| Goals / Non-goals | 必須 | **継承・強化** | Non-goals は AI のスコープクリープ抑止に直接効く |
| Alternatives Considered | 必須（形骸化しがち） | **強化** | AI なら実際に 3 案書ける。建前をやめる |
| Cross-cutting concerns | 必須 | **継承** | セキュリティ / プライバシー / 可観測性 / コスト |
| 長さ | 3〜10 ページ | **1〜5 ページ + 付録** | 人間が読む本体は短く。詳細は付録に追い出す |
| 読者 | 人間のみ | **人間 + AI** | ← 最大の違い |
| 承認 | doc 全体を承認 | **Decision Points を判断** | 人間の判断コストを分岐点に集中させる |
| 機械可読性 | なし | **front matter 必須** | 追跡・検証・自動化のため |
| 保管先 | 社内文書ツール | **リポジトリ内 Markdown** | コードと同じ PR でレビュー、同じ履歴に残る |

---

## いつ書くか

次のいずれかなら **design doc（DD）を書く**。

- 複数のコンポーネント/サービスにまたがる
- 公開 API・データスキーマ・永続データの形を変える
- 後から変更するコストが高い（移行が必要になる）
- 妥当な代替案が 2 つ以上あり、選択に判断が要る
- セキュリティ・プライバシー・課金・可用性に影響する
- 見積もりが概ね 3 人日 / 3 セッションを超える

いずれにも当たらないなら:

| 規模 | 使うもの |
| --- | --- |
| 中（1〜3 日、選択肢はあるが軽い） | [one-pager](../templates/one-pager.md) — `docs/design/` に置くが front matter は簡略 |
| 小（半日以内、設計判断なし） | Issue 本文のみ |

**迷ったら書く側に倒す。** AI にとって執筆コストは安く、書かなかったことによる手戻りは高い。

---

## 構成

テンプレート: [`docs/templates/design-doc.md`](../templates/design-doc.md)

```
front matter        ← 機械可読なメタデータ（CI が検証）
## Summary          ← 3 文以内。これだけ読めば何をするか分かる
## Context          ← 今どうなっていて、何が問題か（散文）
## Goals            ← 達成すること（検証可能な形で）
## Non-Goals        ← やらないこと ★AI のスコープ境界として機能する
## Decision Points  ← ★人間が判断する点。ここがレビューの本体
## Design           ← 設計本体（散文 + 図 + インターフェース）
## Alternatives Considered  ← 実行可能な代替案 2〜3 案と却下理由
## Cross-cutting Concerns   ← セキュリティ / プライバシー / 可観測性 / コスト / 運用
## Acceptance Criteria      ← ★検証可能な受け入れ条件（Given/When/Then + 検証手段）
## Implementation Plan      ← Issue 分解案
## Context for Agents       ← ★AI 向けの制約（触る場所、踏襲パターン、禁止事項）
## Open Questions           ← 未解決の疑問
## Appendix                 ← 詳細データ、計測結果、長い調査ログ
```

★ = 本プロセス独自の拡張。

---

## 独自拡張 3 つの意図

### ★ Decision Points — 人間の判断を分岐点に集中させる

doc 全体を承認させると、人間は全文を読むことになる。これはスケールしない。
代わりに「**判断が必要な点だけ**」を切り出して先頭近くに置く。

各 Decision Point に必ず書くもの:

- **選択肢**（2 つ以上。「やる / やらない」も立派な 2 択）
- **AI の推奨と根拠**（推奨を出さずに丸投げしない）
- **覆すコスト** — 後から変更するのがどれだけ高いか

覆すコストが安い判断は、`[推奨で進行・事後変更可]` と明記して人間の判断を省略してよい。
**判断コストは、覆すコストに見合わせる。**

```markdown
### DP-1: セッション保存先

- **選択肢 A**: Redis（推奨）— 既存の Redis クラスタを流用でき、追加運用コストがない
- **選択肢 B**: RDB のテーブル — 運用対象は増えないが、書き込み頻度がボトルネックになる見込み
- **AI の推奨**: A。現行のピーク書き込みは 1,200 req/s で、B では既存 DB の余力を超える（付録 A-2 参照）
- **覆すコスト**: 中。保存先の抽象化層を挟むので差し替えは可能だが、移行にダウンタイムが要る
```

### ★ Acceptance Criteria — 検証可能性を設計の一部にする

AI は「それらしく動くもの」を高速に作れる。だから品質の担保は**検証可能性**に移る。
受け入れ条件は必ず **Given / When / Then** + **検証手段**で書く。

```markdown
- **AC-1**: Given 有効期限切れのセッション, When API を呼ぶ, Then 401 を返し、監査ログに 1 行残る
  - 検証: `pytest tests/auth/test_session_expiry.py`
```

検証手段が書けない受け入れ条件は、受け入れ条件ではない。**書き直すか、Open Questions に落とす。**

### ★ Context for Agents — AI の探索を設計で制約する

AI は探索範囲が広すぎると、既存パターンを無視した実装をする。doc で先に縛る。

```markdown
## Context for Agents
- 触ってよい場所: `src/auth/**`, `tests/auth/**`
- 触ってはいけない場所: `src/billing/**`（別 doc DD-0007 で改修中）
- 踏襲するパターン: `src/auth/token.py` のリポジトリパターンに合わせる
- 使ってよいライブラリ: 既存の依存のみ。新規追加は Decision Point として提示すること
- 既知の落とし穴: `SessionStore.get()` はキャッシュを見るため、テストでは `flush()` が要る
```

---

## 状態遷移

front matter の `status` は次のいずれか。

```
draft ──→ in-review ──→ approved ──→ implemented
  │           │                          │
  │           └──→ rejected              └──→ superseded (別 DD に置換)
  └──────────────→ rejected
```

| status | 意味 | 誰が遷移させるか |
| --- | --- | --- |
| `draft` | 執筆中。レビュー依頼前 | Agent |
| `in-review` | レビュー中（PR がオープン） | Agent（PR を上げたとき） |
| `approved` | G1 通過。実装に進んでよい | **Owner のみ** |
| `implemented` | 実装完了・マージ済み。as-built に更新済み | Agent（実装 PR で） |
| `rejected` | 却下。**doc は消さず残す**（同じ議論の再発を防ぐ） | Owner |
| `superseded` | 新しい DD に置き換えられた。`superseded_by` に後継 ID | Owner |

**却下された doc を削除してはならない。** 「なぜやらなかったか」は「なぜやったか」と同じ価値がある。

---

## 番号と置き場所

```bash
python3 scripts/new_doc.py design "セッション保存先の変更"
# → docs/design/DD-0004-session-store.md を作成（番号は自動採番）
```

- ID: `DD-0001` 形式（4 桁ゼロ埋め、再利用しない）
- ファイル名: `DD-<番号>-<英小文字ケバブの短い要約>.md`
- 索引: [`docs/design/README.md`](../design/README.md)（`scripts/validate_docs.py` が整合を検証）

---

## レビューのかけ方

1. design doc を**単独の PR** で出す（実装は含めない）
2. PR タイトル: `docs(design): DD-xxxx <title>`
3. PR 本文の冒頭に **Decision Points を転記**する（レビュアが GitHub 上で議論できるように）
4. 各 Decision Point は PR コメントのスレッドで議論する
5. すべて解決したら Owner が `status: approved` にして自らマージする

詳細は [04-review.md](04-review.md)。

---

## 実装後の as-built 更新

**doc は「書いて終わる仕様書」ではなく「維持する資産」である。**

実装 PR をマージする際、同じ PR で doc を更新する。

- `status` を `implemented` に
- `Design` 節の記述が実装と食い違っていれば直す
- 実装中に判明した制約を `Cross-cutting Concerns` か `Appendix` に追記
- 設計方針そのものが変わったなら、doc を直すのではなく **新しい DD を書いて `superseded`**

更新されない doc は、半年後に**嘘をつくドキュメント**になる。
AI はそれを正しい前提として読むので、害は人間が読む場合より大きい。
