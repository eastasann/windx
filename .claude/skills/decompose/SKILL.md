---
name: decompose
description: 承認済みの design doc を実装 Issue 群に分解して起票する。「DD を Issue に分解して」「この設計の実装タスクを切って」「Issue を作って」と言われたとき、または design doc が approved になって実装に進むときに使う。
---

# design doc を Issue に分解する

規約: `docs/process/05-issues-roadmap.md`, `docs/process/07-definition-of-done.md`

---

## 前提条件（**満たさないなら分解しない**）

```bash
grep -E '^(id|status|owner|tracking_issue):' docs/design/DD-xxxx-*.md
python3 scripts/validate_docs.py
```

- `status: approved` であること。`draft` / `in-review` の doc を分解しない
- **未決の Decision Point が残っていないこと**（`validate_docs.py` が検証する）

満たさないなら、分解せずに「まだ G1 を通っていない」と報告する。

---

## 分解の原則

### 粒度

**1 Issue = 1 つの検証可能な成果。** 目安は半日〜2 日（AI セッション 1〜3 回）。

| 大きすぎる兆候 | 小さすぎる兆候 |
| --- | --- |
| 受け入れ条件が 5 個を超える | 受け入れ条件が書けない |
| 題が「〜の改善」「〜の対応」 | 1 行の変更で終わる |
| PR が 500 行を超えそう | 単独では価値を生まない |

### 分割の軸は「工程」ではなく「価値」

- ❌ 設計 Issue → 実装 Issue → テスト Issue
- ✅ エンドポイント A → エンドポイント B → 移行スクリプト

**テストを別 Issue に切らない。** テストは各 Issue の完了条件に含まれる。

### 依存

依存がある Issue は本文に `Depends on #n` を書き、**直列に実行する**。
並列にできる単位を増やすほど全体は速くなるが、依存を無視すると手戻りが増える。

---

## 各 Issue に必ず書くもの

```markdown
Design doc: DD-xxxx

## やること
<1〜3 文。「〜を実装する」と言い切れる粒度で>

## 受け入れ条件
- **AC-1**: Given <前提>, When <操作>, Then <期待結果>
  - 検証: `<コマンド>`

## 影響範囲
- 触ってよい場所: <doc の Context for Agents から転記>
- 触ってはいけない場所:
- 踏襲するパターン:

Depends on #<n>   <!-- あれば -->
```

**受け入れ条件は doc の AC から引き写す。** 新しく発明しない。
doc に書かれていない AC が必要になったなら、それは doc の不足なので
doc に追記するか Decision Point として提示する。

---

## ラベル

| ラベル | 付け方 |
| --- | --- |
| `type/task` | 必須 |
| `priority/*` | doc の優先度を引き継ぐ。不明なら `priority/p2` |
| `stage/g2-build` | 実装段階 |
| `size/*` | 見積もり。`size/xl` なら**さらに分割する** |
| `risk/high` | セキュリティ・課金・データ移行・不可逆操作を含むとき |
| **`agent/ready`** | **付けない。人間が付ける** |

### `agent/ready` を自分で付けてはならない

これは AI の自律実行を開く唯一のスイッチであり、**人間が開ける**。
自分で付けると「曖昧な Issue を自分で ready にして自分の解釈で実装する」閉ループになる。

代わりに、**Definition of Ready を満たす状態まで Issue を整えて**、
人間に「このラベルを付けてよいか」を確認する。

---

## 起票の手順

1. doc の `Implementation Plan` を出発点にする（そのまま使えるとは限らない）
2. 各項目を上の形式の Issue 本文に展開する
3. GitHub に起票する（`mcp__github__issue_write`、または `gh issue create`）
4. **doc の front matter `tracking_issue`** に親 Issue 番号を設定する
5. 起票した Issue 番号を doc の `Implementation Plan` 表に追記する
6. 依存関係が正しいか、番号が確定してから見直す

---

## 完了報告に必ず含めること

1. 起票した Issue の一覧（番号・タイトル・規模・依存）
2. 実行順序（直列にすべき箇所を明示）
3. **`agent/ready` を付けてよいか人間に確認する旨**
4. doc から読み取れず、補完で埋めた箇所（あれば doc 側の不足として報告）

---

## やってはいけないこと

- `approved` でない doc を分解する
- `agent/ready` を自分で付ける
- 受け入れ条件のない Issue を作る
- doc に書かれていない作業を Issue にする（スコープの拡大）
- テストを独立した Issue に切り出す
- 分解と同時に実装を始める
