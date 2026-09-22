# 05. Issue とロードマップ

すべて GitHub で完結させる。外部のチケットツール・スプレッドシート・ドキュメントツールに
**決定や状態を置かない**。リンク切れは知識の消失を意味する。

| 用途 | GitHub 上の実体 |
| --- | --- |
| 作業単位 | **Issues** |
| 設計文書 | `docs/design/DD-xxxx-*.md` + 追跡 Issue |
| 意思決定記録 | `docs/adr/ADR-xxxx-*.md` |
| かんばん / 状態管理 | **Projects (v2)** のボードビュー |
| ロードマップ | **Projects (v2)** のロードマップビュー + **Milestones** |
| 出荷単位 | **Milestones** → **Releases** |
| 議論（結論未確定のもの） | **Discussions**（結論が出たら Issue か ADR にする） |

---

## Issue の粒度

**1 Issue = 1 つの検証可能な成果。** 目安は **半日〜2 日**（AI セッション 1〜3 回）。

| 大きすぎる兆候 | 小さすぎる兆候 |
| --- | --- |
| 受け入れ条件が 5 個を超える | 受け入れ条件が書けない |
| 「〜の改善」「〜の対応」のような曖昧な題 | 1 行の変更で終わる |
| PR が 500 行を超えそう | 単独ではユーザに何の価値も生まない |
| 複数の DD にまたがる | 他 Issue と必ず同時にマージが要る |

大きすぎるなら分割する。小さすぎるなら束ねる。
**分割の軸は「工程」ではなく「価値」**（× 設計 Issue / 実装 Issue / テスト Issue、
○ エンドポイント A / エンドポイント B）。

---

## Issue テンプレート

`.github/ISSUE_TEMPLATE/` に配置済み。

| テンプレート | `type/*` | 用途 |
| --- | --- | --- |
| Design Doc | `type/design-doc` | DD の起案と追跡（doc の PR を紐づける） |
| Feature | `type/feature` | 新機能・機能改善 |
| Bug | `type/bug` | 不具合。再現手順が必須 |
| Task | `type/task` | DD から分解された実装単位、雑務 |
| Spike | `type/spike` | 時間を区切った調査。**成果物は必ず文書** |

---

## ラベル体系

定義は [`.github/labels.yml`](../../.github/labels.yml)。
`main` への push で [`labels.yml` ワークフロー](../../.github/workflows/labels.yml)が GitHub に同期する。

### `type/*` — 何であるか（必須・1 つ）

`design-doc` / `feature` / `bug` / `task` / `spike` / `chore` / `process`

### `priority/*` — いつやるか（必須・1 つ）

| ラベル | 意味 | 期待される反応 |
| --- | --- | --- |
| `priority/p0` | 本番障害・データ損失・セキュリティ | 今すぐ。他を止める |
| `priority/p1` | 現マイルストーンで必ずやる | 今スプリント |
| `priority/p2` | やる。時期は未定 | バックログ上位 |
| `priority/p3` | あればうれしい | いつか |

### `stage/*` — どのゲートにいるか（1 つ）

`g0-problem` / `g1-design` / `g2-build` / `g3-release`

Projects の Status フィールドと対応させる（下記）。

### `agent/*` — AI の自律可否（重要）

| ラベル | 意味 |
| --- | --- |
| `agent/ready` | **AI が自律着手してよい。** 下の DoR を満たしたときだけ付ける |
| `agent/wip` | AI が作業中。二重着手を防ぐ |
| `agent/needs-human` | 人間の判断・作業が必要。AI は着手しない |
| `agent/blocked` | 外部要因で停止中。理由をコメントに書く |

**`agent/ready` の条件（Definition of Ready）**

1. 受け入れ条件が検証可能な形で書かれている
2. 影響範囲（触るファイル・モジュール）が特定されている
3. design doc が必要なら `approved` 済みで、Issue から参照されている
4. 未解決の Decision Point が残っていない

このラベルが、**AI の自律範囲を制御する唯一のスイッチ**である。安易に付けない。

### `risk/*` — 慎重さの度合い

`risk/high`（セキュリティ・課金・データ移行・不可逆操作）/ `risk/medium` / `risk/low`

`risk/high` は **レビュア 2 名必須**、AI 単独でのマージ不可。

### `size/*` — 見積もり（任意）

`xs`(<2h) / `s`(<0.5d) / `m`(<2d) / `l`(<1w) / `xl`(要分割)

`size/xl` は**分割されるまで `agent/ready` を付けてはならない**。

### `area/*` — どこの話か（プロダクト固有）

`area/docs` と `area/ci` のみ雛形として定義済み。
プロダクトの構造が決まった時点で `.github/labels.yml` に追加する。

