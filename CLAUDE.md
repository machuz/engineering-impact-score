# Engineering Impact Score (EIS) — Claude Code Guide

## 言語ガイドライン

- ユーザーとのコミュニケーションは常に日本語で行う
- コード・コミットメッセージは英語

## プロジェクト概要

Git履歴のみからエンジニアの実質的なインパクトを定量化するCLIツール。
外部API・AIトークン不要。`git log` と `git blame` だけで7軸スコアリング + アーキタイプ分類を行う。

- **言語**: Go 1.25.0
- **依存**: fatih/color, rodaine/table, gopkg.in/yaml.v3（最小構成）
- **配布**: GitHub Releases + Homebrew (`brew install machuz/tap/eis`)

## ディレクトリ構造

```
cmd/eis/main.go                        # エントリポイント
internal/
├── cli/
│   ├── root.go                        # コマンドディスパッチ & help
│   └── analyze.go                     # 分析オーケストレーション
├── config/config.go                   # YAML設定パース & バリデーション
├── domain/detect.go                   # ドメイン自動検出 (BE/FE/Infra/FW)
├── git/
│   ├── runner.go                      # git コマンド実行ラッパー
│   ├── log.go                         # git log --numstat パーサー
│   └── blame.go                       # git blame パーサー + worker pool
├── metric/
│   ├── metric.go                      # RawScores構造体
│   ├── production.go                  # 変更行数
│   ├── quality.go                     # fix率 (100 - fix%)
│   ├── survival.go                    # 時間減衰blame (exp(-days/tau))
│   ├── design.go                      # アーキテクチャファイル貢献
│   ├── debt.go                        # 負債清掃率
│   └── indispensability.go            # バスファクター（モジュール所有率）
├── scorer/
│   ├── scorer.go                      # スコア計算 & 重み付け
│   ├── normalize.go                   # 正規化
│   └── archetype.go                   # アーキタイプ分類（confidence付き）
└── output/
    ├── table.go                       # カラーテーブル出力
    ├── json.go                        # JSON出力
    └── csv.go                         # CSV出力
```

## 7軸スコアリング

| 軸 | 重み | 正規化 | 概要 |
|---|---|---|---|
| Production | 15% | 絶対値（日次変更量/基準値） | 変更量 |
| Quality | 10% | 絶対値（100 - fix率） | 初回品質 |
| Survival | 25% | 相対値（ドメイン内） | 時間減衰blame生存 |
| Design | 20% | 相対値 | アーキテクチャファイル貢献 |
| Breadth | 10% | 相対値 | リポ横断（3コミット以上） |
| Debt Cleanup | 15% | 絶対値（0-100） | 他者の負債清掃率 |
| Indispensability | 5% | 相対値 | モジュール80%+所有 |

## アーキタイプ一覧（archetype.go のルール定義順 = 優先順位）

1. Architect — Prod↑ Surv↑ Design↑
2. Former Architect — RawSurv↑ Surv↓ (Design↑ or Indisp↑)
3. Churn Producer — Prod-Surv gap≥30 + notLow(Prod) + Qual↓ + Surv↓
4. Rescue Producer — Prod↑ Surv↓ Debt↑
5. Mass Producer — Prod↑ Surv↓
6. Solid Cleaner — Qual↑ Surv↑ Debt↑
7. Spreader — Breadth↑ Prod↓ Surv↓ Design↓
8. Silent Killer — Prod↓ Surv↓ Debt↓ (commits≥100のみ)
9. Fragile Fortress — Surv↑ Prod↓ Qual<70（変更圧がないから残っているだけ）
10. Specialist — Surv↑ Breadth↓
11. Quality Anchor — Qual↑ notLow(Prod)
12. Growing — Prod↓ Qual↑

### 分類ロジック

- soft-match関数: `highness(v)`, `lowness(v)`, `notLow(v)` → 0.0〜1.0
- 最小信頼度閾値: 0.10（これ未満はフィルタ）
- 優先マージン: 0.15以内なら定義順（priority）で解決
- Primary + Secondary を返す

## ドキュメント更新対象

アーキタイプ追加・変更時に更新が必要なファイル（全4箇所）:

1. **README.md** — アーキタイプテーブル + 説明文
2. **PROMPT.md** — Claude分析プロンプト内のアーキタイプリスト
3. **docs/blog-en-devto.md** — 英語ブログ（テーブル + 説明 + 注釈）
4. **docs/blog-ja-hatena.md** — 日本語ブログ（テーブル + 説明 + 注釈）

出力フォーマット変更時:
- **docs/images/terminal-output.svg** — ターミナル出力のSVG
- **docs/images/archetypes-radar.svg** — レーダーチャートSVG

## リリースフロー

```bash
# 1. コミット & プッシュ
git add <files> && git commit -m "feat: ..." && git push origin main

# 2. タグ作成 & プッシュ
git tag v0.X.Y && git push origin v0.X.Y

# 3. goreleaser実行（ローカル）
GITHUB_TOKEN=$(gh auth token) goreleaser release --clean
# 注: HOMEBREW_TAP_GITHUB_TOKEN が未設定だとbrew更新だけ失敗する（バイナリは公開される）

# 4. Homebrew tap手動更新（HOMEBREW_TAP_GITHUB_TOKENがない場合）
cat dist/homebrew/eis.rb > /tmp/homebrew-tap/eis.rb
cd /tmp/homebrew-tap && git add eis.rb && git commit -m "update eis to v0.X.Y" && git push

# 5. ローカル更新
brew upgrade eis
# または
go install github.com/machuz/engineering-impact-score/cmd/eis@latest
```

### GitHub Actionsリリース（タグプッシュで自動）

`.github/workflows/release.yml` がタグ `v*` で自動実行。
`HOMEBREW_TAP_GITHUB_TOKEN` シークレットが必要。

## テスト実行

```bash
go test ./...
```

## 自律的に進めてよい作業

- archetype.goの修正 → ドキュメント4箇所の更新 → コミット → リリースまで一気通貫でOK
- SVGの更新
- ブログ記事の更新（日英両方）
- Homebrew tap更新

## 設計思想

- **ゲーム耐性**: 時間減衰survivalは忙しさでは膨らまない。残ったコードだけがカウントされる
- **ドメイン分離**: BE/FE/Infra/FWは別々にスコアリング。混ぜると汚染される
- **ハイブリッドスコアリング**: 絶対値（組織横断比較可能）+ 相対値（ドメイン内順位）
- **40点 = シニア**: 7軸で40+を出すのは意図的に厳しい基準

## 今後の方向性

impact metric → **engineering risk detector** への進化:
- `change_pressure = commits_touching_module / module_LOC` で変更圧を定量化
- `tested_survival` vs `untested_survival` でrobust code vs dormant codeを分離
- Fragile Fortressの精密版として活用
