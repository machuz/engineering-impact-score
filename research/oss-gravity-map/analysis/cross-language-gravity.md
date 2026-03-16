# The Laws of Physics Are Not Uniform — Cross-Language Analysis

*OSS Gravity Map: Do type systems and frameworks shape gravity?*

## Hypothesis

Different programming languages create different "physical laws" in their code universes. Specifically:

1. **Type system expressiveness** may correlate with how Design influence distributes across a team
2. **Gravity concentration** — the degree to which structural influence is held by a few people — may vary systematically by language family
3. **Framework-driven** ecosystems may absorb gravity into the framework itself, lowering individual engineers' structural influence

This is an empirical investigation using EIS (Engineering Impact Score) data from 27 major OSS repositories.

## Methodology

- **27 repositories** analyzed with `eis analyze`, covering 44,382 engineers total
- Repositories classified into **5 categories** by type system and structural culture
- For each repo, the **top 10 contributors by Gravity** are examined (averages of the broader population are diluted by thousands of low-activity contributors)
- **Gravity Concentration** = share of total gravity held by the top 10 contributors

### Categories

| Category | Characteristics | Languages | Repos |
|---|---|---|---|
| **Expressive** | Rich type system, ADTs, pattern matching, traits | Rust, Scala | 5 |
| **Go (Self-structured)** | Static, nominal typing, anti-framework culture, explicit interfaces | Go | 7 |
| **Framework-driven** | Structure delegated to framework; conventions over code | Java (Spring), Python (FastAPI), TS (NestJS), Elixir (Phoenix) | 4 |
| **Systems (C/C++)** | Static, manual memory, templates | C, C++ | 5 |
| **Dynamic / Structural** | Dynamic or structural typing, self-structured | JavaScript, TypeScript, Python | 6 |

**Why split Go and Java?** Go and Java share nominal type systems, but their **structural culture is opposite**. Go eschews frameworks — engineers build structure from scratch using standard library and explicit interfaces. Java (Spring) delegates structure to framework annotations, dependency injection, and convention. This produces fundamentally different gravity distributions.

**Why split Framework-driven and Dynamic?** NestJS, FastAPI, and Phoenix are framework-driven even though their languages are dynamic or structural. Express, React, and Prettier are dynamic-language projects where engineers build their own structure.

---

## Results

### Summary by Category

| Category | Repos | Avg Size | Top10 Design | Top10 Survival | Top10 Gravity | Max Gravity | Gravity Concentration |
|---|---|---|---|---|---|---|---|
| **Go (Self-structured)** | 7 | 2,135 | 31.3 | 19.9 | 52.8 | 88.8 | **16.4%** |
| **Dynamic / Structural** | 6 | 1,184 | 24.8 | 17.1 | 51.2 | 92.2 | 10.4% |
| **Framework-driven** | 4 | 1,127 | 18.5 | 17.5 | 43.2 | 98.4 | 7.1% |
| **Expressive** | 5 | 2,151 | 26.3 | 13.7 | 51.2 | 91.1 | **6.7%** |
| **Systems (C/C++)** | 5 | 1,414 | 25.4 | 14.4 | 52.4 | 94.9 | 3.4% |

### Key Observations

#### 1. Go Concentrates Gravity — Expressive Types Distribute It

| Category | Gravity Concentration |
|---|---|
| **Go (Self-structured)** | **16.4%** |
| **Dynamic / Structural** | 10.4% |
| **Framework-driven** | 7.1% |
| **Expressive (Rust/Scala)** | **6.7%** |
| **Systems (C/C++)** | 3.4% |

**Go concentrates gravity at 2.4x the rate of Expressive type systems.** Go's anti-framework culture means someone *must* build the structure — and that structural authority concentrates in a few architects. The explicit interface pattern creates a small number of contract-defining files that dominate `git blame`.

Expressive type systems distribute gravity more evenly. When the type system itself can encode design decisions (through ADTs, traits, type-level programming), **structure becomes embedded in the type signatures rather than in a few architects' code**. The type system acts as a distributed architect.

#### 2. Frameworks Absorb Gravity

The **Framework-driven** category shows the lowest Top10 Gravity (**43.2**) and the lowest Top10 Design (**18.5**). This is the framework absorbing structural influence that would otherwise belong to engineers.

When Spring, NestJS, or Phoenix defines the routing, DI, middleware, and lifecycle, those design decisions don't appear in any engineer's `git blame`. **The framework is the invisible architect.** EIS can only observe gravity that lives in code — gravity that lives in framework conventions is Dark Matter.

Gravity Concentration (7.1%) is similar to Expressive (6.7%), but for the opposite reason: Expressive distributes gravity across many engineers via the type system, while Framework-driven removes gravity from engineers entirely and places it in the framework.

**Same concentration, completely different physics.**

#### 3. Design Influence Tells the Story

| Category | Top10 Design |
|---|---|
| **Go (Self-structured)** | **31.3** |
| **Expressive** | 26.3 |
| **Systems (C/C++)** | 25.4 |
| **Dynamic / Structural** | 24.8 |
| **Framework-driven** | **18.5** |

Go leads Design because its architects write the interfaces, the routing structure, the middleware patterns — all from scratch. In framework-driven ecosystems, these same design decisions are made by the framework, not by engineers. **The 12.8 point gap between Go and Framework-driven is the framework's shadow.**

---

### Per-Repository Detail

| Repository | Category | Language | Engineers | Top10 Design | Top10 Survival | Top10 Gravity | Max Gravity | Grav Conc |
|---|---|---|---|---|---|---|---|---|
| polars | Expressive | Rust | 694 | 17.4 | 29.8 | 41.3 | 100.0 | 7.0% |
| rust | Expressive | Rust | 7,914 | 53.0 | 5.7 | 68.9 | 77.4 | 0.6% |
| scala | Expressive | Scala | 794 | 32.3 | 5.9 | 56.7 | 81.4 | 6.8% |
| scala3 | Expressive | Scala 3 | 995 | 12.6 | 12.9 | 49.2 | 96.9 | 3.3% |
| swc | Expressive | Rust | 357 | 16.4 | 14.0 | 40.1 | 100.0 | 15.7% |
| argo-cd | Go (Self-structured) | Go | 1,889 | 41.4 | 20.5 | 52.0 | 92.3 | 4.0% |
| esbuild | Go (Self-structured) | Go | 125 | 10.0 | 10.0 | 37.0 | 100.0 | 92.5% |
| grafana | Go (Self-structured) | Go/TS | 2,893 | 16.3 | 24.6 | 50.1 | 80.8 | 1.9% |
| kubernetes | Go (Self-structured) | Go | 5,217 | 42.5 | 19.9 | 56.1 | 77.3 | 0.8% |
| loki | Go (Self-structured) | Go | 1,319 | 34.0 | 19.3 | 65.5 | 86.7 | 7.8% |
| prometheus | Go (Self-structured) | Go | 1,281 | 44.5 | 11.9 | 62.1 | 100.0 | 5.4% |
| terraform | Go (Self-structured) | Go | 2,223 | 30.3 | 32.7 | 46.5 | 84.3 | 2.4% |
| spring-boot | Framework-driven | Java | 1,504 | 30.2 | 34.1 | 52.8 | 93.5 | 7.3% |
| nest | Framework-driven | TypeScript | 684 | 13.3 | 10.2 | 39.6 | 100.0 | 7.0% |
| fastapi | Framework-driven | Python | 897 | 11.7 | 11.2 | 37.7 | 100.0 | 9.4% |
| phoenix | Framework-driven | Elixir | 1,424 | 18.9 | 14.4 | 42.9 | 100.0 | 4.5% |
| ClickHouse | Systems (C/C++) | C++ | 2,563 | 17.3 | 30.0 | 54.8 | 100.0 | 1.4% |
| arrow | Systems (C/C++) | C++/Multi | 1,466 | 28.3 | 12.4 | 50.9 | 77.8 | 3.8% |
| duckdb | Systems (C/C++) | C++ | 690 | 20.7 | 4.9 | 49.3 | 100.0 | 4.5% |
| envoy | Systems (C/C++) | C++ | 1,444 | 46.4 | 15.7 | 61.2 | 96.8 | 3.5% |
| redis | Systems (C/C++) | C | 905 | 14.3 | 8.9 | 45.6 | 100.0 | 4.0% |
| eslint | Dynamic / Structural | JavaScript | 1,180 | 18.6 | 12.8 | 58.6 | 100.0 | 8.1% |
| express | Dynamic / Structural | JavaScript | 391 | 13.5 | 3.2 | 38.9 | 100.0 | 23.9% |
| prettier | Dynamic / Structural | JavaScript | 799 | 42.9 | 10.0 | 48.2 | 95.2 | 13.4% |
| react | Dynamic / Structural | JavaScript | 2,010 | 17.5 | 31.1 | 48.0 | 72.0 | 3.4% |
| superset | Dynamic / Structural | Python/TS | 1,477 | 23.6 | 29.5 | 57.7 | 100.0 | 4.5% |
| vite | Dynamic / Structural | TypeScript | 1,247 | 32.6 | 16.0 | 55.8 | 85.7 | 9.3% |

---

## Interpretation

### Three Modes of Structural Authority

The data reveals three distinct ways that code universes distribute structural authority:

1. **Architect-centric** (Go) — Structure is built by people. A small number of architects hold disproportionate design authority. Gravity concentration: high.

2. **Type-distributed** (Rust, Scala) — Structure is encoded in the type system. Design authority is distributed across anyone who writes type signatures. Gravity concentration: low.

3. **Framework-absorbed** (Spring, NestJS, FastAPI, Phoenix) — Structure lives in the framework. Neither people nor types hold much gravity — the framework does. Gravity on individuals: low.

These three modes produce similar-looking code, but the **physics of who holds structural authority** is fundamentally different. And this has consequences for team scaling, architect succession, and entropy resistance.

### This Is Not About Superiority

These numbers do not say one language is better than another. They show that **each language family creates a different gravitational physics**.

- In a **small universe** where complexity is manageable, framework-absorbed gravity works well. Bootstrap quickly, let the framework be your architect.
- In a **large universe** with many contributors: does the language help distribute design authority (Expressive), or does it force centralization (Go)?
- In **self-structured** universes (Go, Dynamic): the architect becomes a single point of failure. The question is whether you can sustain architect succession.

**Knowing which physics your universe operates under helps you make better structural decisions.**

### Limitations

- **27 repositories** is a meaningful sample but not exhaustive
- Repository maturity, governance model, and community culture are confounding variables
- EIS observes `git blame` and commit patterns — design decisions expressed outside of code (RFCs, ADRs, discussions) are invisible (Dark Matter)
- Some repositories span multiple languages (grafana: Go+TS, superset: Python+TS)
- Category boundaries are judgment calls — reasonable people may classify differently

### Future Directions

- **Entropy resistance by language**: Do expressive type systems show higher Robust Survival as universe size grows?
- **Architect succession patterns**: Do certain language families produce smoother generational transitions?
- **Framework effect isolation**: Compare framework-driven vs bare projects in the same language
- **Scale threshold analysis**: At what universe size does gravity concentration become a risk factor?

---

## Conclusion

The hypothesis that "the laws of physics are not uniform across code universes" is supported by the data.

**Gravity concentration varies by 4.8x between Go (Self-structured) and Systems (C/C++).** Between the three structural modes — architect-centric, type-distributed, framework-absorbed — the difference in how design authority flows through a team is stark.

For years, debates about technology choices have been aerial battles — fought with experience and intuition. This data is a first step toward **making design debates scientific**.

---

*Generated by [EIS (Engineering Impact Score)](https://github.com/machuz/engineering-impact-score) — OSS Gravity Map Project*
*27 repositories, 44,382 engineers, observed through commit light.*
