---
title: "git考古学——ソフトウェア宇宙の完全理論"
---

*もしgit履歴が、誰が本当にコードベースを形作ったかを教えてくれるとしたら？*

17章（0〜16）にわたって、ソフトウェアの理論を構築した——単純な問いから始まり、宇宙論に到達した。これはその全体像を1記事に凝縮したものだ。

---

## 0. 望遠鏡

始まりは一つのフラストレーションだった。**「このチームは強い。しかしそれを説明する言葉がなかった。」**

これまで何人もの強いエンジニアを自ら声をかけて採用してきた。なぜ来てくれたのか。きっと「**この人は自分の仕事をちゃんと見てくれている**」と感じてくれたからだと思う。コミット数ではなく——コードが生き残っているか、アーキテクチャに貢献しているか、負債を片付けているか。

その観測者の目を、EISとして**OSSの望遠鏡**にした。

`git log` と `git blame` だけで、7つの軸でエンジニアリングインパクトを定量化する：

| 軸 | 何を測るか |
|---|---|
| **Production** | アウトプット量 |
| **Quality** | 初回品質（fix率の低さ） |
| **Survival** | コードがどれだけ生き残っているか（時間減衰付き） |
| **Design** | 構造的影響——アーキテクチャファイルへの貢献 |
| **Breadth** | コードベース横断の活動 |
| **Debt Cleanup** | 他者の負債を清掃する力 |
| **Indispensability** | blameによるモジュール所有率 |

ここから3つのトポロジーが浮かび上がる：**Role**（Architect / Anchor / Producer）、**Style**（Builder / Balanced / Mass）、**State**（Active / Growing / Fragile / Former）。

> 定量化できるものは定量化する。できないものは定性的に補う。この順番が大事。

