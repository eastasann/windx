---
id: ADR-0000
title: "<決定そのものを能動態で>"
status: proposed
date: 0000-00-00
deciders: ["@<github-handle>"]
related_docs: []
supersedes: []
superseded_by: null
---

<!--
使い方:
  python3 scripts/new_doc.py adr "<タイトル>"
書き方の規約: docs/process/08-adr.md

原則:
- タイトルは決定そのもの（「〜について」ではなく「〜を採用する」）
- 1 ページを超えたら、それは design doc である
- accepted 後は書き換えない。覆すときは新しい ADR を書いて superseded にする
-->

## Context

<!--
どういう状況で、何を決める必要があったか。2〜3 段落。
制約（期限、人員、既存システム、法令）があれば書く。
-->

## Decision

<!--
何を決めたか。能動態・断定形で 1〜3 文。
❌「Redis がよいと思われる」 → ✅「セッションは Redis に保存する」
-->

## Consequences

### 良い結果

-

### 悪い結果 / 引き受けたコスト

<!-- ★ 必ず 2 つ以上書く。トレードオフのない決定は存在しない。 -->

-
-

### この決定を見直すべき兆候

<!-- 将来この ADR を superseded にすべきシグナル。観測可能な形で。 -->

-

## Alternatives Considered

<!-- 1 案 2〜3 行で簡潔に。詳細は関連 design doc に譲る。 -->

- **<案 A>**: <却下理由>
- **<案 B>**: <却下理由>
