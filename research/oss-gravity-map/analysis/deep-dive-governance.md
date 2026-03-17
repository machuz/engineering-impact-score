# Deep Dive: Three Governance Models — Rails, Laravel, esbuild

*Same metric. Three completely different governance physics.*

---

## Overview

These three projects represent three extremes of how structural authority distributes in open-source software:

| Project | Category | Engineers | Gravity Conc. | Top10 Design | Governance |
|---|---|---|---|---|---|
| **Rails** | Framework-driven (Ruby) | 6,512 | **0.9%** | **51.2** | Multi-architect civilization |
| **Laravel** | Framework-driven (PHP) | 4,449 | 1.5% | 17.2 | Creator's kingdom |
| **esbuild** | Go (Self-structured) | 125 | **92.5%** | 10.0 | One-person universe |

Gravity Concentration ranges from **0.9% to 92.5%** — a 103x difference. The same scoring system, the same formula, reveals fundamentally different civilizations.

---

## 1. Rails — The Multi-Architect Civilization

![Rails Gravity Concentration](chart-gravity-concentration.svg)

### Key Numbers

| Metric | Value |
|---|---|
| Engineers | 6,512 |
| Gravity Concentration | **0.9%** (among lowest measured) |
| Top10 Design | **51.2** (higher than most Go projects) |
| Top10 Gravity | 54.0 |
| Top10 Survival | 7.3 |
| Architects with Design > 35 | **6 people** |

### Top 10 Gravity Ranking

| # | Engineer | Gravity | Design | Indispensability | Survival | State |
|---|---|---|---|---|---|---|
| 1 | David Heinemeier Hansson | **100.0** | 100.0 | 100.0 | 11.5 | Former |
| 2 | Aaron Patterson | 64.0 | 54.0 | 44.4 | 0.9 | Silent |
| 3 | Jeremy Kemper | 58.9 | **89.0** | 5.6 | 0.0 | Silent |
| 4 | Rafael Mendonca Franca | 55.0 | **68.4** | 11.1 | 25.0 | Growing |
| 5 | Pratik Naik | 50.4 | 31.1 | 27.8 | 0.0 | Silent |
| 6 | Xavier Noria | 48.2 | **45.8** | 11.1 | 30.2 | Growing |
| 7 | Jose Valim | 41.8 | **39.4** | 0.0 | 0.0 | Silent |
| 8 | Joshua Peek | 41.0 | **36.6** | 0.0 | 0.0 | Silent |
| 9 | Sean Griffin | 41.0 | 14.4 | 16.7 | 0.0 | Silent |
| 10 | Ryuta Kamizono | 40.1 | 33.6 | 0.0 | 5.0 | Growing |

### Design Authority Distribution

```
DHH             ████████████████████████████████████████████████████████  100.0
Jeremy Kemper   █████████████████████████████████████████████████         89.0
Rafael Franca   ██████████████████████████████████████                    68.4
Aaron Patterson ██████████████████████████████                            54.0
Xavier Noria    █████████████████████████                                 45.8
Jose Valim      ██████████████████████                                    39.4
Joshua Peek     ████████████████████                                      36.6
R. Kamizono     ██████████████████                                        33.6
Pratik Naik     █████████████████                                         31.1
                ─────────────────────────── Design > 35 threshold ────────
```

**6 people exceed Design 35.** This is extraordinary for a framework-driven project.

### Analysis

Rails has evolved from a creator-centric kingdom into a **multi-architect civilization**.

DHH created the gravitational center — Design 100, Indispensability 100. But unlike most framework-driven projects, **multiple architects now share structural authority**. Jeremy Kemper's Design 89 means his architectural fingerprint is nearly as deep as the creator's. Rafael Franca (68.4), Aaron Patterson (54.0), Xavier Noria (45.8), and Jose Valim (39.4) all hold significant design influence.

Top10 Design of **51.2** is higher than most Go projects, which are supposed to concentrate design authority. Rails is "framework-driven" in its user-facing API, but internally it functions more like a self-structured project with distributed governance.

