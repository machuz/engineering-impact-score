### 前回のあらすじ

[第1章](https://ma2k8.hateblo.jp/entry/2026/03/11/153212)では、gitの履歴データだけでエンジニア個人の「戦闘力」を7軸で定量化する手法を紹介した。3軸トポロジー（Role / Style / State）による分類も加え、「この人はどんなエンジニアか」を一言で表現できるようになった。

しかし、個人スコアだけでは見えないものがある。

**チーム**だ。

### 個人指標の限界

個人スコアが全員80点超えのチームが必ずしも「強い」とは限らない。全員がProducerタイプで、Architect不在。誰もアーキテクチャを触らない。誰も負債を片付けない。生産量は凄まじいが、コードは3ヶ月で腐る。

逆に、平均スコアが50点台でもArchitectが1人いて、Cleanerがいて、Growing状態の若手が育っているチームは強い。半年後にはもっと強くなる。

**「強いチーム」は個人の総和では測れない。構成と補完性が重要だ。**

### `eis team` — チーム分析コマンド

個人分析の `eis analyze` に加え、チームレベルの分析を行う `eis team` コマンドを追加した。

```bash
# ドメイン全体を1チームとして分析（設定不要）
eis team --recursive ~/workspace

# チーム定義ありで分析
eis team --config eis.yaml --recursive ~/workspace

# JSON出力（AIに貼って深い分析をしてもらう用）
eis team --format json --recursive ~/workspace
```

teams設定が無い場合はドメイン（Backend / Frontend / Infra）ごとに全メンバーを1チームとして扱う。設定なしでもすぐ使える。

```yaml
# eis.yaml
teams:
  backend-core:
    domain: Backend
    members:
      - alice
      - bob
      - charlie
  frontend-app:
    domain: Frontend
    members:
      - dave
      - eve
```

### チーム健全性 — 7つの指標

チームの「健全性」を以下の7軸で評価する。個人の7軸と対になる設計だ。

#### 1. Complementarity（補完性）

Roleの多様性をカバレッジとして測る。既知のRole 5種（Architect, Anchor, Cleaner, Producer, Specialist）のうち何種類がチームにいるか。

```
coverage = uniqueRoles / 5
bonus = Architect在籍(+10) + Anchor在籍(+5) + Cleaner在籍(+5)
score = coverage × 80 + bonus  (0-100)
```

**Architectが不在のチームは、補完性スコアで真っ先にわかる。** ArchitectはRoleの中で最もスコアを押し上げるボーナスを持つ。これは意図的な設計で、「設計を担える人」がチームにいるかどうかは補完性の核心だからだ。

#### 2. Growth Potential（成長力）

チーム内のGrowing状態メンバーの割合 + メンタリング環境の有無。

```
growingRatio = growingCount / memberCount
score = growingRatio × 60 + Builder在籍(+20) + Cleaner在籍(+20)
```

BuilderやCleanerは「手本になる人」がいる指標。**Growingの若手がいても、手本が不在なら育たない。** 両方揃って初めてスコアが上がる。

#### 3. Sustainability（持続性）

リスク状態（Former, Silent, Fragile）の逆数 + Architectの安定性。

```
riskRatio = (Former + Silent + Fragile) / memberCount
score = (1 - riskRatio) × 80 + Architect在籍(+20)
```

Former（元メンバーのコードが残っている）、Silent（コード書かないが居る）、Fragile（変更圧力のない場所でしか生き残っていない）——これらが多いチームは、見た目のメンバー数に反して実質的な戦力が少ない。

#### 4. Debt Balance（負債バランス）

メンバーのDebt Cleanupスコアの平均。50が中立で、50以上ならチーム全体がクリーン傾向。

```
score = avg(members.DebtCleanup)  // 0-100
```

50を大きく下回るチームは負債を生み出し続けている。50を超えるチームは自浄作用がある。

#### 5. Productivity Density（生産密度）

**この量のコードを、この人数で書いている**——という密度感。少人数で高いアウトプットを出しているチームにボーナスが付く。

```
base = avg(members.Production)
小チームボーナス: 3人以下で平均50以上 → ×1.2
                  5人以下で平均50以上 → ×1.1
```

3人で大規模APIサーバーを回しているようなチームは、この指標で異常値として可視化される。「すごいけど危険」——それが数字で見える。

#### 6. Quality Consistency（品質一貫性）

チーム全体の品質レベルと、そのバラつき。平均品質が高く、かつ標準偏差が小さいほどスコアが高い。

```
stdev = sqrt(sum((member.Quality - avgQuality)²) / memberCount)
score = avgQuality × 0.6 + (100 - stdev × 2) × 0.4
```

**全員が80点台のチームと、95点と40点が混在するチームは、平均が同じでも全く違う。** 後者はレビュー負荷が偏り、品質ゲートが形骸化している可能性がある。

#### 7. Risk Ratio（リスク人材割合）

Former + Silent + Fragile状態のメンバーが全体の何%を占めるか。直球の指標。

```
riskRatio = (Former + Silent + Fragile) / memberCount × 100  (%)
```

25%を超えたら要注意。50%超えは危機的。

### 強いチームの条件

チーム健全性の7軸を運用してみて見えてきたパターン：

**強いチームに共通する特徴：**
- Architect + Builder が在籍（設計する人と、設計を実装に落とせる人）
- Role多様性が3種以上（最低限 Architect / Anchor / Producer）
- Growing率が20%以上（若手が育っている）
- Risk Ratio が0%（リスク人材がいない、または少ない）
- Quality Consistencyが70以上（品質のバラつきが小さい）

**危険なチーム構成：**
- Mass/Churn偏重：大量に書くが生き残らないコードが溢れる
- Architect不在：誰も設計レイヤーを触らない → 暗黙知の蓄積
- Silent蓄積：形式上はメンバーだが実質的に貢献していない人が増える
- Producer一色：全員が書くだけで、片付ける人がいない

### 社会学的インサイト

この分析を複数チームで回して気づいたことがある。

**「こういう人がいるチームは人が育つ」** ——BuilderかCleanerが1人でもいると、Growing状態のメンバーが翌四半期にActiveに遷移する確率が体感で倍になる。コードレビューで「こう書くべき」を示す手本が存在するからだろう。

**「Architect不在のチームは品質が劣化する」** ——Complementarityが低いチームは、半年スパンで見るとQuality Consistencyも下がっていく。設計の道標がないと、各自が好き勝手にコードを書き始める。

**「少人数チームの異常値は、すごさとリスクの両面」** ——Productivity Densityが高いチームは確かに生産性が異常だが、1人抜けたときの崩壊リスクも高い。バス係数の個人版がIndispensabilityだとすれば、チーム版がProductivity Densityの裏側にある。

### 使い方

```bash
# インストール
brew tap machuz/tap && brew install eis

# チーム分析（最もシンプル）
eis team --recursive ~/workspace

# JSON出力 → AIに貼って深掘り
eis team --format json --recursive ~/workspace | pbcopy
# → Claude / ChatGPT に「このチームの強みとリスクを分析して」と投げる
```

深い洞察（Insights）の自動生成は意図的にスコープ外にしている。定量データの算出はツールの仕事、そこから何を読み取るかは人間（またはAI）の仕事。この住み分けが重要だと思っている。

### まとめ — 個人 × チームの両輪で組織を見る

第1章で作った個人スコアは「この人はどんなエンジニアか」を答える。
第2章で追加したチーム分析は「このチームはどんな状態か」を答える。

両方を組み合わせることで：
- **採用**: どのRoleが足りないかが可視化される → ポジション定義に使える
- **チーム編成**: 補完性を最大化する組み合わせが検討できる
- **1on1**: 個人スコアの推移をベースに成長の方向性を議論できる
- **リスク管理**: Risk Ratioの悪化を早期に検知できる

全部gitの履歴から出てくる。追加のツール導入も、エンジニアへのアンケートも不要。

**測れるものは改善できる。測れないものは祈るしかない。**

チームの強さを、祈りから指標に変えよう。
