# CLAUDE.md — AI エージェント常時ルール

このリポジトリで作業する AI エージェントは、毎セッション本ファイルに従うこと。
プロセスの詳細は `docs/process/` にある。本ファイルはその**実行時の要約**である。

---

## 0. 最優先の 3 原則

1. **判断を勝手にしない。** 設計上の分岐は自分で決めず、**Decision Points として提示**して人間の判断を仰ぐ。
2. **根拠のない主張をしない。** 「動くはず」は禁止。**検証コマンドと実行結果**で語る。
3. **決定は必ず文書に残す。** 会話の中だけで決まったことは、doc または ADR に書くまで**存在しない**。

---

## 1. 着手前チェック

作業を始める前に、必ずこの順で確認する。

1. **対象 Issue はあるか。** なければまず Issue を起こす（`.github/ISSUE_TEMPLATE/`）。
2. **どのゲートにいるか。** `docs/process/01-lifecycle.md` の G0〜G3 のどこか。
3. **design doc が必要か。** 下の判定に従う。
4. **`agent/ready` ラベルがあるか。** ない Issue に対して自律実装を始めない。

### design doc が必要かの判定

次のいずれかに当てはまるなら **design doc（DD）が必要**。

- 複数のコンポーネント/サービスにまたがる
- 公開 API・データスキーマ・永続データの形を変える
- 後から変更するコストが高い（移行が必要になる）
- 妥当な代替案が 2 つ以上あり、選択に判断が要る
- セキュリティ・プライバシー・課金・可用性に影響する
- 見積もりが概ね 3 人日/3 セッションを超える

当てはまらないなら **one-pager**（`docs/templates/one-pager.md`）か、Issue 本文だけで進めてよい。
**迷ったら doc を書く側に倒す**（執筆コストは AI にとって安い）。

---

## 2. 実行ループ

```
Explore → Design → Decide → Decompose → Implement → Verify → Record
 調査     doc起案   人間判断   Issue分解    PR         検証     doc/ADR更新
```

各フェーズの禁止事項:

| フェーズ | やってはいけないこと |
| --- | --- |
| Explore | 既存コードを読まずに設計を書く |
| Design | 代替案を 1 つしか出さない／Decision Points を空にする |
| Decide | 人間の承認前に実装を始める |
| Decompose | 受け入れ条件のない Issue を作る |
| Implement | 1 PR に複数 Issue を詰め込む／doc の範囲外に手を広げる |
| Verify | テストを skip・disable・削除して緑にする |
| Record | 設計と実装が乖離したまま doc を放置する |

---

## 3. 文書の書き方

- **design doc**: `docs/templates/design-doc.md` をコピー。`scripts/new_doc.py design "<title>"` で採番される。
- **ADR**: `docs/templates/adr.md`。`scripts/new_doc.py adr "<title>"`。
- front matter の必須キーと見出しは `scripts/validate_docs.py` が検証する。**書いたら必ずローカルで実行**する。

```bash
python3 scripts/validate_docs.py
```

### 代替案（Alternatives Considered）の書き方

AI にとって執筆は安い。**必ず実行可能な代替案を 2〜3 案**出し、各案について書く。

- どう動くか（1 段落）
- 採用した場合に何を失うか（トレードオフ）
- **却下理由**（「複雑だから」は理由にならない。何がどう複雑で、誰がそのコストを払うのかを書く）

### Decision Points の書き方

人間に判断してほしい点だけを列挙する。各項目に必ず含めるもの:

- 選択肢（2 つ以上）
- **AI の推奨と、その根拠**
- **この判断が後から覆るときのコスト**（安いなら「推奨で進めて後で直す」と明記してよい）

Decision Points が空の doc は、レビュー依頼を出してはならない。

---

## 4. Issue とロードマップ

- 1 Issue = 1 つの検証可能な成果。半日〜2 日相当に分解する。
- 必須ラベル: `type/*`, `priority/*`。実装可能なら `agent/ready` を付ける。
- design doc から分解した Issue は、本文に **`Design doc: DD-xxxx`** を必ず書く。
- ロードマップは Milestone（時間軸）+ Projects の Status/Stage フィールドで表す。
  詳細は `docs/process/05-issues-roadmap.md`。

---

## 5. Pull Request

- **1 PR = 1 Issue**。PR 本文に `Closes #<issue>` を書く。
- design doc 由来なら `Design doc: DD-xxxx` も書く。
- `.github/pull_request_template.md` のチェック項目は消さずに埋める。
- **push 前に必ず**、リポジトリの lint / typecheck / テストをローカルで実行し、**結果を PR 本文に貼る**。
- CI が赤いまま「レビュー待ち」にしない。赤は自分の仕事。

---

## 6. 検証の作法

- 受け入れ条件は **Given / When / Then** で書き、**それを確かめるコマンド**を併記する。
- バグ修正では、**先に失敗するテストを書いて再現**させ、その後に直す。
- 「フレーキーだから」は根本原因ではない。再実行は原則 1 回まで。
- テストの skip / disable / 削除で緑にすることは、いかなる理由でも禁止。

---

## 7. やってはいけないこと（ハードルール）

- 人間の承認（G1）前に、design doc が必要な変更の実装を始める
- Decision Points を自分で決めて doc に「決定済み」と書く
- doc に書かれていない範囲へ実装を広げる（スコープクリープ）
- 秘密情報（トークン、鍵、内部ホスト名）を doc・Issue・PR に書く
- 決定の根拠を GitHub 外（チャット等）にだけ残す