The Gravity Concentration of **0.9%** is comparable to Kubernetes (0.8%) and the Rust compiler (0.6%). No single person's departure would collapse the structure.

**Rails has achieved architect succession at scale.** This is the gold standard for open-source governance.

---

## 2. Laravel — The Creator's Kingdom

![Rails vs Laravel](chart-rails-vs-laravel.svg)

### Key Numbers

| Metric | Value |
|---|---|
| Engineers | 4,449 |
| Gravity Concentration | 1.5% |
| Top10 Design | **17.2** (3x lower than Rails) |
| Top10 Gravity | 56.2 |
| Top10 Survival | **15.3** (2x higher than Rails) |
| Design Authority | **Taylor Otwell alone** |

### Top 10 Gravity Ranking

| # | Engineer | Gravity | Design | Indispensability | Survival | Commits |
|---|---|---|---|---|---|---|
| 1 | Taylor Otwell | **100.0** | **100.0** | **100.0** | 36.3 | 9,723 |
| 2 | Kay W. | 70.0 | 0.1 | 100.0 | 0.6 | 7 |
| 3 | Lucas Michot | 51.1 | 3.5 | 50.0 | 8.3 | 724 |
| 4 | Tim MacDonald | 50.8 | 2.6 | 50.0 | 25.4 | 205 |
| 5 | Luke Kuzmish | 50.4 | 1.3 | 50.0 | 57.6 | 158 |
| 6 | Caleb White | 50.3 | 1.0 | 50.0 | 14.8 | 60 |
| 7 | Patrick Hesselberg | 50.0 | 0.0 | 50.0 | 0.1 | 3 |
| 8 | Alex Bowers | 50.0 | 0.1 | 50.0 | 0.0 | 50 |
| 9 | Graham Campbell | 48.9 | **63.1** | 0.0 | 0.2 | 1,249 |
| 10 | Nuno Maduro | 40.1 | 0.2 | 25.0 | 9.9 | 7 |

### Design Monopoly

```
Taylor Otwell      ████████████████████████████████████████████████████████  100.0
Graham Campbell    ███████████████████████████████████                        63.1
                   ─────────────────────── gap ──────────────────────────────
Lucas Michot       ██                                                          3.5
Tim MacDonald      █                                                           2.6
Luke Kuzmish       █                                                           1.3
Caleb White        █                                                           1.0
Kay W.             ▏                                                           0.1
Nuno Maduro        ▏                                                           0.2
Others             ▏                                                           0.0
```

**Taylor Otwell holds all the Design.** Only Graham Campbell (63.1) has meaningful architectural influence. Everyone else: Design < 4.

### Analysis

Laravel is a **creator-centric kingdom** — efficient, but with a single point of structural authority.

Taylor Otwell holds every axis at maximum: Design 100, Indispensability 100, Gravity 100, with 9,723 commits. The structural decisions all flow through one person.

This isn't necessarily a problem. Laravel's Survival of **15.3** is 2x Rails' 7.3 — less code gets rewritten. A single architect's consistent vision means less churn. This is **efficiency through centralization**.

