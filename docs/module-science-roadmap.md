# モジュール科学ロードマップ — チーム提示資料

> EISを「人の間接観測」から「構造の直接測定」に進化させる

## Why — なぜやるのか

EISは現在、git履歴から**人のスコア**を算出し、そこからチーム構造を推測している。

```
git history → 人のスコア → チーム構造の推測（間接観測）
```

しかしgit履歴には、まだ抽出していない**構造情報**が大量に眠っている。
これを直接測定に転換することで、EISは「エンジニア評価ツール」から「**Engineering Risk Detector**」に進化できる。

```
git history → モジュールの構造測定（直接観測）→ リスク検出・予測
```

### ビジネス上の意義

- **採用・退職リスクの定量化**: 「この人が抜けると3つのモジュールがDead Zoneになる」
- **アーキテクチャ改善の根拠**: 「このモジュール境界は漏れている」を数字で示せる
- **Conway's Lawの検証**: チーム構造とコード構造のミスマッチを検出
- **ace-orbit（SaaS版）への差別化要素**: 他ツールにないモジュール分析

---

## What — 何をやるか

### 全体像

| Phase | テーマ | 入力 | 出力 |
|-------|--------|------|------|
| 1 | モジュール直接測定 | git log + blame | ChangePressure, Co-change, Ownership |
| 2 | モジュールスコアリング | Phase 1メトリクス | モジュールアーキタイプ |
| 3 | Conway's Law検証 | 人 × モジュール | 構造ミスマッチ検出 |
| 4 | 予測と処方箋 | 時系列データ | リスク予測・改善提案 |

**全フェーズgit履歴のみ。外部API・AI不要。**

---

## Phase 1：モジュールレベルの直接測定

### 既に実装済み ✅

| メトリクス | ファイル | 状態 |
|-----------|---------|------|
| **ChangePressure** | `internal/metric/changepressure.go` | 実装済み・動作中 |
| **ModuleOf()** | 同上 | ファイルパス→モジュール変換 |
| **ModuleRisk** | `internal/metric/indispensability.go` | バスファクター検出 |
| **Robust/Dormant Survival** | `internal/metric/survival.go` | 変更圧による生存分離 |
| **PressureMode** | `internal/cli/analyze.go` | CLIフラグ (`--pressure include`) |

ChangePressure（`commits_touching_module / blame_lines`）は既に本番稼働しており、
Survival分析のRobust/Dormant分離やArchetype分類（Architect, Resilient, Fragile）にも組み込まれている。

### 新規実装が必要 🔧

#### 1. Co-change Coupling（同時変更分析）

```
同一コミットでファイルXとファイルYが変更された回数を集計
→ モジュール間の暗黙結合を検出
```

- git logから抽出可能（新データソース不要）
- 実質的に**Design Structure Matrix（DSM）** の自動生成
  - Baldwin & Clark（Harvard）が提唱したモジュール性定量化フレームワーク
  - 学術理論との直接的な橋になる
- 実装見込み: `internal/metric/cochange.go`

#### 2. Ownership Fragmentation（所有分散度）

```
モジュール単位で「何人が触っているか」「所有が分散しているか」を測定
→ 現在のIndispensability（人単位）をモジュール単位に反転
```

- 既存のblameデータから算出可能
- 実装見込み: `internal/metric/indispensability.go` を拡張

---

## Phase 2：モジュールスコアリング

Phase 1のメトリクスを組み合わせて、**モジュール単位のアーキタイプ**を定義する。

| 指標 | 何を測るか |
|------|-----------|
| Boundary Integrity | 境界をまたぐco-changeの少なさ |
| Change Absorption | ChangePressureに対するSurvivalの比率 |
| Knowledge Distribution | 所有の適切な分散度 |
| Stability | 変更頻度の時系列安定性 |

### モジュールアーキタイプ（案）

| アーキタイプ | 特徴 | アクション |
|-------------|------|-----------|
| **Stable Core** | 変更少、Survival高、所有分散 | 良い設計。維持 |
| **Turbulent Edge** | 変更多、Survival低 | 境界の見直しが必要 |
| **Dead Zone** | 変更ゼロ、所有者退職済み | Fragile Fortressの構造版 |
| **Coupling Magnet** | co-changeの集中点 | 隠れた依存の中心 |

---

## Phase 3：Conway's Law検証

EISは**人のアーキタイプ**を既に持っている。Phase 2で**モジュールのアーキタイプ**が得られる。

この2つを重ね合わせることで：

- Architectがいるモジュールは本当にStable Coreか？
- Producer Vacuumのチームのモジュールは本当にTurbulent Edgeか？
- Former検出されたモジュールはDead Zoneに向かっているか？

**Conway's Lawの定量的検証**——「チーム構造がシステム構造を規定する」をgit履歴から数字で示す。

---

## Phase 4：予測と処方箋

時系列データから未来を推測する。

- ChangePressureが3ヶ月連続上昇 → 境界分割を推奨
- 特定の人が抜けると複数モジュールが同時にDead Zone化 → 構造版Bus Factor警告
- co-changeパターンとバグ集中領域の一致 → リスク予測

---

## 技術的実現可能性

| 観点 | 評価 |
|------|------|
| データソース | git log + git blameのみ（追加不要） |
| Phase 1の土台 | ChangePressure / ModuleRisk / Robust-Dormant分離 — 実装済み |
| 言語・依存 | Go + 最小構成（fatih/color, rodaine/table, gopkg.in/yaml.v3） |
| 学術的根拠 | DSM（Design Structure Matrix）理論に直結 |
| 追加コスト | git blameのworker poolは既存。co-change分析はgit logパースの拡張 |

### 注意点

- co-change分析のコミット数が大きいリポジトリではメモリ使用量に注意
- モジュール定義（`ModuleOf()`の粒度）がPhase 2以降の品質を左右する
- Phase 3以降はace-orbit（SaaS版）との統合を見据えた設計が必要

---

## 進め方の提案

1. **Phase 1完了** → co-change coupling + ownership fragmentation の実装
2. Phase 1の結果をOSSリポジトリで検証（既にscala3等で実験中）
3. Phase 2のモジュールアーキタイプを設計・実装
4. Phase 3-4はace-orbit側との統合を含めて判断

Phase 1は既存コードベースの自然な拡張であり、リスクは小さい。
