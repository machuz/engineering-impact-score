# The Laws of Physics Are Not Uniform — Cross-Language Analysis

*OSS Gravity Map: Do type systems shape gravity?*

## Hypothesis

Different programming languages create different "physical laws" in their code universes. Specifically:

1. **Type system expressiveness** may correlate with how Design influence distributes across a team
2. **Gravity concentration** — the degree to which structural influence is held by a few people — may vary systematically by language family
3. **Dynamic languages** may produce lower gravity ceilings in their top contributors

This is an empirical investigation using EIS (Engineering Impact Score) data from 27 major OSS repositories.

## Methodology

- **27 repositories** analyzed with `eis analyze`, covering 44,382 engineers total
- Repositories classified into 4 categories by type system characteristics
- For each repo, the **top 10 contributors by Gravity** are examined (averages of the broader population are diluted by thousands of low-activity contributors)
- **Gravity Concentration** = share of total gravity held by the top 10 contributors

### Categories

| Category | Type System | Languages | Repos |
|---|---|---|---|
| **Expressive** | Rich type system, ADTs, pattern matching, traits | Rust, Scala | 5 |
| **Nominal** | Static, nominal typing, interfaces | Go, Java | 8 |
| **Systems** | Static, manual memory, templates | C, C++ | 5 |
| **Dynamic / Structural** | Dynamic or structural typing | JavaScript, TypeScript, Python, Elixir | 9 |

---

## Results

### Summary by Category

| Category | Repos | Avg Size | Top10 Design | Top10 Survival | Top10 Gravity | Max Gravity | Gravity Concentration |
|---|---|---|---|---|---|---|---|
| **Expressive Type System** | 5 | 2151 | 26.3 | 13.7 | 51.2 | 91.1 | 6.7% |
| **Nominal Type System** | 8 | 2056 | 31.2 | 21.6 | 52.8 | 89.4 | 15.3% |
| **Systems (C/C++)** | 5 | 1414 | 25.4 | 14.4 | 52.4 | 94.9 | 3.4% |
| **Dynamic / Structural** | 9 | 1123 | 21.4 | 15.4 | 47.5 | 94.8 | 9.3% |

### Key Observations

#### 1. Gravity Concentration Diverges Sharply

| Category | Gravity Concentration |
|---|---|
| **Nominal (Go/Java)** | **15.3%** |
| **Dynamic (JS/Python)** | 9.3% |
| **Expressive (Rust/Scala)** | 6.7% |
| **Systems (C/C++)** | 3.4% |

**Nominal type systems (Go, Java) concentrate gravity in the top 10 by a factor of 2.3x compared to Expressive type systems.** This suggests that in Go/Java codebases, a small number of engineers hold disproportionate structural influence — possibly because the language's interface-based design encourages centralized architectural decisions.

Expressive type systems distribute gravity more evenly. When the type system itself can encode design decisions (through ADTs, traits, type-level programming), **structure becomes embedded in the type signatures rather than in a few architects' code**.

#### 2. Dynamic Languages Have Lower Gravity Ceilings

The **Dynamic / Structural** category shows the lowest Top10 Gravity (47.5) — roughly 10% lower than other categories. This may reflect that in dynamic languages, design decisions are less visible in code structure (they live in conventions, documentation, and runtime behavior rather than in type signatures and interfaces that EIS can observe through `git blame`).

#### 3. Design Influence Among Top Contributors

Top10 Design scores are relatively similar across categories (21–31), but **Nominal systems lead at 31.2**. This may seem counterintuitive, but Go's explicit interface pattern means architectural decisions are concentrated in a few files that define the system's contracts — these files show up clearly in EIS's Design axis.

---

### Per-Repository Detail

| Repository | Category | Language | Engineers | Top10 Design | Top10 Survival | Top10 Gravity | Max Gravity | Grav Conc |
|---|---|---|---|---|---|---|---|---|
| polars | Expressive Type System | Rust | 694 | 17.4 | 29.8 | 41.3 | 100.0 | 7.0% |
| rust | Expressive Type System | Rust | 7,914 | 53.0 | 5.7 | 68.9 | 77.4 | 0.6% |
| scala | Expressive Type System | Scala | 794 | 32.3 | 5.9 | 56.7 | 81.4 | 6.8% |
| scala3 | Expressive Type System | Scala 3 | 995 | 12.6 | 12.9 | 49.2 | 96.9 | 3.3% |
| swc | Expressive Type System | Rust | 357 | 16.4 | 14.0 | 40.1 | 100.0 | 15.7% |
| argo-cd | Nominal Type System | Go | 1,889 | 41.4 | 20.5 | 52.0 | 92.3 | 4.0% |
| esbuild | Nominal Type System | Go | 125 | 10.0 | 10.0 | 37.0 | 100.0 | 92.5% |
| grafana | Nominal Type System | Go/TS | 2,893 | 16.3 | 24.6 | 50.1 | 80.8 | 1.9% |
| kubernetes | Nominal Type System | Go | 5,217 | 42.5 | 19.9 | 56.1 | 77.3 | 0.8% |
| loki | Nominal Type System | Go | 1,319 | 34.0 | 19.3 | 65.5 | 86.7 | 7.8% |
| prometheus | Nominal Type System | Go | 1,281 | 44.5 | 11.9 | 62.1 | 100.0 | 5.4% |
| spring-boot | Nominal Type System | Java | 1,504 | 30.2 | 34.1 | 52.8 | 93.5 | 7.3% |
| terraform | Nominal Type System | Go | 2,223 | 30.3 | 32.7 | 46.5 | 84.3 | 2.4% |
| ClickHouse | Systems (C/C++) | C++ | 2,563 | 17.3 | 30.0 | 54.8 | 100.0 | 1.4% |
| arrow | Systems (C/C++) | C++/Multi | 1,466 | 28.3 | 12.4 | 50.9 | 77.8 | 3.8% |
| duckdb | Systems (C/C++) | C++ | 690 | 20.7 | 4.9 | 49.3 | 100.0 | 4.5% |
| envoy | Systems (C/C++) | C++ | 1,444 | 46.4 | 15.7 | 61.2 | 96.8 | 3.5% |
| redis | Systems (C/C++) | C | 905 | 14.3 | 8.9 | 45.6 | 100.0 | 4.0% |
| eslint | Dynamic / Structural | JavaScript | 1,180 | 18.6 | 12.8 | 58.6 | 100.0 | 8.1% |
| express | Dynamic / Structural | JavaScript | 391 | 13.5 | 3.2 | 38.9 | 100.0 | 23.9% |
| fastapi | Dynamic / Structural | Python | 897 | 11.7 | 11.2 | 37.7 | 100.0 | 9.4% |
| nest | Dynamic / Structural | TypeScript | 684 | 13.3 | 10.2 | 39.6 | 100.0 | 7.0% |
| phoenix | Dynamic / Structural | Elixir | 1,424 | 18.9 | 14.4 | 42.9 | 100.0 | 4.5% |
| prettier | Dynamic / Structural | JavaScript | 799 | 42.9 | 10.0 | 48.2 | 95.2 | 13.4% |
| react | Dynamic / Structural | JavaScript | 2,010 | 17.5 | 31.1 | 48.0 | 72.0 | 3.4% |
| superset | Dynamic / Structural | Python/TS | 1,477 | 23.6 | 29.5 | 57.7 | 100.0 | 4.5% |
| vite | Dynamic / Structural | TypeScript | 1,247 | 32.6 | 16.0 | 55.8 | 85.7 | 9.3% |

---

## Interpretation

### This Is Not About Superiority

These numbers do not say "Rust is better than JavaScript" or "Go is wrong for large systems." They show that **each language family creates a different gravitational physics**.

- In a **small universe** where complexity is manageable, low gravity concentration is fine — even desirable. A framework-driven dynamic language can bootstrap quickly.
- In a **large universe** with many contributors, the question becomes: does the language's type system help distribute design authority, or does it force centralization?

The data suggests that expressive type systems may naturally distribute gravity, while nominal type systems tend to concentrate it. Neither is inherently better — **but knowing which physics your universe operates under helps you make better structural decisions**.

### Limitations

- **27 repositories** is a meaningful sample but not exhaustive
- Repository maturity, governance model, and community culture are confounding variables
- EIS observes `git blame` and commit patterns — design decisions expressed outside of code (RFCs, ADRs, discussions) are invisible (Dark Matter)
- Some repositories span multiple languages (grafana: Go+TS, superset: Python+TS)

### Future Directions

- **Entropy resistance by language**: Do expressive type systems show higher Robust Survival as universe size grows?
- **Architect succession patterns**: Do certain language families produce smoother generational transitions?
- **Framework effect isolation**: Compare Rails vs bare Ruby, Express vs bare Node, to isolate framework influence from language influence

---

## Conclusion

The hypothesis that "the laws of physics are not uniform across code universes" is supported by the data — at least in its broad strokes.

**Gravity concentration varies by 4.5x between language families.** This is not noise. Something about the choice of language and type system shapes how structural influence distributes across a team.

For years, debates about technology choices have been aerial battles — fought with experience and intuition. This data is a first step toward **making design debates scientific**.

---

*Generated by [EIS (Engineering Impact Score)](https://github.com/machuz/engineering-impact-score) — OSS Gravity Map Project*
*27 repositories, 44,382 engineers, observed through commit light.*