But it creates a bus factor of 1 for structural authority. Compare to Rails: same framework-driven category, but Rails distributes Design across 6+ architects (Top10 Design **51.2** vs Laravel's **17.2**).

**Same framework pattern. Opposite governance physics.**

The interesting question is not "which is better" but "what produced this difference?" Rails is 20+ years old with intentional architect succession. Laravel is younger with a creator who is still the primary architect. Time may tell whether Laravel follows the Rails path toward distributed governance, or maintains its centralized model.

---

## 3. esbuild — The One-Person Universe

### Key Numbers

| Metric | Value |
|---|---|
| Engineers | 125 |
| Gravity Concentration | **92.5%** (highest measured) |
| Top10 Design | 10.0 |
| Evan Wallace — all axes | **100** |
| #2 contributor — all axes | Design 0, Indispensability 0, Survival 0 |

### The Singularity

```
Evan Wallace:    Gravity 100 | Design 100 | Indispensability 100 | Survival 100
                 ════════════════════════════════════════════════════════════════

#2  Ade V. Fadlil:    Gravity 30 | Design 0 | Indispensability 0 | Survival 0
#3  Pig Fang:          Gravity 30 | Design 0 | Indispensability 0 | Survival 0
#4  Mike Cook:         Gravity 30 | Design 0 | Indispensability 0 | Survival 0
#5  Justin Ridgewell:  Gravity 30 | Design 0 | Indispensability 0 | Survival 0
#6  Ryan Tsao:         Gravity 30 | Design 0 | Indispensability 0 | Survival 0
#7  magic-akari:       Gravity 30 | Design 0 | Indispensability 0 | Survival 0
#8  Liu Bowen:         Gravity 30 | Design 0 | Indispensability 0 | Survival 0
#9  Tommaso De Rossi:  Gravity 30 | Design 0 | Indispensability 0 | Survival 0
#10 John Gozde:        Gravity  0 | Design 1 | Indispensability 0 | Survival 0
```

Contributors #2-#9 all have Gravity 30.0 from Breadth (100) alone — they touched broad files, but none of their code became structural. **Zero Design, zero Indispensability, zero Survival.**

### How Extreme Is 92.5%?

| Project | Gravity Concentration |
|---|---|
| **esbuild** | **92.5%** |
| express | 23.9% |
| swc | 15.7% |
| prettier | 13.4% |
| vite | 9.3% |
| react | 3.4% |
| rails | 0.9% |
| kubernetes | 0.8% |
| rust | 0.6% |

esbuild's concentration is **115x higher than Kubernetes** and **103x higher than Rails**. This is not an outlier — it's a different category of project entirely.

### Analysis

esbuild proves that a single brilliant architect can build an entire universe alone.

Evan Wallace created esbuild as a demonstration that JavaScript bundling could be 10-100x faster. He wrote 4,208 commits with every EIS metric at 100. The result is a focused, fast, correct tool — precisely because one person controls every structural decision.

This is the **extreme end of the architect-centric model** — a gravitational singularity. In physics, singularities are points where normal laws break down. The same is true here: esbuild's governance model doesn't scale, doesn't succession-plan, and doesn't need to. It's a finished artifact, not an evolving ecosystem.

The 124 other contributors provided patches and fixes, but none of their code became structural. Breadth 100 means they touched files across the project — but Design 0 and Indispensability 0 mean none of that code shaped the architecture or became depended upon.

**A singularity is powerful, but it cannot be succession-planned.**

---

## Three Models Compared

![Three Modes of Structural Authority](chart-three-modes.svg)

| Dimension | Rails | Laravel | esbuild |
|---|---|---|---|
| **Governance** | Multi-architect democracy | Benevolent monarchy | Singularity |
| **Design Distribution** | 6 architects > 35 | 1 architect (+ 1 deputy) | 1 architect, period |
| **Bus Factor** | High (6+) | Low (1) | Zero |
| **Efficiency** | Lower (more rewriting) | Higher (consistent vision) | Maximum (no coordination) |
| **Succession** | Proven | Untested | N/A |
| **Gravity Concentration** | 0.9% | 1.5% | 92.5% |
| **Top10 Design** | 51.2 | 17.2 | 10.0 |
| **Scalability** | Proven at 6,512 | Proven at 4,449 | Limited to 1 |

### Key Insight

These three projects exist on a spectrum from **maximum distribution** (Rails) to **maximum concentration** (esbuild). Neither extreme is inherently better — each is adapted to its context:

- **Rails** needs distributed governance because it's a living ecosystem with 6,512 contributors spanning 20+ years
- **Laravel** thrives under centralized governance because Taylor Otwell's consistent vision minimizes churn
- **esbuild** works as a singularity because it's a focused tool, not an evolving framework

The question is not "which model is best" but **"which model matches your project's lifecycle stage, scale, and goals?"**

---

*Generated by [EIS (Engineering Impact Score)](https://github.com/machuz/engineering-impact-score) — OSS Gravity Map Project*
*Gravity = Indispensability × 0.40 + Breadth × 0.30 + Design × 0.30*