*詳細: [第0章 — 導入](https://zenn.dev/machuz/books/git-archaeology/viewer/ch0), [第1章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch1), [第2章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch2)*

---

## II. 進化

タイムライン——四半期ごとのスコアスナップショットを加えると、物語が現れた。

あるエンジニアのRoleがProducerからAnchor、そしてArchitectへと遷移する。別のエンジニアのスコアは横ばい——停滞ではなく**戦略的な忍耐**。退職の軌道は、誰かが気づく3四半期前から可視化される。

冷たい数字が、最も人間的な物語を語る。

タイムラインから進化法則を抽出した：

- **BuilderがArchitectの前提条件** — 作ったことがないものは設計できない
- **Producerは代謝であり退行ではない** — 最高のArchitectも時にProducerに戻る
- **Backend Architectは収束する。Frontend Architectは分岐する** — 異なる重力物理
- **退職したArchitectはコードに「魂」を残す** — Debt Cleanupによる成仏は聖なる仕事

*詳細: [第3章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch3), [第4章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch4), [第5章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch5), [第6章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch6)*

---

## III. 宇宙論

深く観測するほど、コードベースは宇宙に似ていた。

| 物理学 | ソフトウェア |
|---|---|
| ビッグバン | 最初のコミット——初期条件がすべてを決める |
| 星 | エンジニア |
| 重力 | 構造的影響力——優れたエンジニアはコードベースの重力を曲げる |
| ダークマター | コミットに現れない仕事：レビュー、設計議論、メンタリング、文化 |
| エントロピー | コード腐敗——放置すれば常に無秩序に向かう |
| ブラックホール | 構造を分散させず依存を集中させるエンジニア |
| 崩壊 | ブラックホールエンジニアが去った時に起きること |

これは比喩ではない。**構造的な対応関係**だ。

**重力**が中核概念。すべてのコードが等しいわけではない。50のファイルが依存するモジュール境界を作ったエンジニアは、重力を生成した——周囲のすべてを形作る構造的な力だ。

**ダークマター**は望遠鏡が見えないもの。文化、メンタリング、設計議論、プランニング——コミットには現れないが、宇宙の全構造を決定する。

**エントロピー**がデフォルト。ソフトウェアは常に腐る。開発はエントロピーとの戦いだ。

**崩壊**は重力が分散ではなく集中した時に起きる。良いArchitectは自分がいなくなった後の宇宙を設計する。

> 星は永遠ではない。だから構造が重要なのだ。

*詳細: [第7章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch7), [第8章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch8), [第9章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch9), [第10章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch10), [第11章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch11), [第12章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch12)*

---

## IV. 文明

ほとんどのコードベースは数年で死ぬ。エントロピーが勝つ。チームが変わる。知識が散逸する。誰かが「スクラッチから書き直そう」と言う。

しかし少数が生き残る。**Linux。Git。PostgreSQL。React。** 創造者は去り、コントリビュータは世代を超えて入れ替わり、それでも構造が持続した。これらはリポジトリではない。**文明**だ。

文明には3つの役割が必要：

```
文明 =
  Architect  → 重力を生む（構造）
  + Anchor   → 秩序を維持する（安定性）
  + Producer → 領土を広げる（成長）
```

どれか一つ欠けると等式が崩れる：

| 欠けた役割 | 結果 |
|---|---|
| Architectなし | 構造なき成長——エントロピーの勝利 |
| Anchorなし | 美しいが脆い——Architectが去ると崩壊 |
| Producerなし | 成長なき構造——化石化 |

最も重要なエンジニアは、自分を必要としないシステムを作る。それが文明のテスト：**Architectが去った後も構造は生き残るか？**

*詳細: [第13章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch13), [第14章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch14)*

---

## V. AIは星を生むが、重力は生まない

AIはスターバースト——かつてない速度でコードを生成する。

しかし構造のないコードはエントロピーだ。どれだけ多くの星が生まれても、重力がなければ銀河は誕生しない。

AI時代、最も希少なエンジニアリング能力は移行する：

| 時代 | 最も希少な能力 |
|---|---|
| AI以前 | コードを書くこと（Production） |
| AI以後 | 重力を生むこと（Design, Survival） |

AIは**重力増幅器**になる。かつて一つのコードベースを形作ったArchitectが、今は十を形作れる。重要なのはコードを書く筋肉ではない——重力を生む筋肉だ。

> AIは星を生む。しかし重力を形作るのはエンジニアだ。

*詳細: [第15章](https://zenn.dev/machuz/books/git-archaeology/viewer/ch15)*

---

## VI. 重力を作るエンジニアたち

ソフトウェアエンジニアリングは、2種類の時間の間に存在する。

Gitは過去を記憶する。AIは未来を想像する。

その間で、エンジニアは重力を形作る——構造を生み、秩序を生み、システムの崩壊を防ぐ。

重力があるところで、コードは単なる断片ではなく構造になる。構造が生まれるとき、システムは時間を超えて持続する。それはもはやリポジトリではない。**文明になる。**

```
Gitは過去を記憶する。
AIは未来を想像する。

その間で、エンジニアは重力を形作る。

そしてその重力から、
ソフトウェア文明が生まれる。
```

*詳細: [第16章（最終章）](https://zenn.dev/machuz/books/git-archaeology/viewer/ch16)*

---

あなたのコード宇宙に重力はあるか？

望遠鏡を向けて、見てみよう。

```bash
❯ brew tap machuz/tap && brew install eis
❯ eis analyze --recursive ~/your-workspace
```

```
      ✦       *        ✧

       ╭────────╮
      │    ✦     │
       ╰────┬───╯
   .        │
            │
         ___│___
        /_______\

   ✧     the Git Telescope     ✦
```

---

### 全章リンク

- **[第0章：git履歴が最強のエンジニアを教えてくれるとしたら？](https://zenn.dev/machuz/books/git-archaeology/viewer/ch0)** — 導入
- [第1章：履歴だけでエンジニアの「戦闘力」を定量化する](https://zenn.dev/machuz/books/git-archaeology/viewer/ch1)
- [第2章：エンジニアの「戦闘力」から、チームの「構造力」へ](https://zenn.dev/machuz/books/git-archaeology/viewer/ch2)
- [第3章：Architectには流派がある](https://zenn.dev/machuz/books/git-archaeology/viewer/ch3)
- [第4章：Backend Architectは収束する](https://zenn.dev/machuz/books/git-archaeology/viewer/ch4)
- [第5章：タイムライン——スコアは嘘をつかない](https://zenn.dev/machuz/books/git-archaeology/viewer/ch5)
- [第6章：チームは進化する](https://zenn.dev/machuz/books/git-archaeology/viewer/ch6)
- [第7章：コードの宇宙を観測する](https://zenn.dev/machuz/books/git-archaeology/viewer/ch7)
- [第8章：エンジニアリング相対性理論](https://zenn.dev/machuz/books/git-archaeology/viewer/ch8)
- [第9章：Origin——コード宇宙のビッグバン](https://zenn.dev/machuz/books/git-archaeology/viewer/ch9)
- [第10章：Dark Matter——見えない重力](https://zenn.dev/machuz/books/git-archaeology/viewer/ch10)
- [第11章：Entropy——宇宙は常に無秩序に向かう](https://zenn.dev/machuz/books/git-archaeology/viewer/ch11)
- [第12章：Collapse——良いArchitectとBlack Hole Engineer](https://zenn.dev/machuz/books/git-archaeology/viewer/ch12)
- [第13章：Cosmology of Code——コード宇宙論](https://zenn.dev/machuz/books/git-archaeology/viewer/ch13)
- [第14章：Civilization——なぜ一部のコードベースだけが文明になるのか](https://zenn.dev/machuz/books/git-archaeology/viewer/ch14)
- [第15章：AI Creates Stars, Not Gravity](https://zenn.dev/machuz/books/git-archaeology/viewer/ch15)
- [第16章（最終章）：The Engineers Who Shape Gravity](https://zenn.dev/machuz/books/git-archaeology/viewer/ch16)

![EIS — the Git Telescope](https://raw.githubusercontent.com/machuz/engineering-impact-score/main/docs/images/logo-full.png?v=2)

**GitHub**: [engineering-impact-score](https://github.com/machuz/engineering-impact-score) — CLIツール、計算式、方法論すべてオープンソース。`brew tap machuz/tap && brew install eis` でインストール。

応援してくれる方: [GitHub Sponsors](https://github.com/sponsors/machuz)