---

## Projects (v2) の設計

**プロジェクト名**: `windx Roadmap`（リポジトリ横断で 1 つ）

### カスタムフィールド

| フィールド | 型 | 値 | 用途 |
| --- | --- | --- | --- |
| **Status** | 単一選択 | `Inbox` / `Triaged` / `Designing` / `Ready` / `In Progress` / `In Review` / `Done` / `Dropped` | 日々のかんばん |
| **Stage** | 単一選択 | `G0` / `G1` / `G2` / `G3` | ゲート位置（`stage/*` ラベルと対応） |
| **Target** | イテレーション | 2 週間 | いつ着手するか |
| **Milestone** | （組み込み） | — | いつ出すか |
| **Design Doc** | テキスト | `DD-0004` | 由来の doc |
| **Confidence** | 単一選択 | `High` / `Medium` / `Low` | ロードマップの確度。**遠い予定ほど Low** |
| **Size** | 単一選択 | `XS`〜`XL` | 見積もり |

### ビュー

| ビュー名 | 種類 | 用途 |
| --- | --- | --- |
| **Board** | Board（Status 別） | 日々の作業。`agent/wip` の可視化 |
| **Roadmap** | Roadmap（Milestone 軸） | 対外・対内のロードマップ提示 |
| **Triage** | Table（`Status = Inbox`） | G0 の判断待ち |
| **Needs Decision** | Table（`agent/needs-human`） | **人間がやるべきことの一覧。ここが人間のタスクリスト** |
| **Agent Queue** | Table（`agent/ready`、優先度順） | **AI が次に拾う Issue の一覧** |

最後の 2 つが本プロセスの要。
**人間は Needs Decision を、AI は Agent Queue を見る。** 2 つのキューが分離していることが重要。

### 自動化（Projects の組み込みワークフロー）

| トリガ | 動作 |
| --- | --- |
| Issue 作成 | Project に追加、`Status = Inbox` |
| `agent/ready` 付与 | `Status = Ready` |
| PR がその Issue を参照してオープン | `Status = In Review` |
| Issue クローズ | `Status = Done` |

---

## Milestone = ロードマップの時間軸

| 粒度 | 命名 | 意味 |
| --- | --- | --- |
| リリース | `v0.3.0` | 出荷単位。Release と 1:1 |
| 期間 | `2026-Q4` | 四半期の到達目標 |
| 特設 | `hardening-2026-10` | 横断的な取り組み |

- **Milestone の説明欄に「この Milestone で何が達成されるか」を 3 文で書く。** 期日だけの Milestone は意味がない
- 期日に入らない Issue は、**期日を延ばさず Milestone から外す**（スコープを削る）
- Milestone クローズ = G3。Release を作り、リリースノートを AI が生成する

### 対外ロードマップ

Projects の Roadmap ビューを公開する。**Confidence を必ず併記する**。

> 遠い未来を `High` と表示することは、嘘をついていることと同じ。
> 次の Milestone = `High`、その次 = `Medium`、それ以降 = `Low` を既定とする。

---

## トレーサビリティ

すべての作業は次の鎖でつながる。

```
ADR-xxxx  ←─ なぜそう決めたか
   ↑
DD-xxxx   ←─ どう作るか
   ↑
Issue #n  ←─ 何をやるか
   ↑
PR #m     ←─ 実際にやったこと（Closes #n）
```

守るべきリンク規約:

- **Issue → DD**: DD 由来の Issue は本文に `Design doc: DD-xxxx` を書く
- **PR → Issue**: PR 本文に `Closes #n` を書く（1 PR = 1 Issue）
- **PR → DD**: DD 由来なら `Design doc: DD-xxxx` を書く
- **DD → Issue**: doc の front matter `tracking_issue` に追跡 Issue 番号を書く
- **DD → ADR**: 重要な決定は `related_adrs` に列挙

CI（[`docs-lint.yml`](../../.github/workflows/docs-lint.yml)）が
doc 側の front matter と索引の整合を検証する。

---

## トリアージ（週 1 回、30 分）

`Triage` ビュー（`Status = Inbox`）を上から処理する。1 件あたり 2 分以内で判断する。

1. **重複か** → クローズしてリンク
2. **やるか** → やらないなら `Dropped` にして**理由をコメント**（無言クローズ禁止）
3. **`priority/*` を付ける**
4. **DD が要るか** → 要るなら `type/design-doc` の Issue を作って `Stage = G1`
5. **要らないなら** → 受け入れ条件を書き（AI に書かせてよい）、`agent/ready` を付ける

迷って 2 分を超えたら `priority/p3` に置いて次へ進む。**トリアージで設計を始めない。**
