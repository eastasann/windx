---
id: DD-0000
title: "<短いタイトル>"
type: one-pager
status: draft
owner: "@<github-handle>"
reviewers: []
created: 0000-00-00
updated: 0000-00-00
tracking_issue: null
related_adrs: []
supersedes: []
superseded_by: null
---

<!--
one-pager は「設計判断はあるが軽い」変更（1〜3 日規模）向けの簡易版。
使い方:  python3 scripts/new_doc.py onepager "<タイトル>"
規約:    docs/process/03-design-doc.md

これより大きい / 複数コンポーネントにまたがる / 後戻りが高い なら
design-doc テンプレートを使うこと。書いている途中で「収まらない」と感じたら、
迷わず design doc に昇格させる（type を design-doc に変えて不足節を足す）。
-->

## Summary

<!-- 3 文以内。何をするか。 -->

## Context

<!-- 今どうなっていて、何が問題か。1〜2 段落。 -->

## Non-Goals

<!-- ★ 短い doc でもここは省略しない。AI のスコープ境界になる。 -->

-

## Decision Points

<!--
★ 判断が必要な点。本当に 1 つもないなら「なし（自明な変更のため）」と書く。
-->

### DP-1: <判断すべきこと>

- **選択肢 A / B**:
- **AI の推奨**: <どちらか> — <根拠>
- **覆すコスト**: <低 / 中 / 高>
- **決定**:

## Design

<!-- どう作るか。1〜3 段落 + 必要なら簡単な図やインターフェース。 -->

## Alternatives Considered

- **<案 A>**: <却下理由>
- **何もしない**: <却下理由>

## Acceptance Criteria

- **AC-1**: Given <前提>, When <操作>, Then <期待結果>
  - 検証: `<コマンド>`

## Context for Agents

- **触ってよい場所**:
- **踏襲するパターン**:
- **既知の落とし穴**:
