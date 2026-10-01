# 09. 導入チェックリスト

リポジトリに取り込んだ後、**人間が GitHub 上で行う設定**の一覧。
コードで表現できない部分（Projects の作成、ブランチ保護など）だけを扱う。

---

## 1. ラベルを同期する（自動／手動どちらでも）

`main` に取り込まれた時点で [`labels` ワークフロー](../../.github/workflows/labels.yml)が走り、
[`.github/labels.yml`](../../.github/labels.yml) の 33 ラベルが作成される。

手動で流す場合:

```bash
gh workflow run labels.yml          # Actions から実行
# または手元から
GH_REPO=eastasann/windx python3 scripts/sync_labels.py
```

- [ ] ラベルが GitHub 上に存在する（`gh label list`）
- [ ] 既定の `bug` / `enhancement` など不要なラベルを削除する
      （`scripts/sync_labels.py --prune` で一括削除できる。**既存 Issue から外れるので取り込み直後に行う**）

---

## 2. GitHub Projects (v2) を作る

設計は [05-issues-roadmap.md](05-issues-roadmap.md)。
**DP-5 の決定により、フィールド設定とビューの同期はコード化する**
（[DD-0001 DP-5](../design/DD-0001-development-process.md#decision-points) / 実装は未着手）。
ただし次の 2 つは Owner の手作業として残る。

### 2-1. classic PAT を登録する（**コード化の前提条件**）

`eastasann/windx` は個人アカウントなので Project は user-owned になり、
**`GITHUB_TOKEN` では Projects v2 を操作できない**。
fine-grained PAT も個人アカウントの Projects 権限を取得できないため、classic PAT が必要。

- [ ] classic PAT を作成する（スコープ: **`project`** と `repo`）
- [ ] 有効期限を **90 日以内**にする（更新を運用に組み込む）
- [ ] リポジトリシークレット **`PROJECTS_TOKEN`** として登録する
- [ ] このトークンを Projects 操作以外に流用しない

> `project` スコープは絞り込めず、`repo` と併せると当該ユーザがアクセスできる
> 全リポジトリに及ぶ。Project を Organization 所有に移せる時点で移し、
> `GITHUB_TOKEN` 運用へ切り替えることが望ましい（DD-0001 の Cross-cutting Concerns 参照）。

### 2-2. Project 本体を作る（初回のみ手作業）

- [ ] プロジェクト `windx Roadmap` を作成する
- [ ] 作成後、フィールドとビューの設定はコード化された同期で行う
      （未実装のうちは下表を GUI で設定する）

- [ ] カスタムフィールドを追加する

| フィールド | 型 | 値 |
| --- | --- | --- |
| Status | 単一選択 | `Inbox` / `Triaged` / `Designing` / `Ready` / `In Progress` / `In Review` / `Done` / `Dropped` |
| Stage | 単一選択 | `G0` / `G1` / `G2` / `G3` |
| Target | イテレーション | 2 週間 |
| Design Doc | テキスト | — |
| Confidence | 単一選択 | `High` / `Medium` / `Low` |
| Size | 単一選択 | `XS` / `S` / `M` / `L` / `XL` |

- [ ] ビューを作る

| ビュー | 種類 | フィルタ |
| --- | --- | --- |
| Board | Board（Status 別） | — |
| Roadmap | Roadmap（Milestone 軸） | — |
| Triage | Table | `Status = Inbox` |
| **Needs Decision** | Table | `label:agent/needs-human` |
| **Agent Queue** | Table | `label:agent/ready`、優先度順 |

- [ ] 自動化を設定する（**暫定: 組み込みワークフロー / 将来: コード化**）
  - Issue 作成 → Project に追加、`Status = Inbox`
  - Issue クローズ → `Status = Done`
  - PR がリンクされたらオープン → `Status = In Review`
  - `agent/ready` 付与 → `Status = Ready`（`Agent Queue` に現れる）

> DP-5=B の決定により、最終的にこれらは `.github/workflows/project-sync.yml` と
> `scripts/project_sync.py` に移す（DD-0001 Implementation Plan #10、未着手）。
> 実装までは組み込みワークフローで運用し、**設定内容をここに書き残しておく**
> （コード化時の仕様になる）。

> **Needs Decision と Agent Queue の分離が本プロセスの要**。
> 人間は前者だけを見て、AI は後者だけを拾う。

---

## 3. 最初の Milestone を作る

- [ ] Milestone を 1 つ作る（例 `v0.1.0` または `2026-Q4`）
- [ ] **説明欄に「この Milestone で何が達成されるか」を 3 文で書く**
      （期日だけの Milestone は意味がない）

---

## 4. ブランチ保護を設定する

`main` に対して:

- [ ] PR 経由のみマージ可能にする
- [ ] ステータスチェックを必須にする: `docs-lint`, `pr-checks`
- [ ] レビュー承認を 1 件以上必須にする
- [ ] マージ後にブランチを自動削除する

> `risk/high` の「レビュア 2 名」は GitHub の設定では表現しきれないため、
> [04-review.md](04-review.md) の運用規約として扱う。

---

## 5. Discussions を有効にする

- [ ] Discussions を有効にする（Issue テンプレートの `config.yml` から導線が張ってある）

「まだやるかどうか決まっていない話」の置き場。結論が出たら Issue か ADR に落とす。

---

## 6. DD-0001 の Decision Points に回答する

- [ ] [`DD-0001`](../design/DD-0001-development-process.md) の DP-1〜DP-5 に回答する
- [ ] `reviewers` を設定し、`status: approved` にする
- [ ] [`ADR-0001`](../adr/ADR-0001-github-as-single-source-of-truth.md) 〜
      [`ADR-0003`](../adr/ADR-0003-human-gates-at-decision-points.md) を `accepted` にする
- [ ] 回答内容に合わせてプロセス文書を更新する（言語方針、閾値など）

**この回答をもって、プロセスが正式に発効する。**
それまでは `in-review` / `proposed` のまま = まだ合意されていない状態である。

---

## 7. 動作確認

```bash
python3 scripts/validate_docs.py      # doc の構造検証
python3 scripts/check_links.py        # リンク切れ検出
python3 scripts/sync_labels.py --dry-run
PR_BODY="Closes #1
Design doc: 不要（動作確認）" python3 scripts/check_pr.py
```

- [ ] 上記 4 つがすべて成功する
- [ ] 最初の PR で `docs-lint` と `pr-checks` が緑になる

---

## 8. プロダクトコードが入ったときに追加すること

- [ ] lint / format / typecheck / unit test を CI に追加する
- [ ] 秘密情報スキャンと依存脆弱性スキャンを追加する
- [ ] `area/*` ラベルをプロダクトの構造に合わせて定義する
- [ ] `CLAUDE.md` にビルド・テストの実行コマンドを追記する
- [ ] AI レビューを CI に組み込む（**人間のゲートの代替にはしない**）
